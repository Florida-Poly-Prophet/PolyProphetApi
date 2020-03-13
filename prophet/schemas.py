from prophet import ma
from prophet.models import User, Question, Response


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    # Only give the internal ID, not the Active Directory identifier
    id = ma.auto_field(dump_only=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class QuestionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Question
        load_instance = True

    id = ma.auto_field(dump_only=True)
    prompt = ma.auto_field()
    # TODO Only dump for privileged users
    correct_answer = ma.auto_field()
    more_info_link = ma.auto_field()
    # TODO Allow writing to this?
    created_at = ma.auto_field(dump_only=True)
    expires_at = ma.auto_field()


question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)


class ResponseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Response
        load_instance = True

    user_id = ma.auto_field()
    question_id = ma.auto_field()
    response = ma.auto_field()
    view_time = ma.auto_field()
    answered_at = ma.auto_field()


response_schema = ResponseSchema()
responses_schema = ResponseSchema(many=True)
