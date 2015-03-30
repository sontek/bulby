class LightState(object):
    def __init__(self, state_data):
        self._data = state_data
        self.xy = state_data['xy']
        self.on = state_data['on']
        self.sat = state_data['sat']
        self.hue = state_data['hue']
        self.bri = state_data['bri']
        self.colormode = state_data['colormode']
        self.reachable = state_data['reachable']


class Light(object):
    def __init__(self, light_id, model, name, state, software_version, light_type,
                 mac_address):
        self.light_id = int(light_id)
        self.model = model
        self.name = name
        self.state = LightState(state)
        self.software_version = software_version
        self.light_type = light_type
        self.mac_address = mac_address
