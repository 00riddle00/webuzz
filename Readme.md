![App logo](app/static/img/app_logo_for_readme.png)

# WeBuzz - a blogging app.

## Installation

#### Create virtual environment in project's root directory:

```Shell
python3.11 -m venv venv
```

#### Activate the virtual environment:

- ##### For Linux / Mac:

  ```Shell
  source venv/bin/activate
  ```

- ##### For Windows:
  ```Shell
  source venv/Scripts/activate
  ```

#### Install the required packages:

```Shell
pip install -r requirements.txt
```

## Setting environment variables

##### Set these variables:

```Shell
export FLASK_APP=webuzz
export FLASK_DEBUG=1
```

## Running

##### Run the development server:
```Shell
flask run
```
##### Alternative without setting environment variables:
```Shell
flask --app webuzz --debug run
```

## Using

In the [data-dev.sqlite](data-dev.sqlite) database (which is in this Git repo) there are already many "fake" users
as well as four "real" users with the following credentials:

* email: `flask.user@yahoo.com`
* username: `user`
* password: `user`


* email: `flask.moderator@yahoo.com`
* username: `moderator`
* password: `moderator`


* email: `flask.4dmin@yahoo.com`
* username: `4dministrator`
* password: `admin`


* email: `tomasgiedraitis@gmail.com`
* username: `riddle`
* password: `tomas`

## Running with a new database:
* Complete the [Installation](#Installation) and [Setting environment variables](#Setting-environment-variables) steps
  above.
* Remove the existing [data-dev.sqlite](data-dev.sqlite) file
* Remove the [migrations](migrations) directoty
* Run the following commands:
  ```Shell
  flask db init
  flask db migrate -m 'initial migration'
  flask db upgrade
  ```
* Enter the Flask Shell:
  ```Shell
  flask shell
  ```
* Enter these commands inside the shell (possibly modifying them to your needs):
  ```python
  from datetime import datetime
  from app import fake

  Role.insert_roles()

  fake.users(100)
  fake.posts(100)

  user_role = Role.query.filter_by(name="User").first()
  moderator_role = Role.query.filter_by(name="Moderator").first()
  admin_role = Role.query.filter_by(name="Administrator").first()

  user = User(
      email='flask.user@yahoo.com',
      username='user',
      password='user',
      confirmed=1,
      role=user_role,
      name='User',
      location='SQLite database file',
      about_me='\
  I am a User, my whole purpose of existence is \
  to be an example of a user account.',
      member_since=datetime.utcnow(),
  )

  moderator = User(
      email='flask.moderator@yahoo.com',
      username='moderator',
      password='moderator',
      confirmed=1,
      role=moderator_role,
      name='Moderator',
      location='SQLite database file',
      about_me='\
  I am a Moderator, my whole purpose of existence is \
  to be an example of a moderator account.',
      member_since=datetime.utcnow(),
  )

  admin = User(
      email='flask.4dmin@yahoo.com',
      username='4dministrator',
      password='admin',
      confirmed=1,
      role=admin_role,
      name='Administrator',
      location='SQLite database file',
      about_me='\
  I am an Administrator, my whole purpose of existence is \
  to be an example of an admin account.',
      member_since=datetime.utcnow(),
  )

  tomas = User(
      email='tomasgiedraitis@gmail.com',
      username='riddle',
      password='tomas',
      confirmed=1,
      role=user_role,
      name='Tomas',
      location='Vilnius',
      about_me='I am a human.',
      member_since=datetime.utcnow(),
  )

  post_by_tomas = Post(
      body='Hello, this is my first blog post!',
      timestamp=datetime.utcnow(),
      author=tomas,
  )

  db.session.add(user)
  db.session.add(moderator)
  db.session.add(admin)
  db.session.add(tomas)
  db.session.add(post_by_tomas)
  db.session.commit()
  exit()
  ```
* Run the development server:
  ```Shell
  flask run
  ```
* Alternative without setting environment variables:
  ```Shell
  flask --app webuzz --debug run
  ```

## Software dependencies

[Flask](https://flask.palletsprojects.com) - a web development framework that is known for its lightweight and modular design. It has many out-of-the-box features and is easily adaptable to specific requirements.

[Jinja2](https://jinja.palletsprojects.com) - a fast, expressive, extensible templating engine. Special placeholders in the template allow writing code similar to Python syntax. Then the template is passed data to render the final document.

[SQLAlchemy](https://www.sqlalchemy.org) - the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.

[Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com) - an extension for Flask that adds support for SQLAlchemy to the app. It simplifies using SQLAlchemy with Flask by setting up common objects and patterns for using those objects, such as a session tied to each web request, models, and engines. This extension does not change how SQLAlchemy works or is used.

[WTForms](https://wtforms.readthedocs.io) - a flexible forms validation and rendering library for Python web development. It can work with whatever web framework and template engine that is chosen. It supports data validation, CSRF protection, internationalization (I18N), and more.

[Flask WTF](https://flask-wtf.readthedocs.io) - simple integration of Flask and WTForms, including CSRF, file upload, and reCAPTCHA.

[Bootstrap Flask](https://bootstrap-flask.readthedocs.io) - a collection of Jinja macros for Bootstrap and Flask. It helps to render Flask-related data and objects to Bootstrap markup HTML more easily.

For the full list of software dependencies see [requirements.txt](requirements.txt).

## Latest releases

**v0.0.0** (2022-10-18)

## API references

None

## [License](LICENSE)

The MIT License (MIT)

Copyright (c) 2022 Code Academy
