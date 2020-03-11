import os
from http import HTTPStatus

import msal

from flask import Flask
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from werkzeug.exceptions import HTTPException, NotFound

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = \
    os.environ.get('DATABASE_URI').format(instance_path=app.instance_path)

db = SQLAlchemy(app)
ma = Marshmallow(app)

cross_origin_auth = cross_origin(headers=('Content-Type', 'Authorization'))


def class_route(rule, name=None, *class_args, **class_kwargs):
    """Decorator to add a flask route for a View class
    """
    def decorator(cls):
        # For some reason, this complains about `name` not being defined,
        # but the below works fine
        # TODO Figure out what's wrong
        #
        # if name is None:
        #     name = cls.__name__.lower()
        # app.add_url_rule(
        #     rule, view_func=cls.as_view(name, *class_args, **class_kwargs))

        app.add_url_rule(
            rule,
            view_func=cls.as_view(
                name if name else cls.__name__.lower(),
                *class_args,
                **class_kwargs))
        return cls

    return decorator

# These have to be imported after `app`, `db`, etc. are defined so that
# the circular imports resolve properly (this is the reccommended way to
# organize the project according to the Flask documentation)

from prophet.auth import requires_auth
from prophet.models import User, Question, Response
import prophet.resources

# TODO Only run this in debug mode / when using a local database?
db.create_all()


# Set up generic error handlers

@app.errorhandler(NotFound)
def handle_not_found(e):
    return {
        'error': {
            'code': 'resource_not_found',
            'description': e.description,
        },
    }, HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Handler for un-recognized errors.
    """
    return {
        'error': {
            'code': 'unknown',
            'description': e.description,
        },
    }, HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/teapot')
@cross_origin_auth
@requires_auth
def im_a_teapot():
    """Protected endpoint for testing authentication.
    """
    # 418 is the (semi-)official I'M A TEAPOT status code as specified in
    # RFC 2324
    return {'data': "I'm a teapot"}, 418
