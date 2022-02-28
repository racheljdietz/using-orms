# using-orms
Use SQLAlchemy ORMs to Access MySQL Data in Python.

## Table of Contents
* [Installing](#installing)
* [Connecting](#connecting)
* [Mapping](#mapping)
* [Session](#session)
* [Adding, Updating, and Deleting](#adding-updating-and-deleting)
* [Querying](#querying)

## Installing
- Install SQLAlchemy `pip install sqlalchemy`
- Install a DBAPI complaint driver specific to MySQL database `pip install mysqlclient`

## Connecting
To connect to the database use `create_engine()`. The connection string consists of:
- The `dialect` (mysql), which refers to the name of the database
- The `driver` (mysqldb), which refers to the DBAPI you are using. 
- The `username` and `password` are the credentials to login to the database server. 
- The `host` is the location of the database server. 
- The `database` (dbname) is the name of the database you want to connect to.

```
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqldb://username:password@host/dbname")
```

## Mapping
Use Automap to reflect an existing database into a new model. In the code shown below, a new AutomapBase class is created using `automap_base()`. You reflect the schema and produce mappings by calling `AutomapBase.prepare()` on the resulting base class.

Reflect the tables
```
  Base = automap_base()
  Base.prepare(engine, reflect=True)
```

The mapped classes are now created with names matching that of the table names
```
  User = Base.classes.user
  Entry = Base.classes.entry
  Exercise = Base.classes.exercise
  Workout = Base.classes.workout
```

## Session
The Session establishes all communication with the database. The ORM objects themselves are kept in the Session, in a structure known as the identity map, which is a data structure that keeps track of unique copies of each object, where "unique" implies "only one object with a given primary key." 
- Create a session using `session = Session(engine)`
- Commit changes to the database using `session.commit()`
- Close a session using `session.close()`

**Note** instances are pending until changes are committed to the database using `session.commit()`. Until then, the object is not yet represented by a row in the database.

## Adding, Updating, and Deleting
Adding basics
- Declare an object `new_user = User(username='susanb23', password='password')`
- Add it to the session `session.add(new_user)`
- Add multiple at once `session.add_all([])`

Updating basics
- directly modifying object `new_user.password = 'new_password'`
- or from query 

```
a_user = session.query(User).filter(User.user_id == 1).one()
a_user.password = "password2"
```

Deleting Basics
- Delete a row from a table `session.query(User).filter(User.user_id == 1).delete()`

## Querying
- Using count `session.query(func.count(User.user_id))`
- Using multiple joins and filters. For example, query workouts completed for February 2022, by a specified user

```
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
```
