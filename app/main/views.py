from datetime import datetime

from flask import (
    abort,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries

from .. import db
from ..decorators import admin_required, permission_required
from ..email import send_email
from ..models import Comment, Permission, Post, Role, User
from . import main
from .forms import (
    CommentForm,
    EditProfileAdminForm,
    EditProfileForm,
    NameForm,
    PostForm,
)


@main.route("/shutdown")
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get("werkzeug.server.shutdown")
    if not shutdown:
        abort(500)
    shutdown()
    return "Shutting down..."


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config["SLOW_DB_QUERY_TIME"]:
            current_app.logger.warning(
                "Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n"
                % (
                    query.statement,
                    query.parameters,
                    query.duration,
                    query.context,
                )
            )
    return response


@main.route("/", methods=["GET", "POST"])
def index():
    """Handle the post form and pass old blog posts to the template.

    Also handle pagination.
    """
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(
            body=form.body.data, author=current_user._get_current_object()
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get("show_followed", ""))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    posts = pagination.items
    return render_template(
        "index.html",
        form=form,
        posts=posts,
        show_followed=show_followed,
        pagination=pagination,
    )


@main.route("/about")
def about():
    """Show the page with the info about the web app."""
    return render_template("about.html")


@main.route("/hello/", methods=["GET", "POST"])
@main.route("/hello/<name>", methods=["GET", "POST"])
def hello(name=None):
    """Greet people who come to our web app and choose to say hello to us.

    :param name: the name a person put in URL after "hello/" ('GET' request)
    This page displays a web form asking a page visitor's name. If they submit
    a name, the personal greeting message along with some fun information is
    displayed, and also there appears a link with a text suggesting to hide
    the form and treat the visitor as a normal user. If the visitor clicks it,
    they actually get redirected to /hello/<name> page (via 'POST' request).
    We treat the visitor as "engaged" with our web app at this point and
    suggest them to register and become regular users.
    The code in this function also deals with some of the complexities of both
    '/hello/' and '/hello/<name>' routes being accessible via 'GET' and
    'POST' requests.
    """

    # This page is only for non logged-in visitors
    if current_user.is_authenticated:
        abort(404)

    # Context will be passed to the template for rendering
    context = {}

    # The case when the URL ends in /hello/<name>, where <name> is not empty
    if name:
        # Use this <name> then, no need to have a form
        context["name"] = name

        if request.method == "POST":
            context["visitor_engaged"] = True

            # Notify admin by email that a visitor is interested in signing up
            # to the app.
            if current_app.config["ADMIN_EMAIL"]:
                send_email(
                    current_app.config["ADMIN_EMAIL"],
                    "Visitor interested!",
                    "email/visitor_engaged",
                    visitor_name=context["name"],
                )

        # Also, remove the previous name (if it exists) from the session.
        #
        # This happens when firstly user goes to /hello and enters a name,
        # then goes to /hello/<name>, and then returns to /hello.
        #
        # So we need to make sure that in this case a user returning from
        # /hello/<name> to /hello should be greeted as a stranger again.
        session["name"] = None
        session["form_was_submitted"] = False

    # The case when the URL ends in /hello
    else:
        context["name"] = session.get("name")

        # We need a form to ask for user name or allow them to change the name.
        form = NameForm()
        # Add this form to context, to be passed further for rendering
        context["form"] = form

        # This is true if a form is already submitted (via 'POST' request)
        # and also all its inputs are valid
        if form.validate_on_submit():
            session["form_was_submitted"] = True
            old_name = context["name"]

            # Message flashing
            if old_name is not None and old_name != form.name.data:
                flash("Looks like you have changed your name!")

            session["name"] = form.name.data
            return redirect(url_for(".hello"))

    temperatures = [10, 15, 20, 25, 30]

    current_time = datetime.utcnow()

    hello_msgs = {
        "morning": "Good morning!",
        "day": "Good afternoon!",
        "evening": "Good evening!",
        "night": "Good night!",
    }

    funny_msgs = [
        "I like it.",
        "I dislike it.",
    ]

    more_context = {
        "temperatures": temperatures,
        "current_time": current_time,
        "hello_msgs": hello_msgs,
        "funny_msgs": funny_msgs,
    }

    context = {**context, **more_context}

    return render_template(
        "hello.html",
        **context,
    )


# user profile page route
@main.route("/user/<username>")
def user(username):
    """Show user's profile with posts."""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    posts = pagination.items
    return render_template(
        "user.html", user=user, posts=posts, pagination=pagination
    )


# edit user profile route
@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.default_gravatar = form.default_gravatar.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for(".user", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)


# edit user profile route for administrators
@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("The profile has been updated.")
        return redirect(url_for(".user", username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template("edit_profile.html", form=form, user=user)


@main.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post=post,
            author=current_user._get_current_object(),
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been published.")
        return redirect(url_for(".post", id=post.id, page=-1))
    page = request.args.get("page", 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config[
            "COMMENTS_PER_PAGE"
        ] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page=page,
        per_page=current_app.config["COMMENTS_PER_PAGE"],
        error_out=False,
    )
    comments = pagination.items
    return render_template(
        "post.html",
        posts=[post],
        form=form,
        comments=comments,
        pagination=pagination,
    )


@main.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("The post has been updated.")
        return redirect(url_for(".post", id=post.id))
    form.body.data = post.body
    return render_template("edit_post.html", form=form)


@main.route("/follow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    if current_user.is_following(user):
        flash("You are already following this user.")
        return redirect(url_for(".user", username=username))
    current_user.follow(user)
    db.session.commit()
    flash("You are now following %s." % username)
    return redirect(url_for(".user", username=username))


@main.route("/unfollow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    if not current_user.is_following(user):
        flash("You are not following this user.")
        return redirect(url_for(".user", username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash("You are not following %s anymore." % username)
    return redirect(url_for(".user", username=username))


@main.route("/followers/<username>")
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(
        page=page,
        per_page=current_app.config["FOLLOWERS_PER_PAGE"],
        error_out=False,
    )
    follows = [
        {"user": item.follower, "timestamp": item.timestamp}
        for item in pagination.items
    ]
    return render_template(
        "followers.html",
        user=user,
        title="Followers of",
        endpoint=".followers",
        pagination=pagination,
        follows=follows,
    )


@main.route("/followed_by/<username>")
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followed.paginate(
        page=page,
        per_page=current_app.config["FOLLOWERS_PER_PAGE"],
        error_out=False,
    )
    follows = [
        {"user": item.followed, "timestamp": item.timestamp}
        for item in pagination.items
    ]
    return render_template(
        "followers.html",
        user=user,
        title="Followed by",
        endpoint=".followed_by",
        pagination=pagination,
        follows=follows,
    )


@main.route("/all")
@login_required
def show_all():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "", max_age=30 * 24 * 60 * 60)
    return resp


@main.route("/followed")
@login_required
def show_followed():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "1", max_age=30 * 24 * 60 * 60)
    return resp


@main.route("/moderate")
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["COMMENTS_PER_PAGE"],
        error_out=False,
    )
    comments = pagination.items
    return render_template(
        "moderate.html", comments=comments, pagination=pagination, page=page
    )


@main.route("/moderate/enable/<int:id>")
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(
        url_for(".moderate", page=request.args.get("page", 1, type=int))
    )


@main.route("/moderate/disable/<int:id>")
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(
        url_for(".moderate", page=request.args.get("page", 1, type=int))
    )
