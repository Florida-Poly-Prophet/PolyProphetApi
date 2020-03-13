from http import HTTPStatus

from flask import g, request, url_for
from flask.views import MethodView

from prophet import app, class_route, db
from prophet.auth import msal_app, requires_auth
from prophet.models import Question, Response, Response
from prophet.resources import (
    question as question_resourse,
    user as user_resourse,
)
from prophet.schemas import ResponseSchema, responses_schema, response_schema


class ResponseNotFound(Exception):
    def __init__(self, user_id, question_id):
        self.user_id = user_id
        self.question_id = question_id


@app.errorhandler(ResponseNotFound)
def handle_response_not_found(e):
    return {
        'error': {
            'code': 'response_not_found',
            'description':
                f"User `{e.user_id}` has not responsed to "
                f"question `{e.question_id}`",
        },
    }, HTTPStatus.NOT_FOUND


def query_response(user_id, question_id):
    response = Response.query.get((user_id, question_id))
    if response is None:
        raise ResponseNotFound(user_id, question_id)
    return response


def response_with_links(response):
    return {
        'data': response_schema.dump(response),
        'links': {
            'self': url_for(
                'response_detail',
                user_id=response.user_id,
                question_id=response.question_id,
                _external=True),
            'user': url_for('user_detail', id=response.user_id, _external=True),
            'question': url_for(
                'question_detail',
                id=response.question_id,
                _external=True),
        },
    }


@class_route('/users/<user_id>/responses/<question_id>', 'response_detail')
# Secondary URL for the resourse (TODO remove this?)
@class_route(
    '/questions/<question_id>/responses/<user_id>', 'question_response_detail')
class ResponseDetail(MethodView):
    def get(self, user_id, question_id):
        response = query_response(user_id, question_id)
        return response_with_links(response)

    def put(self, user_id, question_id):
        response = Response.query.get((user_id, question_id))
        if response is None:
            # Extract the real ID in case of "me"
            user = user_resourse.query_user(user_id)
            user_id = user.id

            # Make sure the question exists
            question_resourse.query_question(question_id)

            # TODO Validate incoming request data
            # Create a new one for this question
            data = request.get_json()
            response = response_schema.load({
                'user_id': user_id,
                'question_id': question_id,
                'response': data['response'],
                # This is optional
                'view_time': data.get('view_time'),
            }, session=db.session)
        else:
            # Update the existing one
            # TODO Disallow changing the IDs
            response = response_schema.load(
                request.get_json(), instance=response, partial=True)

        db.session.add(response)
        db.session.commit()
        return response_with_links(response)


@class_route('/users/<user_id>/responses', 'user_responses')
class UserResponses(MethodView):
    def get(self, user_id):
        # Get the user to check that the user ID is valid and to resolve
        # references to "me" (but don't create users just to look at an empty
        # list of responses).
        user = user_resourse.query_user(user_id)
        # Extract the real ID instead of "me"
        id = user.id
        responses = Response.query.filter_by(user_id=id).all()

        return {
            'data': responses_schema.dump(responses),
            'links': {
                'self': url_for('user_responses', user_id=id, _external=True),
                'user': url_for('user_detail', id=id, _external=True),
            },
        }


@class_route('/questions/<question_id>/responses', 'question_responses')
class QuestionResponses(MethodView):
    def get(self, question_id):
        responses = Response.query.filter_by(response_id=question_id).all()
        if len(responses) == 0:
            # Validate that the question ID is valid
            # (Just called for the exception if the question does not exist)
            question_resourse.query_question(question_id)

        return {
            'data': responses_schema.dump(responses),
            'links': {
                'self': url_for('question_responses', id=id, _external=True),
                'question': url_for(
                    'question_detail', id=question_id, _external=True),
            },
        }
