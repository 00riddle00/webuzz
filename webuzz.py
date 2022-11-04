#!/usr/bin/env python3

"""Here the Flask application instance is defined."""

import os

import click
from dotenv import load_dotenv
from flask_migrate import Migrate, upgrade

from app import create_app, db
from app.models import Comment, Follow, Permission, Post, Role, User

basedir = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(basedir, ".env")
if os.path.exists(dotenv_path):
    # take environment variables from .env file
    load_dotenv(dotenv_path)


app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    """Add database object and models to Flask shell context."""
    return dict(
        db=db,
        User=User,
        Role=Role,
        Permission=Permission,
        Comment=Comment,
        Follow=Follow,
        Post=Post,
    )


@app.cli.command()
@click.argument("test_names", nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest

    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def deploy():
    """Runs deployment. Allows database migration,
    creating/updating roles, adds user self follow."""
    upgrade()

    Role.insert_roles()

    User.add_self_follows()


@app.cli.command()
@click.option(
    "--length",
    default=25,
    help="Number of functions to include in the profiler report.",
)
@click.option(
    "--profile-dir",
    default=None,
    help="Directory where profiler data files are saved.",
)
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware

    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app, restrictions=[length], profile_dir=profile_dir
    )
    app.run(debug=False)
