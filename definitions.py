# These are the mapping definitions to be used within the Flask API
# decorators to associate a function with a url

import config

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import extract  
from sqlalchemy import func
from sqlalchemy import distinct
from sqlalchemy import exists

# connecting
engine = create_engine(config.engine)

# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name
User = Base.classes.user
Entry = Base.classes.entry
Exercise = Base.classes.exercise
Workout = Base.classes.workout
WorkoutAgenda = Base.classes.workout_agenda

# creating a session
session = Session(engine)

# authenticate user
def authUser(username: str, password: str):
    result = session.query(exists().where(User.username == username, User.password == password)).scalar()
    return result # returns true if exists, false if not

# add new user
def addUser(username: str, password: str, image: str):
    new_user = User(username = username, password = password, image=image)
    session.add(new_user)
    session.commit()
    return "User added"

# get profile image
def getProfImg(file: str, user: str):
    user = session.query(User).filter(User.username == user).one()
    return user.image

# update profile image
def updateProfImg(file: str, user: str):
    user = session.query(User).filter(User.username == user).one()
    user.image = file
    session.commit()
    return "Updated profile image"

# get username
def getUser(userid: int):
    user = session.query(User).filter(User.user_id == userid).one()
    return user.username

# get total count of workouts for user
def countWorkouts(user: str):
    count = session.query(func.count(distinct(Entry.date))).\
        filter(User.username==user).scalar()
    return count

# update user password
def updatePW(pw: str):
    user = session.query(User).filter(User.username == user).one()
    user.password = pw
    session.commit()
    return "Password updated"

# delete user account
def deleteUser(userid: int):

    result = session.query(Workout.workout_id).filter(Workout.user_id == userid).all()
    workouts = [r[0] for r in result]

    # delete from workout agenda and entries
    for id in workouts:
        session.query(WorkoutAgenda).filter(WorkoutAgenda.workout_id == id).delete()
        session.query(Entry).filter(Entry.workout_id == id).delete()

    # delete from workouts
    session.query(Workout).filter(Workout.user_id == userid).delete()

    # delete from user table
    session.query(User).filter(User.user_id == userid).delete()
    session.commit()
    return "User deleted"

# get user workouts
def getUserWorkouts(userid: int):
    result = session.query(Workout.title).filter(Workout.user_id == userid).all()
    workouts = [r[0] for r in result]
    return workouts

# create new workout for user
def addWorkout(title: str, userid: int, exercises: list):
    new_workout = Workout(title = title, user_id = userid)
    session.add(new_workout)
    session.commit()
    
    workoutid = session.query(func.max(Workout.workout_id)).scalar()

    # add all exercises
    for exerciseid in exercises:
        new = WorkoutAgenda(workout_id = workoutid, exercise_id = exerciseid)
        session.add(new)
        session.commit()

    return "Workout added"

# get exercises for workout
def getWorkoutExercises(workout: int):
    result = session.query(Exercise.name).\
        join(WorkoutAgenda, WorkoutAgenda.exercise_id == Exercise.exercise_id).\
            join(Workout, Workout.workout_id == WorkoutAgenda.workout_id).\
        filter(Workout.workout_id == workout).all()
    return result

# get exercises for muscle group
def getExercisesForMuscle(muscle: str):
    result = session.query(Exercise.name).filter(Exercise.type == muscle).all()
    return result

# get past workouts completed by month and year
def queryWorkouts(month: int, year: int, user: str):
    result = session.query(Entry, Exercise, Workout).\
        outerjoin(Exercise, Entry.exercise_id == Exercise.exercise_id).\
        join(Workout, Exercise.exercise_id == Workout.exercise_id).\
        filter(
            extract('month', Entry.date)==month,
            extract('year', Entry.date)==year,
            User.username == user)
    return result

# insert new completed workout
def addEntry(lbs, sets, reps, date, exercise_id, workout_id):
    new_entry = Entry(lbs=lbs, sets=sets, reps=reps, date=date, exercise_id=exercise_id, workout_id=workout_id)
    session.add(new_entry)
    session.commit()

# get past lbs,sets,and reps for an exercise
def getPastStats(exercise: int):
    result = session.query(Entry.lbs, Entry.sets, Entry.reps).filter(Entry.exercise_id == exercise).order_by(Entry.entry_id.desc()).first()
    return result