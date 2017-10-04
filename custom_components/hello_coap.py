import homeassistant.loader as loader

import pdb

DOMAIN = 'hello_coap'

DEPENDENCIES = ['coap']

def setup(hass, config):
  coap = loader.get_component('coap')
  resource = config[DOMAIN].get('resource')
  entity_id = resource['path'].replace("/", ".")

  # pdb.set_trace()

  def print_payload(resource, payload):
    print("Message received! %s" % entity_id)
    hass.states.set(entity_id, payload)

  pdb.set_trace()

  coap.listen_resource(hass, resource, print_payload)

  return True