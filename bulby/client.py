from bulby.ssdp import discover
from bulby.models import Light
from bulby.color import get_xy_from_hex
from collections.abc import Mapping
from urllib.parse import urlparse
import requests
import json


class HueBridgeClient(object):
    def __init__(self, ip_address=None, port=80, scheme='http',
                 device_type='bulby', username='bulbyapp'):
        '''
        Connects to a Hue Bridge, if an ip address isn't defined it
        will use ssdp to discover the bridge on the network. If there
        are more than one bridge it will raise an Exception.
        '''
        if ip_address is None:
            results = discover('IpBridge')
            locations = [x.location for x in results]

            if len(locations) > 1:
                raise Exception('Found more than one bridge %r' % locations)
            elif len(locations) == 0:
                raise Exception('No bridges found')
            else:
                parsed_location = urlparse(locations[0])
                self.ip_address = parsed_location.hostname
                self.port = int(parsed_location.port)
                self.base_url = '%s://%s' % (
                    parsed_location.scheme,
                    parsed_location.netloc
                )
        else:
            self.ip_address = ip_address
            self.port = port
            self.base_url = '%s://%s:%s' % (
                scheme, ip_address, port
            )

        self.device_type = device_type
        self.username = username
        self._lights = None
        self.connect()

    def make_request(self, method, url, body=None):
        url = '%s%s' % (self.base_url, url)
        fn = getattr(requests, method.lower())

        if method != 'get' and body is not None:
            response = fn(url, data=json.dumps(body))
        else:
            response = fn(url)

        data = response.json()
        # Errors are returned as lists instead of dictionaries
        if not isinstance(data, Mapping):
            return data[0]
        return data

    def validate_registration(self):
        '''
        Checks if the device + username have already been registered with the
        bridge.
        '''
        url = '/api/%s' % self.username
        response = self.make_request('GET', url)

        if 'error' in response:
            return False

        return True

    def connect(self):
        '''
        Registers a new device + username with the bridge
        '''
        # Don't try to register if we already have
        if self.validate_registration():
            return True

        body = {
            'devicetype': self.device_type,
            'username': self.username,
        }
        response = self.make_request('POST', '/api', body)

        if 'error' in response:
            if response['error']['type'] == 101:
                msg = 'Please press the link button and try again'
            else:
                msg = response['error']['description']

            raise Exception(msg)

    def get_lights(self):
        '''
        Lists all available lights on the bridge.
        '''
        url = '/api/%s/lights' % self.username
        response = self.make_request('GET', url)
        lights = []
        # Did we get a success response back?
        # error responses look like:
        # [{'error': {'address': '/lights',
        #    'description': 'unauthorized user',
        #    'type': 1}}]

        if 'error' in response:
            raise Exception(response['error']['description'])

        for id_, data in response.items():
            lights.append(Light(
                id_,
                data['modelid'],
                data['name'],
                data['state'],
                data['swversion'],
                data['type'],
                data['uniqueid']
            ))

        lights = sorted(lights, key=lambda x: x.light_id)
        self._lights = lights
        return lights

    def get_light(self, key):
        if self._lights is None:
            lights = self.get_lights()
        else:
            lights = self._lights

        if isinstance(key, str):
            for light in lights:
                if light.name == key:
                    return light
        else:
            for light in lights:
                if light.light_id == key:
                    return light

        raise Exception('Did not find light %s' % key)

    def set_state(self, light_id, **kwargs):
        '''
        Sets state on the light, can be used like this:

        .. code-block:: python

            set_state(1, xy=[1,2])
        '''
        light = self.get_light(light_id)
        url = '/api/%s/lights/%s/state' % (self.username, light.light_id)
        response = self.make_request('PUT', url, kwargs)
        setting_count = len(kwargs.items())
        success_count = 0

        for data in response:
            if 'success' in data:
                success_count += 1

        if success_count == setting_count:
            return True
        else:
            return False

    def set_color(self, light_id, hex_value, brightness=None):
        '''
        This will set the light color based on a hex value
        '''
        light = self.get_light(light_id)

        xy = get_xy_from_hex(hex_value)
        data = {
            'xy': [xy.x, xy.y],
        }

        if brightness is not None:
            data['bri'] = brightness

        return self.set_state(light.light_id, **data)
