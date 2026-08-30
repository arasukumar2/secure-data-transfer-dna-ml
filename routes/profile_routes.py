from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for
)

from utils.auth_utils import login_required


profile_routes = Blueprint(
    "profile_routes",
    __name__
)


@profile_routes.route(
    "/profile",
    methods=["GET"]
)
@login_required
def profile():

    user_id = session["user_id"]

    username = session.get(
        "username",
        "User"
    )

    return render_template(
        "profile.html",
        username=username,
        user_id=user_id
    )