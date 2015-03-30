import pytest
from unittest import mock


class DummySSDPResponse(object):
    def __init__(self, ip_address):
        self.location = 'http://%s:80/description.xml' % ip_address


@pytest.fixture(scope='module')
def bridge_client():
    from bulby.client import HueBridgeClient
    client = HueBridgeClient(username='bulbydeveloper')
    client.validate_registration()
    return client


@pytest.mark.unit
def test_ssdp_parse_ip():
    from bulby.client import HueBridgeClient
    with mock.patch('bulby.client.discover') as discover:
        with mock.patch('bulby.client.HueBridgeClient.connect') as connect:
            discover.return_value = [DummySSDPResponse('192.168.1.1')]
            client = HueBridgeClient()

    assert client.ip_address == '192.168.1.1'
    assert client.port == 80
    assert client.base_url == 'http://192.168.1.1:80'


@pytest.mark.unit
def test_ssdp_raise_exception_multiple():
    from bulby.client import HueBridgeClient
    with mock.patch('bulby.client.discover') as discover:
        with mock.patch('bulby.client.HueBridgeClient.connect') as connect:
            ip_one = '192.168.1.1'
            ip_two = '192.168.1.2'

            discover.return_value = [
                DummySSDPResponse(ip_one),
                DummySSDPResponse(ip_two),
            ]

            with pytest.raises(Exception) as e:
                HueBridgeClient()

            msg = ' '.join([
                "Found more than one bridge ['http://%s:80/description.xml',",
                "'http://%s:80/description.xml']"
            ]) % (ip_one, ip_two)

            assert str(e.value) == msg


@pytest.mark.unit
def test_ssdp_no_bridges():
    from bulby.client import HueBridgeClient
    with mock.patch('bulby.client.discover') as discover:
        with mock.patch('bulby.client.HueBridgeClient.connect') as connect:

            discover.return_value = [
            ]

            with pytest.raises(Exception) as e:
                HueBridgeClient()

            assert str(e.value) == 'No bridges found'


@pytest.mark.unit
def test_client_static_ip_default_port():
    from bulby.client import HueBridgeClient

    with mock.patch('bulby.client.HueBridgeClient.connect') as connect:
        client = HueBridgeClient(ip_address='192.168.1.1')

    assert client.ip_address == '192.168.1.1'
    assert client.port == 80
    assert client.base_url == 'http://192.168.1.1:80'


@pytest.mark.unit
def test_client_static_ip_custom_port():
    from bulby.client import HueBridgeClient
    with mock.patch('bulby.client.HueBridgeClient.connect') as connect:
        client = HueBridgeClient(ip_address='192.168.1.1', port=1337)

    assert client.ip_address == '192.168.1.1'
    assert client.port == 1337


@pytest.mark.unit
def test_client_static_ip_custom_scheme():
    from bulby.client import HueBridgeClient

    with mock.patch('bulby.client.HueBridgeClient.connect') as connect:
        client = HueBridgeClient(ip_address='192.168.1.1',
                                 scheme='https', port=443)

    assert client.ip_address == '192.168.1.1'
    assert client.base_url == 'https://192.168.1.1:443'


@pytest.mark.functional
def test_speaking_with_bridge(bridge_client):
    assert bridge_client.ip_address is not None
    assert bridge_client.base_url is not None


@pytest.mark.functional
def test_register_with_bridge(bridge_client):
    assert bridge_client.connect() is True


@pytest.mark.functional
def test_list_lights(bridge_client):
    lights = bridge_client.get_lights()
    assert len(lights) > 0
    assert lights[0].state.reachable in [True, False]
    assert lights[0].state.on in [True, False]
    assert lights[0].name is not None


@pytest.mark.functional
def test_set_light_state(bridge_client):
    lights = bridge_client.get_lights()
    light = lights[0]
    result = bridge_client.set_state(light.light_id, hue=25500)
    assert result is True


@pytest.mark.functional
def test_set_color(bridge_client):
    lights = bridge_client.get_lights()
    light = lights[0]
    result = bridge_client.set_color(light.light_id, '000082')
    assert result is True


@pytest.mark.functional
def test_get_light_by_name(bridge_client):
    lights = bridge_client.get_lights()
    light = lights[0]
    light = bridge_client.get_light(light.name)

    assert light is not None

    result = bridge_client.set_color(light.name, 'ff0000')
    assert result is True
