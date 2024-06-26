from flask import jsonify, render_template, request

from . import main


@main.app_errorhandler(403)
def forbidden(e):
    """Handle HTTP 403 Forbidden Error."""
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "forbidden"})
        response.status_code = 403
        return response
    return render_template("403.html"), 403


@main.app_errorhandler(404)
def page_not_found(e):
    """Handle HTTP 404 Page Not Found Error."""
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "not found"})
        response.status_code = 404
        return response
    return render_template("404.html"), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    """Handle HTTP 500 Internal Server Error."""
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "internal server error"})
        response.status_code = 500
        return response
    return render_template("500.html"), 500
