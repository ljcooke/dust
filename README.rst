dust.py
=======

Dust cloud generator for `@dust_exe`_, a Twitter bot.

Originally a proof of concept was made with `Cheap Bots Done Quick`_, then
rewritten in Python. The original `Tracery JSON source`_ is available.

Requirements
------------

Python 3 is required. Install the Python requirements using Pip:

.. code:: bash

    pip3 install -r requirements.txt

librsvg_ is used to render the SVG to PNG, and Imagemagick_ is used to then
convert the PNG to JPG.

On OS X, these may be installed using Homebrew:

.. code:: bash

    brew install librsvg imagemagick

Example
-------

.. image:: sample.jpg


.. _@dust_exe: https://twitter.com/dust_exe
.. _Cheap Bots Done Quick: http://cheapbotsdonequick.com/
.. _Tracery JSON source: http://cheapbotsdonequick.com/source/dust_exe
.. _librsvg: https://wiki.gnome.org/Projects/LibRsvg
.. _ImageMagick: http://imagemagick.org/script/index.php
.. _Homebrew: http://brew.sh
