import sqlite3
from datetime import datetime


# ==========================================
# DATABASE PATH
# ==========================================

DATABASE_PATH = "database/secure_data.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()


    # ======================================
    # USERS TABLE
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ======================================
    # ADD ROLE COLUMN IF MISSING
    # ======================================

    cursor.execute("""
        PRAGMA table_info(users)
    """)

    user_columns = cursor.fetchall()

    column_names = [
        column["name"]
        for column in user_columns
    ]

    if "role" not in column_names:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN role TEXT
            DEFAULT 'user'
        """)

        print(
            "role column added successfully."
        )

    else:

        print(
            "role column already exists."
        )


    # ======================================
    # FILES TABLE
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            original_filename TEXT NOT NULL,

            encrypted_filename TEXT NOT NULL,

            file_size INTEGER NOT NULL,

            pseudo_key TEXT NOT NULL,

            status TEXT NOT NULL,

            uploaded_at TEXT NOT NULL,

            user_id INTEGER,

            FOREIGN KEY (user_id)
                REFERENCES users(id)

        )
    """)


    # ======================================
    # TRANSFERS TABLE
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transfers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            file_id INTEGER,

            action TEXT NOT NULL,

            status TEXT NOT NULL,

            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id),

            FOREIGN KEY (file_id)
                REFERENCES files(id)

        )
    """)


    # ======================================
    # SECURITY AUDIT LOG TABLE
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_audit_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            action TEXT NOT NULL,

            description TEXT,

            status TEXT NOT NULL,

            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)

        )
    """)


    connection.commit()

    connection.close()


# ==========================================
# ADD USER ID COLUMN TO EXISTING DATABASE
# ==========================================

def add_user_id_column():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        PRAGMA table_info(files)
    """)

    columns = cursor.fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    if "user_id" not in column_names:

        cursor.execute("""
            ALTER TABLE files
            ADD COLUMN user_id INTEGER
        """)

        connection.commit()

        print(
            "user_id column added successfully."
        )

    else:

        print(
            "user_id column already exists."
        )

    connection.close()


def create_user(
    username,
    password_hash
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (
                username,
                password_hash,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            username,
            password_hash,
            "user",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ))

        connection.commit()

        user_id = cursor.lastrowid

        return user_id

    except Exception as error:

        print(
            "CREATE USER ERROR:",
            error
        )

        connection.rollback()

        return None

    finally:

        connection.close()


# ==========================================
# CREATE INITIAL ADMIN FROM ENVIRONMENT
# ==========================================

def create_initial_admin():

    import os

    admin_username = os.environ.get(
        "ADMIN_USERNAME"
    )

    admin_password = os.environ.get(
        "ADMIN_PASSWORD"
    )

    if not admin_username or not admin_password:

        print(
            "ADMIN environment variables not configured."
        )

        return


    connection = get_connection()

    cursor = connection.cursor()

    try:

        # Check whether admin already exists

        cursor.execute("""
            SELECT id
            FROM users
            WHERE username = ?
        """, (
            admin_username,
        ))

        existing_admin = cursor.fetchone()


        if existing_admin:

            cursor.execute("""
                UPDATE users
                SET role = 'admin'
                WHERE id = ?
            """, (
                existing_admin["id"],
            ))

            connection.commit()

            print(
                "Admin account already exists."
            )

            return


        # Create admin account

        from werkzeug.security import (
            generate_password_hash
        )

        password_hash = (
            generate_password_hash(
                admin_password
            )
        )


        cursor.execute("""
            INSERT INTO users (
                username,
                password_hash,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            admin_username,
            password_hash,
            "admin",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ))


        connection.commit()

        print(
            "Initial admin account created."
        )


    except Exception as error:

        connection.rollback()

        print(
            "ADMIN CREATION ERROR:",
            error
        )

    finally:

        connection.close()
# ==========================================
# GET USER BY USERNAME
# ==========================================

def get_user_by_username(
    username
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (
        username,
    ))

    user = cursor.fetchone()

    connection.close()

    return user


# ==========================================
# ADD FILE
# ==========================================

def add_file(
    original_filename,
    encrypted_filename,
    file_size,
    pseudo_key,
    user_id,
    status="Encrypted"
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO files (
            original_filename,
            encrypted_filename,
            file_size,
            pseudo_key,
            status,
            uploaded_at,
            user_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        original_filename,
        encrypted_filename,
        file_size,
        pseudo_key,
        status,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        user_id
    ))

    connection.commit()

    file_id = cursor.lastrowid

    connection.close()

    return file_id


# ==========================================
# GET ALL FILES
# ==========================================

def get_all_files():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM files
        ORDER BY uploaded_at DESC
    """)

    files = cursor.fetchall()

    connection.close()

    return files


# ==========================================
# GET FILE BY ID
# ==========================================

def get_file_by_id(
    file_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM files
        WHERE id = ?
    """, (
        file_id,
    ))

    file = cursor.fetchone()

    connection.close()

    return file


# ==========================================
# GET FILE BY ID + USER
# ==========================================

def get_file_by_id_and_user(
    file_id,
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM files
        WHERE id = ?
        AND user_id = ?
    """, (
        file_id,
        user_id
    ))

    file = cursor.fetchone()

    connection.close()

    return file


# ==========================================
# GET FILES BY USER
# ==========================================

def get_files_by_user(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM files
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
    """, (
        user_id,
    ))

    files = cursor.fetchall()

    connection.close()

    return files


# ==========================================
# TOTAL FILE COUNT
# ==========================================

def get_file_count():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM files
    """)

    result = cursor.fetchone()

    connection.close()

    return result["count"]


# ==========================================
# ENCRYPTED FILE COUNT
# ==========================================

def get_encrypted_file_count():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM files
        WHERE status = 'Encrypted'
    """)

    result = cursor.fetchone()

    connection.close()

    return result["count"]


# ==========================================
# USER FILE COUNT
# ==========================================

def get_user_file_count(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM files
        WHERE user_id = ?
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    return result["count"]


# ==========================================
# USER ENCRYPTED FILE COUNT
# ==========================================

def get_user_encrypted_file_count(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM files
        WHERE user_id = ?
        AND status = 'Encrypted'
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    return result["count"]


# ==========================================
# USER TOTAL STORAGE
# ==========================================

def get_user_total_storage(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(
            SUM(file_size),
            0
        ) AS total_size
        FROM files
        WHERE user_id = ?
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    return result["total_size"]


# ==========================================
# USER STORAGE SIZE
# ==========================================

def get_user_storage_size(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(
            SUM(file_size),
            0
        ) AS total_size
        FROM files
        WHERE user_id = ?
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    return result["total_size"]


# ==========================================
# USER CLOUD FILE COUNT
# ==========================================

def get_user_cloud_file_count(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM files
        WHERE user_id = ?
        AND status = 'Encrypted'
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    return result["count"]


# ==========================================
# USER SECURE TRANSFER COUNT
# ==========================================

def get_user_secure_transfer_count(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM transfers
        WHERE user_id = ?
        AND status = 'SUCCESS'
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    return result["count"]


# ==========================================
# ADD TRANSFER
# ==========================================

def add_transfer(
    user_id,
    file_id,
    action,
    status="SUCCESS"
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transfers (
            user_id,
            file_id,
            action,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        file_id,
        action,
        status,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    connection.commit()

    connection.close()


# ==========================================
# GET USER TRANSFER ACTIVITY
# ==========================================

def get_user_transfer_activity(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            DATE(created_at) AS transfer_date,
            COUNT(*) AS transfer_count
        FROM transfers
        WHERE user_id = ?
        AND status = 'SUCCESS'
        GROUP BY DATE(created_at)
        ORDER BY transfer_date ASC
    """, (
        user_id,
    ))

    activity = cursor.fetchall()

    connection.close()

    return activity


# ==========================================
# GET RECENT TRANSFERS
# ==========================================

def get_recent_transfers(
    user_id,
    limit=10
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            transfers.id,
            transfers.user_id,
            transfers.file_id,
            transfers.action,
            transfers.status,
            transfers.created_at,
            files.original_filename
        FROM transfers
        LEFT JOIN files
            ON transfers.file_id = files.id
        WHERE transfers.user_id = ?
        ORDER BY transfers.created_at DESC
        LIMIT ?
    """, (
        user_id,
        limit
    ))

    transfers = cursor.fetchall()

    connection.close()

    return transfers


# ==========================================
# DELETE FILE
# ==========================================

def delete_file(
    file_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM files
        WHERE id = ?
    """, (
        file_id,
    ))

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted


# ==========================================
# GET ALL TRANSFERS BY USER
# ==========================================

def get_all_transfers_by_user(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            transfers.id,
            transfers.user_id,
            transfers.file_id,
            transfers.action,
            transfers.status,
            transfers.created_at,
            files.original_filename
        FROM transfers
        LEFT JOIN files
            ON transfers.file_id = files.id
        WHERE transfers.user_id = ?
        ORDER BY transfers.created_at DESC
    """, (
        user_id,
    ))

    transfers = cursor.fetchall()

    connection.close()

    return transfers


# ==========================================
# SECURITY SCORE
# ==========================================

def get_security_score(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    score = 0

    checks = {

        "authentication": False,

        "file_ownership": False,

        "encryption": False,

        "transfer_logging": False

    }

    try:

        # ==================================
        # AUTHENTICATION
        # ==================================

        cursor.execute("""
            SELECT id
            FROM users
            WHERE id = ?
        """, (
            user_id,
        ))

        user = cursor.fetchone()

        if user:

            checks[
                "authentication"
            ] = True


        # ==================================
        # FILE OWNERSHIP
        # ==================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM files
            WHERE user_id = ?
        """, (
            user_id,
        ))

        file_count = (
            cursor.fetchone()[0]
        )

        if file_count >= 0:

            checks[
                "file_ownership"
            ] = True


        # ==================================
        # ENCRYPTION
        # ==================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM files
            WHERE user_id = ?
            AND status = 'Encrypted'
        """, (
            user_id,
        ))

        encrypted_count = (
            cursor.fetchone()[0]
        )

        if (
            file_count == 0
            or encrypted_count == file_count
        ):

            checks[
                "encryption"
            ] = True


        # ==================================
        # TRANSFER LOGGING
        # ==================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM transfers
            WHERE user_id = ?
        """, (
            user_id,
        ))

        transfer_count = (
            cursor.fetchone()[0]
        )

        if transfer_count >= 0:

            checks[
                "transfer_logging"
            ] = True


        # ==================================
        # CALCULATE SCORE
        # ==================================

        passed_checks = sum(
            1
            for value in checks.values()
            if value
        )

        score = int(
            (
                passed_checks /
                len(checks)
            ) * 100
        )

        return score, checks

    finally:

        connection.close()


# ==========================================
# SECURITY AUDIT LOG
# ==========================================

def add_security_audit_log(
    user_id,
    action,
    description,
    status="SUCCESS"
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO security_audit_logs (
            user_id,
            action,
            description,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        action,
        description,
        status,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    connection.commit()

    connection.close()


# ==========================================
# GET SECURITY AUDIT LOGS
# ==========================================

def get_security_audit_logs(user_id, limit=100):

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            action,
            description,
            status,
            created_at
        FROM security_audit_logs
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            user_id,
            limit
        )
    )

    logs = cursor.fetchall()

    conn.close()

    return logs
# ==========================================
# USER TRANSFER COUNT
# ==========================================

def get_user_transfer_count(
    user_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM transfers
        WHERE user_id = ?
        AND status = 'SUCCESS'
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    return result["count"]
# ==========================================
# GET ALL USERS - ADMIN
# ==========================================

def get_all_users():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            created_at
        FROM users
        ORDER BY id ASC
    """)

    users = cursor.fetchall()

    connection.close()

    return users


# ==========================================
# GET ALL SECURITY AUDIT LOGS - ADMIN
# ==========================================

def get_all_security_audit_logs(limit=200):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            security_audit_logs.id,
            security_audit_logs.user_id,
            users.username,
            security_audit_logs.action,
            security_audit_logs.description,
            security_audit_logs.status,
            security_audit_logs.created_at
        FROM security_audit_logs
        LEFT JOIN users
            ON security_audit_logs.user_id = users.id
        ORDER BY security_audit_logs.id DESC
        LIMIT ?
    """, (limit,))

    logs = cursor.fetchall()

    connection.close()

    return logs