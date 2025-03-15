from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
db = SQLAlchemy()

IST=pytz.timezone('Asia/Kolkata')

class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    email=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String(20),nullable=False)
    username=db.Column(db.String(100),nullable=False)
    qualification=db.Column(db.String(100),nullable=False)
    date_of_birth=db.Column(db.String(20),nullable=False)
    role=db.Column(db.String(20),nullable=False,default="Student")
    

class Subject(db.Model):
    __tablename__='subject'
    id=db.Column(db.String(50),primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.Text,nullable=False)

class Chapter(db.Model):
    __tablename__='chapter'
    id=db.Column(db.String(50),primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.Text,nullable=False)
    subject_id=db.Column(db.String(100),db.ForeignKey('subject.id'),nullable=False)
    subject=db.relationship('Subject',backref=db.backref('chapters',cascade="all,delete-orphan"))

class Quiz(db.Model):
    __tablename__='quiz'
    id=db.Column(db.String(50),primary_key=True)
    chapter_id=db.Column(db.String(100),db.ForeignKey('chapter.id'),nullable=False)
    remarks=db.Column(db.String(100),nullable=False)
    quiz_date=db.Column(db.Date,nullable=False)
    time_dur=db.Column(db.String(5),nullable=False)
    chapter=db.relationship('Chapter',backref=db.backref('quizzes',cascade="all,delete-orphan"))

class Question(db.Model):
    __tablename__='question'
    id=db.Column(db.String(50),primary_key=True)
    quiz_id=db.Column(db.String(100),db.ForeignKey('quiz.id'),nullable=False)
    que=db.Column(db.Text,nullable=False)
    o_a=db.Column(db.String(300),nullable=False)
    o_b=db.Column(db.String(300),nullable=False)
    o_c=db.Column(db.String(300),nullable=False)
    o_d=db.Column(db.String(300),nullable=False)
    correct_o=db.Column(db.String(1),nullable=False)
    quiz=db.relationship('Quiz',backref=db.backref('questions',cascade="all,delete-orphan"))

class Score(db.Model):
    __tablename__='score'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    quiz_id=db.Column(db.String(100),db.ForeignKey('quiz.id'),nullable=False)
    user_id=db.Column(db.String(100),db.ForeignKey('user.id'),nullable=False)
    attempt_timing=db.Column(db.DateTime,default=lambda:datetime.now(IST))
    tot_score=db.Column(db.Integer,nullable=False)
    quiz=db.relationship('Quiz',backref=db.backref('scores',cascade="all,delete-orphan"))
    user=db.relationship('User',backref=db.backref('scores',cascade="all,delete-orphan"))
    


