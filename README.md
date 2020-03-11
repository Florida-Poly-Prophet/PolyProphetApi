# PolyProphetApi

RESTful API for Florida Poly Prophet

## Overview

Source code is in the `prophet/` subdirectory.
- `models.py`: SQLAlchemy models describing the database tables
- `schemas.py`: Marshmallow schemas for converting JSON data into database model
  objects
- `resources/`: Resource endpoints for the API
- `auth.py`: Authentication-related helper functions
- `__init__.py`: Module entry point which sets up the application


## Development Environment

All that is needed for development is Python 3.6+ and `pip` (usually installed
by default with Python 3).

It is recommended to use a
[virtual environment](https://docs.python.org/3/tutorial/venv.html) to keep
libraries and dependencies for this project isolated from other projects and the
rest of the system. To set up the environment the first time:
```
# Create the environment
python3 -m venv venv

# Enter the environment
# On MacOS and Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

After initial setup, just perform the middle step to enter the environment in a
new terminal session.

See the link above for more info about virtual environments.

### Configuration

Several configuration parameters are required for authentication and the
database. For security purposes, these cannot be included in the GitHub repo, so
they have to be set by each person. All of the required values and some basic
descriptions are in the `template.env`, which should be copied to `.env` and
then filled. The values can be found in the Azure portal.

### Local Database

If using a local SQLite database, the `instance/` directory has to be created at
the root of the project. By default, the database file name will be
`instance/prophet.db`.

### Installing Dependencies

If any new libraries are installed, they should be added to the
`requirements.txt` file like so (once in the virtual environment):
```
pip freeze > requirements.txt
```


## Running

Once the environment has been set up, the server can be run with:
```
export FLASK_APP=prophet
export FLASK_ENV=development
# On Windows, use `set` instead of `export`
flask run
```

In development mode, Flask will be more verbose with errors, return JSON
pretty-printed, and automatically reload code files when they are modified.

To run in production mode, use the same command without setting `FLASK_ENV`.
Note: This shouldn't be used as Flask's server is not suitable for production.
When deployed, a WSGI server such as [`gunicorn`](https://gunicorn.org/) or a
serverless platform should be used instead.


## Links

### Library Documentation

- HTTP requests library: https://2.python-requests.org/en/master/
- Web server framework: https://flask.palletsprojects.com/en/1.1.x/
- Database driver and ORM: https://www.sqlalchemy.org/
- Flask database integration:
  https://flask-sqlalchemy.palletsprojects.com/en/2.x/
- Flask serializer integration:
  https://flask-marshmallow.readthedocs.io/en/latest/
- Serializer database integration:
  https://marshmallow-sqlalchemy.readthedocs.io/en/latest/
- Microsoft Authentication Library:
  https://msal-python.readthedocs.io/en/latest/

### Azure Active Directory Authentication

- JWT token viewer: https://jwt.ms
- https://docs.microsoft.com/en-us/azure/active-directory/develop/
- https://github.com/Azure-Samples/ms-identity-python-webapi-azurefunctions
- https://github.com/Azure-Samples/ms-identity-python-webapp
