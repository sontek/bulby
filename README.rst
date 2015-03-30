bulby
=================
Python library for managing the phillips hue lightbulb

Getting Started
=================
To get started you just need to do the following:

.. code-block:: python

    from bulby.client import HueBridgeClient
    client = HueBridgeClient()
    light = client.get_lights()[0]
    client.set_state(light.light_id, hue=25500)

and now your light should be green!


Development
================
API Documentation for the Phillips Hue is here:

http://www.developers.meethue.com/

You can test the API of your phillips hue by going to ``/debug/clip.html``.

Running tests
=================
To run the tests you can do the following:

.. code-block:: bash

    tox -e py34

The first time you run the tests you will need to hold the link button.

Credits
==================
- SSDP Module originally developed by Dan Krause here:
  https://gist.github.com/dankrause/6000248

- Hex -> XY originally developed by Ben Knight here:
  https://github.com/benknight/hue-python-rgb-converter
