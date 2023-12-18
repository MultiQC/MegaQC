Frontend
========

As with the API, MegaQC is currently transitioning from using an HTML +
CSS + JavaScript frontend to `React`_. This can be confusing, as a
number of technologies are mixed in the same project.

As explained in the backends section, each URL in MegaQC renders a
Jinja2 template. The old-style endpoints have a lot of HTML code in
their `templates`_ that defines the entire page layout, and load
JavaScript and CSS located in the `static`_ directory.

However, the newer React pages instead render a special template, called
`react.html`_, which is a very simple page that acts as the entry
point for the React code, which handles all layout and logic.

The source code for the React JavaScript can be found in the `src`_
directory, which currently has one root-level ``.js`` file for each
React page that then imports other components to use.

Note that all new pages going forward should be written using React, to
improve the maintainability of the frontend.

.. _React: https://reactjs.org/
.. _templates: https://github.com/MultiQC/MegaQC/tree/master/megaqc/templates
.. _static: https://github.com/MultiQC/MegaQC/tree/master/megaqc/static
.. _react.html: https://github.com/MultiQC/MegaQC/tree/master/megaqc/templates/public/react.html
.. _src: https://github.com/MultiQC/MegaQC/tree/master/src
