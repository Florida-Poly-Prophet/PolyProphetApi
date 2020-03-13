from http import HTTPStatus

from flask import request, url_for
from flask.views import MethodView

from marshmallow import Schema, fields

from prophet import app, class_route, db
from prophet.models import Question, Response
from prophet.schemas import question_schema, questions_schema, responses_schema


class QuestionNotFound(Exception):
    def __init__(self, id):
        self.id = id


@app.errorhandler(QuestionNotFound)
def handle_question_not_found(e):
    return {
        'error': {
            'code': 'question_not_found',
            'description': f"Question `{e.id}` does not exist",
        },
    }, HTTPStatus.NOT_FOUND


def query_question(id):
    q = Question.query.get(id)
    if q is None:
        raise QuestionNotFound(id)

    return q


def question_with_links(q):
    return {
        'data': question_schema.dump(q),
        'links': {
            'self': url_for('question_detail', id=q.id, _external=True),
            'responses': url_for(
                'question_responses', question_id=q.id, _external=True),
        },
    }


# TODO Restrict the type of `id` in the URL rule and figure out how to properly
# handle errors with flask
@class_route('/questions/<id>', 'question_detail')
class QuestionDetail(MethodView):
    def get(self, id):
        q = query_question(id)
        return question_with_links(q)

    def put(self, id):
        q = query_question(id)
        q = question_schema.load(request.get_json(), instance=q, partial=True)
        db.session.add(q)
        db.session.commit()
        return question_with_links(q)

    def delete(self, id):
        q = query_question(id)
        db.session.delete(q)
        db.session.commit()
        return {
            'data': {}
        }


@class_route('/questions', 'question_list')
class QuestionList(MethodView):
    def get(self):
        return {
            'data': questions_schema.dump(Question.query.all()),
            'links': {
                'self': url_for('question_list', _external=True),
            },
        }

    def post(self):
        q = question_schema.load(request.get_json())
        db.session.add(q)
        db.session.commit()
        return question_with_links(q)
