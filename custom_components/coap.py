from coapthon.client.helperclient import HelperClient
from coapthon import defines
from coapthon.messages.message import Message
from coapthon.messages.option import Option
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon.serializer import Serializer

import asyncio
import logging
import os
import socket
import time
import ssl
import re
import requests.certs

import pdb
import voluptuous as vol

from homeassistant.core import callback
from homeassistant.setup import async_prepare_setup_platform
from homeassistant.config import load_yaml_config_file
from homeassistant.exceptions import HomeAssistantError
from homeassistant.loader import bind_hass
from homeassistant.helpers import template, config_validation as cv
from homeassistant.helpers.event import track_time_interval
from homeassistant.helpers.dispatcher import (
	 async_dispatcher_connect, dispatcher_send)
from homeassistant.util.async import (
    run_coroutine_threadsafe, run_callback_threadsafe)
from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP, CONF_VALUE_TEMPLATE, CONF_USERNAME,
    CONF_PASSWORD, CONF_PORT, CONF_PROTOCOL, CONF_PAYLOAD)

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['CoAPthon==4.0.1']
DOMAIN = 'coap'

DATA_COAP = 'coap'

SIGNAL_COAP_MESSAGE_RECEIVED = 'coap_message_received'

CONF_HOST = 'host'
CONF_DISCOVERY = 'discovery'
CONF_RESOURCES = 'resources'
CONF_DISCOVERY_PREFIX = 'discovery_prefix'
CONF_BIRTH_MESSAGE = 'birth_message'
CONF_WILL_MESSAGE = 'will_message'

CONF_PATH = 'path'
CONF_TIME_INTERVAL = 'time_interval'
CONF_QOS = 'qos'

PROTOCOL_31 = '3.1'
PROTOCOL_311 = '3.1.1'

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8765
DEFAULT_TIME_INTERVAL = 1
DEFAULT_QOS = 0
DEFAULT_DISCOVERY = False
DEFAULT_DISCOVERY_PREFIX = 'homeassistant'
DEFAULT_TLS_PROTOCOL = 'auto'

ATTR_RESOURCE = 'resource'
ATTR_PAYLOAD = 'payload'
ATTR_PAYLOAD_TEMPLATE = 'payload_template'
ATTR_QOS = CONF_QOS

MAX_RECONNECT_WAIT = 300  # seconds

def valid_resource_name(value, invalid_chars='\0'):
    """Validate that we can subscribe using this MQTT topic."""
    value = cv.string(value)
    if all(c not in value for c in invalid_chars):
        return vol.Length(min=1, max=65535)(value)
    raise vol.Invalid('Invalid CoAP resource name')

def valid_discovery_resource(value):
    """Validate a discovery topic."""
    return valid_subscribe_topic(value, invalid_chars='#+\0/')

_VALID_QOS_SCHEMA = vol.All(vol.Coerce(int), vol.In([0, 1, 2]))

_COAP_WILL_BIRTH_SCHEMA = vol.Schema({
	vol.Required(ATTR_RESOURCE): valid_resource_name,
	vol.Required(ATTR_PAYLOAD, CONF_PAYLOAD): cv.string,
	vol.Optional(ATTR_QOS, default=DEFAULT_QOS): _VALID_QOS_SCHEMA,
}, required=True)

_COAP_RESOURCES_SCHEMA = vol.Schema([{
	vol.Required(CONF_PATH): valid_resource_name,
	vol.Optional(CONF_TIME_INTERVAL, default= DEFAULT_TIME_INTERVAL): cv.string,
	vol.Optional(CONF_QOS, default= DEFAULT_QOS): _VALID_QOS_SCHEMA
}])

CONFIG_SCHEMA = vol.Schema({
	DOMAIN: vol.Schema({
		vol.Optional(CONF_RESOURCES): _COAP_RESOURCES_SCHEMA,
		vol.Optional(CONF_HOST, default= DEFAULT_HOST): cv.string,
		vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
		vol.Optional(CONF_WILL_MESSAGE): _COAP_WILL_BIRTH_SCHEMA,
		vol.Optional(CONF_BIRTH_MESSAGE): _COAP_WILL_BIRTH_SCHEMA,
		vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
		vol.Optional(CONF_DISCOVERY_PREFIX, default=DEFAULT_DISCOVERY_PREFIX): valid_discovery_resource,
	}),
}, extra=vol.ALLOW_EXTRA)

@asyncio.coroutine
@bind_hass
def async_listen(hass, resource, msg_callback):
	""" listen an resource """
	@callback
	def listen_callback(resource, payload):
		hass.async_run_job(msg_callback, resource, payload)

	async_remove = async_dispatcher_connect(hass, SIGNAL_COAP_MESSAGE_RECEIVED, listen_callback)

	yield from hass.data[DATA_COAP].async_listen(resource)
	return async_remove

@bind_hass
def listen(hass, resource, callback= None):
	async_remove = run_coroutine_threadsafe(async_listen(hass, resource, callback), hass.loop).result()

	def remove():
		run_callback_threadsafe(hass.loop, async_remove).result()

	return remove

@asyncio.coroutine
def _async_discovery(hass, config):
	yield from hass.data[DATA_COAP].discover()
	_LOGGER("Discovering resources on %s:%s" % (conf.get(CONF_HOST), conf.get(CONF_PORT)))


@asyncio.coroutine
def async_setup(hass, config):

	conf= config.get(DOMAIN)

	if conf is None:
		conf = CONFIG_SCHEMA({DOMAIN: {}})[DOMAIN]

	host= conf.get(CONF_HOST)
	port= conf.get(CONF_PORT)
	will_message= conf.get(CONF_WILL_MESSAGE)
	birth_message= conf.get(CONF_BIRTH_MESSAGE)
	discovery_prefix= conf.get(CONF_DISCOVERY_PREFIX)
	
	try:
		hass.data[DATA_COAP]= CoAP(hass, host, port, will_message, birth_message, discovery_prefix)
	except socket.gaierror:
		_LOGGER.exception("Cannot initialize CoAP client. Checkout your configs")
		return False
	
	@asyncio.coroutine
	def async_stop_coap(event):
		yield from hass.data[DATA_COAP].stop()

	hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_stop_coap)

	if conf.get(CONF_DISCOVERY):
		yield from _async_discovery(hass, config)

	return True

class CoAP(object):
	def __init__(self, hass, host, port, will_message, birth_message, discovery_prefix):
		print("GO coap\n")
		self.client= HelperClient(server=(host, port))
		self.hass= hass
		self.will_message= will_message
		self.birth_message= birth_message
		self.discovery_prefix= discovery_prefix
		self.resources= []
	  
	@asyncio.coroutine
	def get(self, resource, time_interval, qos):
		print("GET coap\n")
		if resource not in self.resources:
			_LOGGER("COAP warning: Trying to get an resource not listenned: %s" % resource.get('path'))
			return

		def client_callback(self, msg):
			dispatcher_send(self.hass, SIGNAL_COAP_MESSAGE_RECEIVED, msg.get('resource'), msg.get('payload'))

		self.client.get(resource, client_callback)

	@asyncio.coroutine
	def discover(self, callback= None, timeout= None):
		if callback is not None:
			self.client.discover(callback, timeout)
		else:
			def set_resources_from_discover(resources):
				for res in resources:
					if res not in self.resources:
						self.async_listen(res)
			self.client.discover(set_resources_from_discover)

		self.resources= list(set(self.resources).union(resources))

	@asyncio.coroutine
	def stop(self):
		self.client.stop()

	@asyncio.coroutine
	def async_listen(self, resource):
		print("async_listen to coap resource\n")
		if resource is None or resource in self.resources:
			_LOGGER("COAP warning: Trying to listen an resource already set: %s" % resource.get('path'))
			return

		self.resources.append(resource)
		path = resource.get('path')
		time_interval = resource.get('time_interval', DEFAULT_TIME_INTERVAL)
		qos = resource.get('qos', DEFAULT_QOS)
		# pdb.set_trace()
		while(True):
			self.get(path, qos)
			time.sleep(time_interval)
		# track_time_interval(self.hass, self.hass.data[DATA_COAP].get(path, qos), time_interval)
