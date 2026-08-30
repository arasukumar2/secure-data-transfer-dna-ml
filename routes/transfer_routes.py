from flask import (
    Blueprint,
    render_template,
    session
)

from database.database import (
    get_all_transfers_by_user
)

from utils.auth_utils import login_required


transfer_routes = Blueprint(
    "transfer_routes",
    __name__
)


# ==========================================
# TRANSFER HISTORY
# ==========================================

@transfer_routes.route(
    "/transfers",
    methods=["GET"]
)
@login_required
def transfers():

    user_id = session["user_id"]

    transfers = get_all_transfers_by_user(
        user_id
    )

    return render_template(
        "transfers.html",
        transfers=transfers
    )