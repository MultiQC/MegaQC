Changelog
=========

Development
----------

Added
~~~~~

- `[#443]`_: Added support and testing for Python 3.11
- `[#479]`_: A "Filters" resource to the admin interface, allowing users to view, edit and delete filters there. This resolves `[#476]`_.
- `[#433]`_: "Statistic" selector that allows the selection of "measurement" or "isolation forest". The isolation forest statistic plots the multivariate outlier score in a non-parametric way, with an adjustable threshold
- `[#479]`_: Give all users access to the admin interface. Unprivileged users won't be able to edit or delete most entities, however
- `[#479]`_: Consistently added show, edit and delete buttons to all pages of the admin interface

Changed
~~~~~~~

- `[#479]`_: Allow unprivileged users to create new filters and delete their own filters via the REST API. This also resolves issues where these users couldn't create their own filters on certain pages.
- `[#479]`_: The "Edit Filters" page now redirects to the Filters tab of the Data Admin page. This relates to `[#476]`_.
- `[#440]`_ Set up poetry to manage the dependencies, which might keep the dependencies from breaking down, and reduce the chances of the happening of issues such as `[#430]`_

Fixed
~~~~~

- `[#443]`_: Fix a bug in the database script when constructing URLs that broken under new SQLAlchemy versions

Removed
~~~~~~~

- `[#433]`_ Removed outlier detection from normal measurement plot, because the normal assumption is not reasonable
- `[#443]`_: Dropped support for Python 3.6

0.3.0
-----

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

New Features
~~~~~~~~~~~~

-  `[#140]`_ Added a changelog. It’s here! You’re reading it!
-  Sphinx based documentation on Github Pages
-  `[#69]`_ Added a check to verify that a database exists and exit nicely if not

Bug Fixes
~~~~~~~~~

- `[#139]`_ Fixed the user management page (``/users/admin/users``), which lost its JavaScript
- `[#148]`_ Explicitly disable pagination for ``find()`` calls, ensuring we get more than 30 results in certain places
- `[#156]`_ Fixed comparison plot running into comparisons with None values
- `[#170]`_ Improved handling of environment variables with environs
- `[#194]`_ Forward more headers through nginx when using Docker Compose. This should avoid bad HTTP redirects.

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
.. _[#430]: https://github.com/ewels/MegaQC/issues/430
.. _[#433]: https://github.com/ewels/MegaQC/pull/433
.. _[#440]: https://github.com/ewels/MegaQC/pull/440
.. _[#443]: https://github.com/ewels/MegaQC/pull/443
.. _[#476]: https://github.com/ewels/MegaQC/issues/476
.. _[#479]: https://github.com/ewels/MegaQC/issues/479