from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
    flash
)


def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login to continue."
            )

            return redirect(
                url_for(
                    "auth_routes.login"
                )
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function