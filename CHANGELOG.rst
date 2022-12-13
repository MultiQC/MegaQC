Changelog
=========

.. _section-1:

development
-----

.. _breaking-changes-1:

Breaking Changes
~~~~~~~~~~~~~~~~

-  `[#138]`_ Added ``USER_REGISTRATION_APPROVAL`` as a config variable,
   which defaults to true. This means that the admin must explicitly
   activate new users in the user management page
   (``/users/admin/users``) before they can login. To disable this
   feature, you need to create a config file (for example
   ``megaqc.conf.yaml``) with the contents:

   .. code:: yaml

      STRICT_REGISTRATION: false

   Then, whenever you run MegaQC, you need to ``export MEGAQC_CONFIG
   /path/to/megaqc.conf.yaml``

-  Much stricter REST API permissions. You now need an API token for
   almost all requests. One exception is creating a new account, which
   you can do without a token, but it will be deactivated by default,
   unless it is the first account created

-  Dropped support for Node 8

-  `[#440]`_ Set up poetry to manage the dependencies, which might keep 
   the dependencies from breaking down, and reduce the chances of the 
   happening of issues `[#430]`

.. _new-features-1:

New Features
~~~~~~~~~~~~

-  `[#140]`_ Added a changelog. It’s here! You’re reading it!
-  Sphinx based documentation on Github Pages
-  `[#69]`_ Added a check to verify that a database exists and exit nicely if not


.. _bug-fixes-1:

Bug Fixes
~~~~~~~~~

- `[#139]`_ Fixed the user management page (``/users/admin/users``), which lost its JavaScript
- `[#148]`_ Explicitly disable pagination for ``find()`` calls, ensuring we get more than 30 results in certain places
- `[#156]`_ Fixed comparison plot running into comparisons with None values
- `[#170]`_ Improved handling of environment variables with environs
- `[#194]`_ Forward more headers through nginx when using Docker Compose. This should avoid bad HTTP redirects.

.. _internal-changes-1:

Internal Changes
~~~~~~~~~~~~~~~~

-  Tests for the REST API permissions
-  Enforce inactive users (by default) in the model layer
-  Many and more dependency updates


.. _[#69]:  https://github.com/ewels/MegaQC/issues/69
.. _[#138]: https://github.com/ewels/MegaQC/issues/138
.. _[#139]: https://github.com/ewels/MegaQC/issues/139
.. _[#140]: https://github.com/ewels/MegaQC/issues/140
.. _[#148]: https://github.com/ewels/MegaQC/issues/148
.. _[#156]: https://github.com/ewels/MegaQC/issues/156
.. _[#170]: https://github.com/ewels/MegaQC/issues/170
.. _[#194]: https://github.com/ewels/MegaQC/issues/194
