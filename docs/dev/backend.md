# Python Backend
The Python backend is written in [flask](https://www.palletsprojects.com/p/flask/), which
determines the structure of the project.

## Database
MegaQC uses [SQLAlchemy](https://docs.sqlalchemy.org/) to handle database access, which
means it can integrate with any SQL database that it supports. For development this will
likely be SQLite.

Database models are located in [`model/models.py`](/megaqc/model/models.py) and
[`user/models.py`](/megaqc/user/models.py).

## API
MegaQC actually has two APIs. The first, older API is accessed at `/api`, and the code
for this API is located in [`megaqc/api`](/megaqc/api).
This API is implemented using regular flask views.

However, all future development should be done on the newer REST API.
This is accessed at `/rest_api/v1`, and the code for it is located in
[`megaqc/rest_api`](/megaqc/rest_api).
This API is composed of views, located in [`views.py`](megaqc/rest_api/views.py). These view classes, 
which rely on [flapison](https://github.com/TMiguelT/flapison), each define an SQLAlchemy
model that defines how to access the data, and a Marshmallow schema, which defines how
to serialize and deserialize the data to JSON. The Marshmallow schemas themselves are
defined in [`schemas.py`](/megaqc/rest_api/schemas.py). For more information, refer to the 
flapison documentation.

## Views
Flask endpoints that return HTML (the non-API URLs) are defined in [`public/views.py`](/megaqc/public/views.py),
and [`user/views.py`](/megaqc/user/views.py). All of these render a
[Jinja2](https://jinja.palletsprojects.com/en/2.11.x/) template, which all the other
frontend CSS and JavaScript is connected to. This is further explained in the
[frontend](./frontend.md) docs.

## Tests
Python tests are located in [`tests`](/tests) (note: there aren't currently any JavaScript tests).
To run them, use `pytest test`. Each new URL should be tested, although
since new pages will likely rely only on React and the REST API, testing can mostly
be done inside [`test_api.py`](/tests/api/test_api.py), which tests all REST API endpoints.

