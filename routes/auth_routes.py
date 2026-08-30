from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.database import (
    create_user,
    get_user_by_username,
    add_security_audit_log
)


auth_routes = Blueprint(
    "auth_routes",
    __name__
)


# ==========================================
# REGISTER
# ==========================================

@auth_routes.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # ======================================
        # VALIDATE INPUT
        # ======================================

        if not username or not password:

            flash(
                "Username and password are required."
            )

            return redirect(
                url_for(
                    "auth_routes.register"
                )
            )


        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters."
            )

            return redirect(
                url_for(
                    "auth_routes.register"
                )
            )


        # ======================================
        # CHECK EXISTING USER
        # ======================================

        existing_user = (
            get_user_by_username(
                username
            )
        )


        if existing_user:

            flash(
                "Username already exists."
            )

            return redirect(
                url_for(
                    "auth_routes.register"
                )
            )


        # ======================================
        # HASH PASSWORD
        # ======================================

        password_hash = (
            generate_password_hash(
                password
            )
        )


        # ======================================
        # CREATE USER
        # ======================================

        user_id = create_user(
            username,
            password_hash
        )


        if user_id is None:

            flash(
                "Could not create account."
            )

            return redirect(
                url_for(
                    "auth_routes.register"
                )
            )


        # ======================================
        # AUDIT LOG - REGISTRATION
        # ======================================

        try:

            add_security_audit_log(
                user_id=user_id,
                action="REGISTER_SUCCESS",
                description=(
                    "New user account created successfully."
                ),
                status="SUCCESS"
            )

        except Exception as error:

            print(
                "AUDIT LOG ERROR:",
                error
            )


        flash(
            "Account created successfully. Please login."
        )


        return redirect(
            url_for(
                "auth_routes.login"
            )
        )


    return render_template(
        "register.html"
    )


# ==========================================
# LOGIN
# ==========================================

@auth_routes.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # ======================================
        # FIND USER
        # ======================================

        user = get_user_by_username(
            username
        )


        # ======================================
        # USER NOT FOUND
        # ======================================

        if user is None:

            flash(
                "Invalid username or password."
            )

            try:

                add_security_audit_log(
                    user_id=None,
                    action="LOGIN_FAILED",
                    description=(
                        "Login failed: "
                        "username was not found."
                    ),
                    status="FAILED"
                )

            except Exception as error:

                print(
                    "AUDIT LOG ERROR:",
                    error
                )


            return redirect(
                url_for(
                    "auth_routes.login"
                )
            )


        # ======================================
        # CHECK PASSWORD
        # ======================================

        if not check_password_hash(
            user["password_hash"],
            password
        ):

            flash(
                "Invalid username or password."
            )


            # ==================================
            # AUDIT LOG - WRONG PASSWORD
            # ==================================

            try:

                add_security_audit_log(
                    user_id=user["id"],
                    action="LOGIN_FAILED",
                    description=(
                        "Login failed: "
                        "incorrect password."
                    ),
                    status="FAILED"
                )

            except Exception as error:

                print(
                    "AUDIT LOG ERROR:",
                    error
                )


            return redirect(
                url_for(
                    "auth_routes.login"
                )
            )


        # ======================================
        # LOGIN SUCCESS
        # ======================================

        session["user_id"] = user["id"]

        session["username"] = user["username"]


        # ======================================
        # AUDIT LOG - SUCCESSFUL LOGIN
        # ======================================

        try:

            add_security_audit_log(
                user_id=user["id"],
                action="LOGIN_SUCCESS",
                description=(
                    "User authenticated successfully."
                ),
                status="SUCCESS"
            )

        except Exception as error:

            print(
                "AUDIT LOG ERROR:",
                error
            )


        flash(
            "Login successful!"
        )


        # ======================================
        # REDIRECT BASED ON USER ROLE
        # ======================================

        if user["username"].lower() == "admin":

            return redirect(
                url_for(
                    "dashboard_routes.admin_dashboard"
                )
            )


        return redirect(
            url_for(
                "dashboard_routes.dashboard"
            )
        )


    return render_template(
        "login.html"
    )


# ==========================================
# LOGOUT
# ==========================================

@auth_routes.route(
    "/logout"
)
def logout():

    # ======================================
    # GET CURRENT USER
    # BEFORE CLEARING SESSION
    # ======================================

    user_id = session.get(
        "user_id"
    )

    username = session.get(
        "username",
        "User"
    )


    # ======================================
    # AUDIT LOG - LOGOUT
    # ======================================

    if user_id is not None:

        try:

            add_security_audit_log(
                user_id=user_id,
                action="LOGOUT",
                description=(
                    f"User '{username}' "
                    "logged out successfully."
                ),
                status="SUCCESS"
            )

        except Exception as error:

            print(
                "AUDIT LOG ERROR:",
                error
            )


    # ======================================
    # CLEAR SESSION
    # ======================================

    session.clear()


    flash(
        "You have been logged out."
    )


    return redirect(
        url_for(
            "auth_routes.login"
        )
    )