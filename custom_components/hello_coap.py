import homeassistant.loader as loader
from homeassistant.core import callback

DOMAIN = 'hello_coap'

DEPENDENCIES = ['coap']

DEFAULT_TIME_INTERVAL = 1

def setup(hass, config):
  coap = loader.get_component('coap')
  resource = config[DOMAIN].get('resource')
  # resource = Resource(resource_conf.get('path'), resource_conf.get('time_interval'), resource_conf.get('qos'))
  entity_id = '{}.{}'.format(DOMAIN, resource.get('path').replace('/', '.'))

  def print_payload(path, payload):
    print("From within hello_coap! %s" % entity_id)
    print("coap response: path: %s\n%s" % (path, payload))
    hass.states.set(entity_id, payload)

  coap.listen(hass, resource, print_payload)

  return True
