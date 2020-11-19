Backend
=======

The Python backend is written in `flask`_, which determines the
structure of the project.

Database
--------

MegaQC uses `SQLAlchemy`_ to handle database access, which means it can
integrate with any SQL database that it supports. For development this
will likely be SQLite.

Database models are located in ```model/models.py``` and ```user/models.py```.

API
---

MegaQC actually has two APIs. The first, older API is accessed at
```/api```, and the code for this API is located in ```megaqc/api```.
This API is implemented using regular flask views.

However, all future development should be done on the newer REST API.
This is accessed at ``/rest_api/v1``, and the code for it is located in
```megaqc/rest_api```. This API is composed of views, located in
```views.py```. These view classes, which rely on `flapison`_, each
define an SQLAlchemy model that defines how to access the data, and a
Marshmallow schema, which defines how to serialize and deserialize the
data to JSON. The Marshmallow schemas themselves are defined in
```schemas.py```. For more information, refer to the flapison
documentation.

Views
-----

Flask endpoints that return HTML (the non-API URLs) are defined in
```public/views.py```, and ```user/views.py```. All of these render a
`Jinja2`_ template, which all the other frontend CSS and JavaScript is
connected to. This is further explained in the `frontend`_ docs.

Tests
-----

Python tests are located in ```tests``` (note: there aren’t currently
any JavaScript tests). To run them, use ``pytest test``. Each new URL
should be tested, although since new pages will likely rely only on
React and the REST API, testing can mostly be done inside
```test_api.py```_, which tests all REST API endpoints.

.. _flask: https://www.palletsprojects.com/p/flask/
.. _SQLAlchemy: https://docs.sqlalchemy.org/
.. _``model/models.py``: https://github.com/ewels/MegaQC/blob/master/megaqc/model/models.py
.. _``user/models.py``: https://github.com/ewels/MegaQC/blob/master/megaqc/user/models.py
.. _``megaqc/api``: https://github.com/ewels/MegaQC/tree/master/megaqc/api
.. _``megaqc/rest_api``: https://github.com/ewels/MegaQC/tree/master/megaqc/rest_api
.. _``views.py``: https://github.com/ewels/MegaQC/blob/master/megaqc/rest_api/views.py
.. _flapison: https://github.com/TMiguelT/flapison
.. _``schemas.py``: https://github.com/ewels/MegaQC/tree/master/megaqc/rest_api/schemas.py
.. _``public/views.py``: https://github.com/ewels/MegaQC/tree/master/megaqc/public/view.py
.. _``user/views.py``: https://github.com/ewels/MegaQC/tree/master/megaqc/user/views.py
.. _Jinja2: https://jinja.palletsprojects.com/en/2.11.x/
.. _frontend: ./frontend.md
.. _``tests``: https://github.com/ewels/MegaQC/tree/master/tests
.. _``test_api.py``: https://github.com/ewels/MegaQC/tree/master/megaqc/api/test_api.py