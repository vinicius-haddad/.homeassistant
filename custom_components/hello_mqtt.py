import homeassistant.loader as loader

DOMAIN = 'hello_mqtt'

DEPENDENCIES = ['mqtt']

CONF_TOPIC = 'topic'
DEFAULT_TOPIC = 'home-assistant/hello_mqtt'

def setup(hass, config):
  mqtt = loader.get_component('mqtt')
  topic = config[DOMAIN].get('topic', DEFAULT_TOPIC)
  entity_id = 'hello_mqtt.last_message'

  def message_received(topic, payload, qos):
    hass.states.set(entity_id, payload)
  
  mqtt.subscribe(hass, topic, message_received)

  hass.states.set(entity_id, 'hello_mqtt initialized successfully')

  def set_state_service(call):
    mqtt.publish(hass, topic, call.data.get('new_state'))

  hass.services.register(DOMAIN, 'set_state', set_state_service)

  return True