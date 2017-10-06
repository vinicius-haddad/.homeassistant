import homeassistant.loader as loader

import pdb

DOMAIN = 'hello_coap'

DEPENDENCIES = ['coap']

def setup(hass, config):
  coap = loader.get_component('coap')
  resource = config[DOMAIN].get('resource')
  entity_id = resource['path'].replace("/", ".")

  def print_payload(oqueqtemaquinessecallback):
    print("Message received! %s" % entity_id)
    print("callback:\n\n%s\n\n" % oqueqtemaquinessecallback)
    hass.states.set(entity_id, oqueqtemaquinessecallback)

  # pdb.set_trace()
  # print("VAIIIIIIII\n\nVEEEEEEEEEEI\n")
  coap.listen(hass, resource, print_payload)

  return True