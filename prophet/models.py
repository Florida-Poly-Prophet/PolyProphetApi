from prophet import db

from sqlalchemy import sql


class User(db.Model):
    """User of the application.
    For now, this is just a mapping from subject identifiers from the Active
    Directory (`sub` key in the JWTs), but will probably contain more
    information in the future.
    TODO Use the subject identifier as the primary key instead of introducing
    new IDs?
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    # TODO Is the sub field length always 44, or should this be extended a bit?
    subject_identifier = db.Column(db.String(44), nullable=False)


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    # TODO Have a length cap?
    prompt = db.Column(db.Text, nullable=False)
    more_info_link = db.Column(db.Text)
    # Null indicates no known correct answer
    correct_answer = db.Column(db.Boolean)
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=sql.func.now())
    # Null indicates no expiration
    expires_at = db.Column(db.DateTime)


class Response(db.Model):
    __tablename__ = 'response'

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), primary_key=True)
    question_id = db.Column(
        db.Integer, db.ForeignKey('question.id'), primary_key=True)

    # Null indicates the user skipped the question
    # TODO Use an enum instead to be more explicit?
    response = db.Column(db.Boolean)
    view_time = db.Column(db.Time, nullable=False)
    answered_at = db.Column(
        db.DateTime, nullable=False, server_default=sql.func.now())

    user = db.relationship('User', backref=db.backref('response', lazy=True))
    question = db.relationship('Question', backref=db.backref('response', lazy=True))
