from peewee import *
from flask import Flask
from flask import request
from flask import g
import json
import dateutil.parser

app = Flask(__name__)
db = SqliteDatabase('db.db')

class Base(Model):
    class Meta:
        database = db

class User(Base):
    name = CharField()

class Workout(Base):
    date_time = DateTimeField()
    duration = IntegerField()
    calories = IntegerField()
    workout_type = CharField()
    user = ForeignKeyField(User, backref = 'workouts')

class Group(Base):
    name = CharField()
    members = ManyToManyField(User, backref = 'groups')


@app.before_request
def before_request():
    g.db = db
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/get_workouts/<int:user_id>')
def get_workouts(user_id):
    user = User.get(User.id == user_id)
    print(len(user.workouts))
    return json.dumps([workout.__dict__['__data__'] for workout in user.workouts], default=str)


@app.route('/submit_workout', methods=['POST'])
def submit_workout():
    workout_json = request.get_json()

    workout = Workout(
            date_time = dateutil.parser.parse(workout_json['date_time']),
            duration = int(workout_json['duration']),
            calories = int(workout_json['calories']),
            workout_type = workout_json['workout_type'],
            user = User.get(User.id == int(workout_json['user_id']))
            )
    workout.save()
    return 'success'


if __name__ == "__main__":
    db.create_tables([User, Workout, Group, Group.members.get_through_model()])
