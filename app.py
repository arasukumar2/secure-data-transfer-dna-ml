import os

os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"

from flask import (
    Flask,
    redirect,
    url_for,
    request,
    session,
    Response
)

from routes.file_routes import file_routes
from routes.dashboard_routes import dashboard_routes
from routes.auth_routes import auth_routes
from routes.transfer_routes import transfer_routes

from database.database import (
    initialize_database,
    create_initial_admin
)



create_initial_admin()

# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# SECRET KEY
# ==========================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-this"
)


# ==========================================
# SESSION SECURITY
# ==========================================

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# False for local HTTP development.
# Change to True when deployed with HTTPS.

app.config["SESSION_COOKIE_SECURE"] = True


# ==========================================
# FILE UPLOAD LIMIT
# ==========================================

app.config["MAX_CONTENT_LENGTH"] = (
    50 * 1024 * 1024
)


# ==========================================
# DATABASE
# ==========================================

initialize_database()


# ==========================================
# BLUEPRINTS
# ==========================================

app.register_blueprint(
    auth_routes
)

app.register_blueprint(
    file_routes
)

app.register_blueprint(
    dashboard_routes
)

app.register_blueprint(
    transfer_routes
)


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/")
def home():
    return redirect(
        url_for("auth_routes.login")
    )


# ==========================================
# TAB TOKEN REQUEST HANDLING
# ==========================================

@app.before_request
def restore_tab_session():

    # Login/register/static resources do not
    # require a tab session.
    if request.endpoint in (
        "auth_routes.login",
        "auth_routes.register"
    ):
        return None

    if request.path.startswith(
        "/static/"
    ):
        return None

    tab_token = (
        request.args.get("tab_token")
        or request.form.get("tab_token")
        or request.headers.get("X-Tab-Token")
    )

    if not tab_token:
        return None

    from database.database import (
        get_user_by_tab_token
    )

    user = get_user_by_tab_token(
        tab_token
    )

    if user:

        session["tab_token"] = tab_token
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

    return None
@app.after_request
def add_tab_auth_script(response):

    content_type = response.headers.get(
        "Content-Type",
        ""
    )

    if (
        "text/html" not in content_type
        or request.path.startswith("/static/")
    ):
        return response

    script = """
<script>
(function () {

    const KEY =
        "secure_data_transfer_tab_token";

    let token =
        sessionStorage.getItem(KEY);

    if (!token) {
        return;
    }

    function addTokenToUrl(url) {

        try {

            const parsed =
                new URL(
                    url,
                    window.location.origin
                );

            if (
                parsed.origin ===
                window.location.origin
            ) {

                parsed.searchParams.set(
                    "tab_token",
                    token
                );

                return parsed.toString();
            }

        } catch (error) {
            return url;
        }

        return url;
    }


    document
        .querySelectorAll("a[href]")
        .forEach(function (link) {

            const href =
                link.getAttribute("href");

            if (
                href &&
                !href.startsWith("#") &&
                !href.startsWith("javascript:")
            ) {

                link.setAttribute(
                    "href",
                    addTokenToUrl(href)
                );

            }

        });


    document
        .querySelectorAll("form")
        .forEach(function (form) {

            let input =
                form.querySelector(
                    'input[name="tab_token"]'
                );

            if (!input) {

                input =
                    document.createElement(
                        "input"
                    );

                input.type = "hidden";
                input.name = "tab_token";

                form.appendChild(
                    input
                );

            }

            input.value = token;

        });

})();
</script>
"""

    if response.direct_passthrough:
        return response

    data = response.get_data(
        as_text=True
    )

    data = data.replace(
        "</body>",
        script + "</body>"
    )

    response.set_data(data)

    return response

# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )