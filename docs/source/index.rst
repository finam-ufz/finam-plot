.. :html_theme.sidebar_secondary.remove: true

==========
FINAM Plot
==========

Live plotting components for FINAM.

Quickstart
----------

Installation:

.. code-block:: bash

    pip install git+https://git.ufz.de/FINAM/finam-plot.git

Usage
-----

Most plot components in this package are push-based and have no internal time step.
In coupling setups where FINAM complains about dead links, it may be necessary to put a
:class:`finam.modules.TimeTrigger` component before the plot component in question.

API References
--------------

Information about the API of FINAM-plot.

.. toctree::
    :hidden:
    :maxdepth: 1

    self

.. toctree::
    :maxdepth: 1

    api/index

