:html_theme.sidebar_secondary.remove: true

==========
FINAM Plot
==========

Live plotting components for the `FINAM <https://finam.pages.ufz.de/>`_ model coupling framework.

Uses :mod:`matplotlib` for all plotting functionality.

Quickstart
----------

Installation:

.. code-block:: bash

    pip install finam-plot

For available components, see the :doc:`api/index`.

Usage
-----

See the `example scripts <https://git.ufz.de/FINAM/finam-plot/-/tree/main/examples>`_
in the GitLab repository for fully functional usage examples.

Most plot components in this package are push-based and have no internal time step.
In coupling setups where FINAM complains about dead links, it may be necessary to put a
:class:`finam.components.TimeTrigger` component before the plot component in question.

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

About
-----

Further information about licensing, the developers team and the changelog of FINAM-Plot.

.. toctree::
  :maxdepth: 2

  about/index


License
^^^^^^^

LGPLv3, Copyright © 2021-2023, the FINAM developers from Helmholtz-Zentrum für Umweltforschung GmbH - UFZ. All rights reserved.
