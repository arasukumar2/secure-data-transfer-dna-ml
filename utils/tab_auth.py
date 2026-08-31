from functools import wraps
import secrets

from flask import (
    request,
    session,
    redirect,
    url_for,
    flash
)

from database.database import (
    get_user_by_tab_token
)


TAB_TOKEN_HEADER = "X-Tab-Token"


def generate_tab_token():
    """
    Generate a secure random token for one browser tab.
    """
    return secrets.token_urlsafe(32)


def get_tab_token():
    """
    Get the tab token sent by the browser.
    """
    return request.headers.get(TAB_TOKEN_HEADER)


def get_current_tab_user():
    """
    Return the user associated with the current tab.
    """

    tab_token = get_tab_token()

    if not tab_token:
        return None

    return get_user_by_tab_token(
        tab_token
    )


def tab_login_required(function):
    """
    Protect a route using the tab-specific
    authentication token.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        user = get_current_tab_user()

        if user is None:

            flash(
                "Please login to continue."
            )

            return redirect(
                url_for(
                    "auth_routes.login"
                )
            )

        # Keep the current user's identity
        # available to existing application code.
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        return function(
            *args,
            **kwargs
        )

    return decorated_function