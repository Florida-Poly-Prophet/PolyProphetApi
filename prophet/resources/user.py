from http import HTTPStatus

from flask import g, request, url_for
from flask.views import MethodView

from prophet import app, class_route, db
from prophet.auth import msal_app, requires_auth
from prophet.models import User, Response
from prophet.schemas import UserSchema, user_schema, users_schema, responses_schema


class UserNotFound(Exception):
    def __init__(self, id):
        self.id = id


@app.errorhandler(UserNotFound)
def handle_user_not_found(e):
    return {
        'error': {
            'code': 'user_not_found',
            'description': f"User `{e.id}` does not exist",
        },
    }, HTTPStatus.NOT_FOUND


def create_user(sub, commit=True):
    """Creates a new user entry in the database from the subject identifier.

    By default, a database transaction will be committed immediately. If the
    session will be committed later anyway, `commit` can be set to False.
    """
    user = User(subject_identifier=sub)
    db.session.add(user)
    if commit:
        db.session.commit()

    return user


def query_user(id, create=False):
    """Gets a user from the database, creating it if necessary.
    Accepts the user ID (local to this database) or the string "me" to indicate
    the current user.

    TODO Accept Active Directory subject identifiers as well, or only do this
    when creating users?

    If `create` is True and `id` is "me", the user entry will be created if it
    does not already exist. It cannot automatically create users that are not
    signed in since creating the database entry requires the subject identifier.
    """
    # TODO Accept user IDs, SUBs, or both?
    if id == 'me':
        if not hasattr(g, 'current_user'):
            raise AuthError("User must be logged in to access `/users/me`")

        sub = g.current_user.sub
        user = User.query.filter_by(subject_identifier=sub).first()
        if user is None:
            if create:
                return create_user(sub)
            else:
                raise UserNotFound(id)

        return user
    else:
        user = User.query.get(id)
        if user is None:
            raise UserNotFound(id)
        return user


def user_with_links(user):
    # TODO Should this use "me" in URLS when possible, or always use explicit
    # IDs so that the links will work for others (probably not an actual use
    # case, but it would be nice to be consistent).
    #
    # TODO Pull in more details from the auth token and/or MS Graph API
    #
    # TODO This complains about the scope being invalid. Using on-behalf-of
    # works fine, though
    # auth_result = msal_app.acquire_token_for_client(["User.Read.All"])
    # auth_result = msal_app.acquire_token_on_behalf_of(
    #     g.user_access_token, ["User.ReadBasic.All"])
    return {
        'data': user_schema.dump(user),
        'links': {
            'self': url_for('user_detail', id=user.id, _external=True),
            'responses': url_for(
                'user_responses', user_id=user.id, _external=True),
        },
    }


@class_route('/users/<id>', 'user_detail')
class UserDetail(MethodView):
    def get(self, id):
        user = query_user(id, True)
        return user_with_links(user)

    def delete(self, id):
        # Don't create the user since it will be deleted immediately
        user = query_user(id)
        # TODO Delete the user's responses? Does this happend automatically?
        db.session.delete(user)
        db.session.commit()
        return {
            'data': {}
        }


@class_route('/users', 'user_list')
class UserList(MethodView):
    def get(self):
        return {
            'data': users_schema.dump(User.query.all()),
            'links': {
                'self': url_for('user_list', _external=True),
            },
        }

    def post(self):
        data = user_create_args.load(request.get_json())
        user = create_user(data['subject_identifier'])
        return user_with_links(user)


# @class_route('/users/<id>/questions', 'user_question_list')
# class UserQuestions(MethodView):
#     """Route for a user's unanswered questions."""

#     def get(self, id):
