import homeassistant.loader as loader

DOMAIN = 'hello_coap'

DEPENDENCIES = ['coap']

CONF_RESOURCE = 'resource'
DEFAULT_RESOURCE = 'home-assistant/hello_coap'

def setup(hass, config):
  coap = loader.get_component('coap')
  resource = config[DOMAIN].get('resource', DEFAULT_RESOURCE)
  entity_id = 'hello_coap.birth_of_coap'

  def birth_message(resource, payload, qos):
    hass.states.set(entity_id, 'hello_coap initialized successfully')
    hass.states.set(entity_id, payload)
  
  coap.listen(hass, resource, birth_message)

  return True