from coapthon.client.helperclient import HelperClient

import asyncio
import logging
import os
import socket
import time
import ssl
import re
import requests.certs

import voluptuous as vol

from homeassistant.core import callback
from homeassistant.setup import async_prepare_setup_platform
from homeassistant.config import load_yaml_config_file
from homeassistant.exceptions import HomeAssistantError
from homeassistant.loader import bind_hass
from homeassistant.helpers import template, config_validation as cv
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect, dispatcher_send)
from homeassistant.util.async import (
    run_coroutine_threadsafe, run_callback_threadsafe)
from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP, CONF_VALUE_TEMPLATE, CONF_USERNAME,
    CONF_PASSWORD, CONF_PORT, CONF_PROTOCOL, CONF_PAYLOAD)
from homeassistant.components.mqtt.server import HBMQTT_CONFIG_SCHEMA

REQUIREMENTS = ['CoAPthon']
DOMAIN = 'coap'

@bind_hass
def publish(hass, topic, payload, qos=None, retain=None):

@callback
@bind_hass
def async_publish(hass, topic, payload, qos=None, retain=None):

@bind_hass
def publish_template(hass, topic, payload_template, qos=None, retain=None):

@asyncio.coroutine
@bind_hass
def async_subscribe(hass, topic, msg_callback, qos=DEFAULT_QOS,
                    encoding='utf-8'):

    @callback
    def async_mqtt_topic_subscriber(dp_topic, dp_payload, dp_qos):

@bind_hass
def subscribe(hass, topic, msg_callback, qos=DEFAULT_QOS,
              encoding='utf-8'):

@asyncio.coroutine
def _async_setup_server(hass, config):

@asyncio.coroutine
def _async_setup_discovery(hass, config):

@asyncio.coroutine
def async_setup(hass, config):
    
    @asyncio.coroutine
    def async_stop_mqtt(event):
    
    @asyncio.coroutine
    def async_publish_service(call):
    
    @asyncio.coroutine
    def async_publish(self, topic, payload, qos, retain):
    
    @asyncio.coroutine
    def async_connect(self):
    
    @asyncio.coroutine
    def async_subscribe(self, topic, qos):
    
    @asyncio.coroutine
    def async_unsubscribe(self, topic):

class CoAP
  def __init__(self, host, port):
    return True


