import config

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import extract  
from sqlalchemy import func


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

# creating a session
session = Session(engine)

# adding and updating objects
new_user = User(username='susanb23', password='password')
session.add(new_user)

# update from object
new_user.username = 'suzie39'

# update by query
a_user = session.query(User).filter(User.user_id == 1).one()
a_user.password = "password2"

# query all users
for instance in session.query(User):
    print("User: ", instance.username)

# query workouts completed for a given month and year by user
result = session.query(Entry, Exercise, Workout).\
    outerjoin(Exercise, Entry.exercise_id == Exercise.exercise_id).\
    join(Workout, Exercise.exercise_id == Workout.exercise_id).\
    filter(
        extract('month', Entry.date)==2,
        extract('year', Entry.date)==2022,
        User.user_id == 1)

for row in result:
    print(row.workout.title, 
            row.exercise.name,
            row.entry.lbs, 
            row.entry.sets,
            row.entry.reps,
            row.entry.date)

# count all users
count = session.query(func.count(User.user_id)).scalar()
print(count)

# delete user
session.query(User).filter(User.user_id == 3).delete()

# commit all changes
session.commit()