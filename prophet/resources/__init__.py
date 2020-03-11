from http import HTTPStatus

from marshmallow import ValidationError

from prophet import app

# Import these so that the app routes are loaded
import prophet.resources.question
import prophet.resources.user


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    # TODO Change error format to allow for multiple errors and show full
    # information
    return {
        'error': {
            'code': 'invalid_field',
            'description': f'Invalid value for `{e.field_name}`',
        }
    }, HTTPStatus.BAD_REQUEST
