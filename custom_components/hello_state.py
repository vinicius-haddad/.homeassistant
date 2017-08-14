DOMAIN = 'hello_state'

def setup(hass, config):
  hass.states.set('hello.world', 'Fenicio')
  
  return True