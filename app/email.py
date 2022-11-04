from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from . import mail


def send_async_email(app, msg):
    """Send email in a new thread.

    Flask-Mail’s send() function uses current_app, so it requires the
    application context to be active. But since contexts are associated with a
    thread, when the mail.send() function executes in a different thread it
    needs the application context to be created artificially using
    app.app_context(). The app instance is passed to the thread as an argument
    so that a context can be created.
    """
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """Send an email using a HTML template (and a plain text alternative).

    :param **kwargs: These arguments will be resent to templates to be used
    there, e.g. user=user.

    To avoid unnecessary delays during request handling, the email send
    function can be moved to a background thread.
    """
    app = current_app._get_current_object()

    msg = Message(
        f"{app.config['MAIL_SUBJECT_PREFIX']} {subject}",
        sender=app.config["MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
