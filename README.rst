bulby
=================
Python library for managing the phillips hue lightbulb

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
