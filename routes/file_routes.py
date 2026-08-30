import os
import uuid

from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    render_template,
    send_file,
    session,
    after_this_request
)

from werkzeug.utils import secure_filename

from crypto.file_crypto import (
    encrypt_file,
    decrypt_encrypted_file
)

from database.database import (
    get_file_by_id_and_user,
    add_file,
    get_files_by_user,
    delete_file,
    add_transfer
)

from cloud_storage.local_storage import (
    upload_file as cloud_upload_file,
    download_file as cloud_download_file,
    delete_file as cloud_delete_file
)

from utils.auth_utils import login_required


# ==========================================
# BLUEPRINT
# ==========================================

file_routes = Blueprint(
    "file_routes",
    __name__
)


# ==========================================
# ALLOWED FILE TYPES
# ==========================================

ALLOWED_EXTENSIONS = {
    "txt",
    "pdf",
    "doc",
    "docx",
    "jpg",
    "jpeg",
    "png",
    "csv",
    "zip"
}


def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ==========================================
# FOLDERS
# ==========================================

UPLOAD_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted"
DOWNLOAD_FOLDER = "downloads"


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    ENCRYPTED_FOLDER,
    exist_ok=True
)

os.makedirs(
    DOWNLOAD_FOLDER,
    exist_ok=True
)


# ==========================================
# UPLOAD PAGE
# ==========================================

@file_routes.route(
    "/upload",
    methods=["GET"]
)
@login_required
def upload_page():

    return render_template(
        "upload.html"
    )


# ==========================================
# UPLOAD + ENCRYPT
# ==========================================

@file_routes.route(
    "/upload",
    methods=["POST"]
)
@login_required
def upload_file():

    user_id = session["user_id"]

    original_path = None
    encrypted_path = None
    cloud_uploaded = False
    file_id = None
    encrypted_filename = None

    try:

        # ======================================
        # CHECK FILE
        # ======================================

        if "file" not in request.files:

            flash(
                "No file selected."
            )

            return redirect(
                url_for(
                    "file_routes.upload_page"
                )
            )


        file = request.files["file"]


        if file.filename == "":

            flash(
                "No file selected."
            )

            return redirect(
                url_for(
                    "file_routes.upload_page"
                )
            )


        # ======================================
        # SECURE FILENAME
        # ======================================

        original_filename = secure_filename(
            file.filename
        )


        if not original_filename:

            flash(
                "Invalid filename."
            )

            return redirect(
                url_for(
                    "file_routes.upload_page"
                )
            )


        # ======================================
        # FILE TYPE VALIDATION
        # ======================================

        if not allowed_file(
            original_filename
        ):

            flash(
                "File type is not allowed."
            )

            return redirect(
                url_for(
                    "file_routes.upload_page"
                )
            )


        # ======================================
        # UNIQUE FILE PATHS
        # ======================================

        unique_id = uuid.uuid4().hex


        encrypted_filename = (
            unique_id + ".encrypted"
        )


        # Temporary plaintext filename
        temp_original_filename = (
            unique_id
            + "_"
            + original_filename
        )


        original_path = os.path.join(
            UPLOAD_FOLDER,
            temp_original_filename
        )


        encrypted_path = os.path.join(
            ENCRYPTED_FOLDER,
            encrypted_filename
        )


        # ======================================
        # SAVE PLAINTEXT TEMPORARILY
        # ======================================

        file.save(
            original_path
        )


        file_size = os.path.getsize(
            original_path
        )


        print()
        print("================================")
        print("SECURE FILE TRANSFER")
        print("================================")


        print(
            "User ID:",
            user_id
        )


        print(
            "Username:",
            session.get("username")
        )


        print(
            "Original file:",
            original_filename
        )


        print(
            "File size:",
            file_size,
            "bytes"
        )


        # ======================================
        # ENCRYPT FILE
        # ======================================

        print()
        print(
            "Encrypting file..."
        )


        pseudo_key = encrypt_file(
            original_path,
            encrypted_path
        )


        print(
            "Encryption completed."
        )


        # ======================================
        # VERIFY ENCRYPTED FILE
        # ======================================

        if not os.path.exists(
            encrypted_path
        ):

            raise RuntimeError(
                "Encrypted file was not created."
            )


        if os.path.getsize(
            encrypted_path
        ) == 0:

            raise RuntimeError(
                "Encrypted file is empty."
            )


        # ======================================
        # UPLOAD ENCRYPTED FILE
        # ======================================

        print()
        print(
            "Uploading encrypted file..."
        )


        cloud_upload_path = cloud_upload_file(
            encrypted_path,
            encrypted_filename
        )


        cloud_uploaded = True


        print(
            "Cloud storage path:",
            cloud_upload_path
        )


        # ======================================
        # DELETE PLAINTEXT
        # ======================================

        if os.path.exists(
            original_path
        ):

            os.remove(
                original_path
            )

            original_path = None


        print(
            "Plaintext file deleted."
        )


        # ======================================
        # PSEUDO KEY TO STRING
        # ======================================

        pseudo_key_string = ",".join(
            str(value)
            for value in pseudo_key
        )


        # ======================================
        # DATABASE RECORD
        # ======================================

        file_id = add_file(
            original_filename=original_filename,
            encrypted_filename=encrypted_filename,
            file_size=file_size,
            pseudo_key=pseudo_key_string,
            user_id=user_id,
            status="Encrypted"
        )


        if file_id is None:

            raise RuntimeError(
                "Database record could not be created."
            )


        print(
            "Database record created."
        )


        print(
            "File ID:",
            file_id
        )


        print(
            "Owner User ID:",
            user_id
        )


        # ======================================
        # TRANSFER HISTORY
        # ======================================

        add_transfer(
            user_id=user_id,
            file_id=file_id,
            action="UPLOAD",
            status="SUCCESS"
        )


        print(
            "Upload activity recorded."
        )


        # ======================================
        # REMOVE LOCAL ENCRYPTED COPY
        # ======================================

        if os.path.exists(
            encrypted_path
        ):

            os.remove(
                encrypted_path
            )

            encrypted_path = None


        print()
        print(
            "SECURE UPLOAD COMPLETED!"
        )

        print(
            "================================"
        )


        flash(
            "File uploaded, encrypted and securely stored!"
        )


        return redirect(
            url_for(
                "file_routes.my_files"
            )
        )


    except Exception as error:

        print()
        print(
            "SECURE UPLOAD ERROR:",
            str(error)
        )


        # ======================================
        # REMOVE TEMPORARY PLAINTEXT
        # ======================================

        if (
            original_path
            and os.path.exists(original_path)
        ):

            try:

                os.remove(
                    original_path
                )

                print(
                    "Temporary plaintext removed."
                )

            except Exception as cleanup_error:

                print(
                    "Plaintext cleanup failed:",
                    cleanup_error
                )


        # ======================================
        # REMOVE LOCAL ENCRYPTED FILE
        # ======================================

        if (
            encrypted_path
            and os.path.exists(encrypted_path)
        ):

            try:

                os.remove(
                    encrypted_path
                )

                print(
                    "Temporary encrypted file removed."
                )

            except Exception as cleanup_error:

                print(
                    "Encrypted cleanup failed:",
                    cleanup_error
                )


        # ======================================
        # REMOVE CLOUD FILE IF NECESSARY
        # ======================================

        if cloud_uploaded and file_id is None:

            try:

                cloud_delete_file(
                    encrypted_filename
                )

                print(
                    "Orphaned cloud file removed."
                )

            except Exception as cleanup_error:

                print(
                    "Cloud cleanup failed:",
                    cleanup_error
                )


        flash(
            "Upload failed. Your file was not stored."
        )


        return redirect(
            url_for(
                "file_routes.upload_page"
            )
        )


# ==========================================
# DOWNLOAD + DECRYPT
# ==========================================

@file_routes.route(
    "/download/<int:file_id>",
    methods=["GET"]
)
@login_required
def download_file(file_id):

    user_id = session["user_id"]

    encrypted_path = None
    output_path = None

    try:

        # ======================================
        # OWNERSHIP CHECK
        # ======================================

        file_record = get_file_by_id_and_user(
            file_id,
            user_id
        )

        if file_record is None:

            flash(
                "File not found or access denied."
            )

            return redirect(
                url_for(
                    "file_routes.my_files"
                )
            )


        # ======================================
        # FILE INFORMATION
        # ======================================

        encrypted_filename = (
            file_record["encrypted_filename"]
        )

        original_filename = (
            file_record["original_filename"]
        )

        pseudo_key_string = (
            file_record["pseudo_key"]
        )


        # ======================================
        # CONVERT PSEUDO KEY
        # ======================================

        pseudo_key = [
            int(value)
            for value in pseudo_key_string.split(",")
            if value
        ]

        if not pseudo_key:

            raise RuntimeError(
                "Invalid encryption key."
            )


        # ======================================
        # CREATE TEMPORARY FILENAMES
        # ======================================

        download_id = uuid.uuid4().hex


        encrypted_temp_filename = (
            download_id
            + "_"
            + encrypted_filename
        )


        output_temp_filename = (
            download_id
            + "_"
            + original_filename
        )


        encrypted_path = os.path.join(
            DOWNLOAD_FOLDER,
            encrypted_temp_filename
        )


        output_path = os.path.join(
            DOWNLOAD_FOLDER,
            output_temp_filename
        )


        # ======================================
        # SECURE DOWNLOAD
        # ======================================

        print()
        print("================================")
        print("SECURE DOWNLOAD")
        print("================================")

        print(
            "User ID:",
            user_id
        )

        print(
            "Cloud file:",
            encrypted_filename
        )


        # ======================================
        # DOWNLOAD FROM CLOUD
        # ======================================

        cloud_download_file(
            encrypted_filename,
            encrypted_path
        )


        if not os.path.exists(
            encrypted_path
        ):

            raise RuntimeError(
                "Encrypted file could not be downloaded."
            )


        print(
            "Encrypted file downloaded."
        )


        # ======================================
        # DECRYPT
        # ======================================

        print(
            "Decrypting file..."
        )


        decrypt_encrypted_file(
            encrypted_path,
            output_path,
            pseudo_key
        )


        if not os.path.exists(
            output_path
        ):

            raise RuntimeError(
                "Decrypted file was not created."
            )


        print(
            "Decryption completed."
        )


        # ======================================
        # DELETE TEMPORARY ENCRYPTED COPY
        # ======================================

        if os.path.exists(
            encrypted_path
        ):

            os.remove(
                encrypted_path
            )

            encrypted_path = None

            print(
                "Temporary encrypted download removed."
            )


        # ======================================
        # RECORD DOWNLOAD
        # ======================================

        add_transfer(
            user_id=user_id,
            file_id=file_id,
            action="DOWNLOAD",
            status="SUCCESS"
        )


        print(
            "Download activity recorded."
        )


        print(
            "================================"
        )

        print(
            "SECURE DOWNLOAD COMPLETED!"
        )

        print(
            "================================"
        )


        # ======================================
        # SEND FILE
        # ======================================
        #
        # IMPORTANT:
        # We do NOT delete output_path here.
        #
        # Windows keeps the file locked while
        # Flask is sending it to the browser.
        #
        # The temporary decrypted file will
        # remain in downloads until the next
        # cleanup pass.
        #

        return send_file(
            output_path,
            as_attachment=True,
            download_name=original_filename
        )


    # ==========================================
    # CLOUD FILE NOT FOUND
    # ==========================================

    except FileNotFoundError:

        flash(
            "Encrypted cloud file not found."
        )

        return redirect(
            url_for(
                "file_routes.my_files"
            )
        )


    # ==========================================
    # DOWNLOAD ERROR
    # ==========================================

    except Exception as error:

        print()
        print(
            "SECURE DOWNLOAD ERROR:",
            str(error)
        )


        # ======================================
        # CLEANUP ENCRYPTED TEMPORARY FILE
        # ======================================

        if (
            encrypted_path
            and os.path.exists(
                encrypted_path
            )
        ):

            try:

                os.remove(
                    encrypted_path
                )

            except Exception as cleanup_error:

                print(
                    "Encrypted cleanup failed:",
                    cleanup_error
                )


        # ======================================
        # CLEANUP DECRYPTED FILE
        # ======================================

        if (
            output_path
            and os.path.exists(
                output_path
            )
        ):

            try:

                os.remove(
                    output_path
                )

            except Exception as cleanup_error:

                print(
                    "Decrypted cleanup failed:",
                    cleanup_error
                )


        flash(
            "Download failed. The file could not be decrypted."
        )


        return redirect(
            url_for(
                "file_routes.my_files"
            )
        )


# ==========================================
# MY FILES
# ==========================================

@file_routes.route(
    "/files",
    methods=["GET"]
)
@login_required
def my_files():

    user_id = session["user_id"]


    files = get_files_by_user(
        user_id
    )


    return render_template(
        "files.html",
        files=files
    )


# ==========================================
# DELETE FILE
# ==========================================

@file_routes.route(
    "/delete/<int:file_id>",
    methods=["POST"]
)
@login_required
def delete_uploaded_file(file_id):

    user_id = session["user_id"]


    try:

        # ======================================
        # OWNERSHIP CHECK
        # ======================================

        file_record = get_file_by_id_and_user(
            file_id,
            user_id
        )


        if file_record is None:

            flash(
                "File not found or access denied."
            )

            return redirect(
                url_for(
                    "file_routes.my_files"
                )
            )


        encrypted_filename = (
            file_record["encrypted_filename"]
        )


        # ======================================
        # DELETE LOCAL ENCRYPTED COPY
        # ======================================

        encrypted_path = os.path.join(
            ENCRYPTED_FOLDER,
            encrypted_filename
        )


        if os.path.exists(
            encrypted_path
        ):

            os.remove(
                encrypted_path
            )


        # ======================================
        # DELETE CLOUD COPY
        # ======================================

        cloud_delete_file(
            encrypted_filename
        )


        # ======================================
        # RECORD DELETE
        # ======================================

        add_transfer(
            user_id=user_id,
            file_id=file_id,
            action="DELETE",
            status="SUCCESS"
        )


        # ======================================
        # DELETE DATABASE RECORD
        # ======================================

        delete_file(
            file_id
        )


        print()
        print(
            "File deleted."
        )


        print(
            "User ID:",
            user_id
        )


        print(
            "File ID:",
            file_id
        )


        flash(
            "Encrypted file permanently deleted."
        )


    except Exception as error:

        print(
            "DELETE ERROR:",
            str(error)
        )


        flash(
            "File deletion failed."
        )


    return redirect(
        url_for(
            "file_routes.my_files"
        )
    )