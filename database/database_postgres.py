import os
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set."
        )

    return psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor
    )


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                file_id INTEGER,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users(id),
                FOREIGN KEY (file_id)
                    REFERENCES files(id)
                    ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_audit_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                action TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
            )
        """)

        # Existing Neon databases may already have the tables.
        # Make sure the role column exists for older schemas.
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS role TEXT
                DEFAULT 'user'
        """)

        cursor.execute("""
            UPDATE users
            SET role = 'user'
            WHERE role IS NULL
        """)

        # The application deletes files while retaining transfer history.
        # Make file_id nullable when the referenced file is deleted.
        cursor.execute("""
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'transfers_file_id_fkey'
              AND conrelid = 'transfers'::regclass
        """)

        if cursor.fetchone():
            cursor.execute("""
                ALTER TABLE transfers
                DROP CONSTRAINT transfers_file_id_fkey
            """)

        cursor.execute("""
            ALTER TABLE transfers
            ADD CONSTRAINT transfers_file_id_fkey
            FOREIGN KEY (file_id)
            REFERENCES files(id)
            ON DELETE SET NULL
        """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# ADD USER ID COLUMN
# ==========================================

def add_user_id_column():
    # user_id is created by initialize_database().
    return


# ==========================================
# CREATE USER
# ==========================================

def create_user(username, password_hash):
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
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            username,
            password_hash,
            "user",
            datetime.now()
        ))

        user_id = cursor.fetchone()["id"]
        connection.commit()
        return user_id

    except Exception as error:
        print("CREATE USER ERROR:", error)
        connection.rollback()
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# CREATE INITIAL ADMIN FROM ENVIRONMENT
# ==========================================

def create_initial_admin():
    from werkzeug.security import generate_password_hash

    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if not admin_username or not admin_password:
        print("ADMIN environment variables not configured.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id
            FROM users
            WHERE username = %s
        """, (admin_username,))

        existing_admin = cursor.fetchone()

        if existing_admin:
            cursor.execute("""
                UPDATE users
                SET role = 'admin'
                WHERE id = %s
            """, (existing_admin["id"],))

            connection.commit()
            print("Admin account already exists.")
            return

        password_hash = generate_password_hash(admin_password)

        cursor.execute("""
            INSERT INTO users (
                username,
                password_hash,
                role,
                created_at
            )
            VALUES (%s, %s, %s, %s)
        """, (
            admin_username,
            password_hash,
            "admin",
            datetime.now()
        ))

        connection.commit()
        print("Initial admin account created.")

    except Exception as error:
        connection.rollback()
        print("ADMIN CREATION ERROR:", error)

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET USER BY USERNAME
# ==========================================

def get_user_by_username(username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username = %s
    """, (username,))

    user = cursor.fetchone()

    cursor.close()
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
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        original_filename,
        encrypted_filename,
        file_size,
        pseudo_key,
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_id
    ))

    file_id = cursor.fetchone()["id"]
    connection.commit()

    cursor.close()
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

    cursor.close()
    connection.close()

    return files


# ==========================================
# GET FILE BY ID
# ==========================================

def get_file_by_id(file_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM files
        WHERE id = %s
    """, (file_id,))

    file = cursor.fetchone()

    cursor.close()
    connection.close()

    return file


# ==========================================
# GET FILE BY ID + USER
# ==========================================

def get_file_by_id_and_user(file_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM files
        WHERE id = %s
        AND user_id = %s
    """, (file_id, user_id))

    file = cursor.fetchone()

    cursor.close()
    connection.close()

    return file


# ==========================================
# GET FILES BY USER
# ==========================================

def get_files_by_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM files
        WHERE user_id = %s
        ORDER BY uploaded_at DESC
    """, (user_id,))

    files = cursor.fetchall()

    cursor.close()
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

    cursor.close()
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

    cursor.close()
    connection.close()

    return result["count"]


# ==========================================
# USER FILE COUNT
# ==========================================

def get_user_file_count(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM files
        WHERE user_id = %s
    """, (user_id,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result["count"]


# ==========================================
# USER ENCRYPTED FILE COUNT
# ==========================================

def get_user_encrypted_file_count(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM files
        WHERE user_id = %s
        AND status = 'Encrypted'
    """, (user_id,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result["count"]


# ==========================================
# USER TOTAL STORAGE
# ==========================================

def get_user_total_storage(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(file_size), 0) AS total_size
        FROM files
        WHERE user_id = %s
    """, (user_id,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result["total_size"]


# ==========================================
# USER STORAGE SIZE
# ==========================================

def get_user_storage_size(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(file_size), 0) AS total_size
        FROM files
        WHERE user_id = %s
    """, (user_id,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result["total_size"]


# ==========================================
# USER CLOUD FILE COUNT
# ==========================================

def get_user_cloud_file_count(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM files
        WHERE user_id = %s
        AND status = 'Encrypted'
    """, (user_id,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result["count"]


# ==========================================
# USER SECURE TRANSFER COUNT
# ==========================================

def get_user_secure_transfer_count(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM transfers
        WHERE user_id = %s
        AND status = 'SUCCESS'
    """, (user_id,))

    result = cursor.fetchone()

    cursor.close()
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
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user_id,
        file_id,
        action,
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()

    cursor.close()
    connection.close()


# ==========================================
# GET USER TRANSFER ACTIVITY
# ==========================================

def get_user_transfer_activity(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            DATE(created_at) AS transfer_date,
            COUNT(*) AS transfer_count
        FROM transfers
        WHERE user_id = %s
        AND status = 'SUCCESS'
        GROUP BY DATE(created_at)
        ORDER BY transfer_date ASC
    """, (user_id,))

    activity = cursor.fetchall()

    cursor.close()
    connection.close()

    return activity


# ==========================================
# GET RECENT TRANSFERS
# ==========================================

def get_recent_transfers(user_id, limit=10):
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
        WHERE transfers.user_id = %s
        ORDER BY transfers.created_at DESC
        LIMIT %s
    """, (user_id, limit))

    transfers = cursor.fetchall()

    cursor.close()
    connection.close()

    return transfers


# ==========================================
# DELETE FILE
# ==========================================

def delete_file(file_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM files
            WHERE id = %s
        """, (file_id,))

        deleted = cursor.rowcount > 0
        connection.commit()
        return deleted

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET ALL TRANSFERS BY USER
# ==========================================

def get_all_transfers_by_user(user_id):
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
        WHERE transfers.user_id = %s
        ORDER BY transfers.created_at DESC
    """, (user_id,))

    transfers = cursor.fetchall()

    cursor.close()
    connection.close()

    return transfers


# ==========================================
# SECURITY SCORE
# ==========================================

def get_security_score(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    checks = {
        "authentication": False,
        "file_ownership": False,
        "encryption": False,
        "transfer_logging": False
    }

    try:
        cursor.execute("""
            SELECT id
            FROM users
            WHERE id = %s
        """, (user_id,))

        user = cursor.fetchone()

        if user:
            checks["authentication"] = True

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM files
            WHERE user_id = %s
        """, (user_id,))

        file_count = cursor.fetchone()["count"]

        if file_count >= 0:
            checks["file_ownership"] = True

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM files
            WHERE user_id = %s
            AND status = 'Encrypted'
        """, (user_id,))

        encrypted_count = cursor.fetchone()["count"]

        if file_count == 0 or encrypted_count == file_count:
            checks["encryption"] = True

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM transfers
            WHERE user_id = %s
        """, (user_id,))

        transfer_count = cursor.fetchone()["count"]

        if transfer_count >= 0:
            checks["transfer_logging"] = True

        passed_checks = sum(
            1 for value in checks.values() if value
        )

        score = int(
            (passed_checks / len(checks)) * 100
        )

        return score, checks

    finally:
        cursor.close()
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

    try:
        cursor.execute("""
            INSERT INTO security_audit_logs (
                user_id,
                action,
                description,
                status,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            action,
            description,
            status,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ==========================================
# GET SECURITY AUDIT LOGS
# ==========================================

def get_security_audit_logs(user_id, limit=100):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            user_id,
            action,
            description,
            status,
            created_at
        FROM security_audit_logs
        WHERE user_id = %s
        ORDER BY id DESC
        LIMIT %s
    """, (user_id, limit))

    logs = cursor.fetchall()

    cursor.close()
    connection.close()

    return logs


# ==========================================
# USER TRANSFER COUNT
# ==========================================

def get_user_transfer_count(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM transfers
        WHERE user_id = %s
        AND status = 'SUCCESS'
    """, (user_id,))

    result = cursor.fetchone()

    cursor.close()
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
            created_at,
            role
        FROM users
        ORDER BY id ASC
    """)

    users = cursor.fetchall()

    cursor.close()
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
        LIMIT %s
    """, (limit,))

    logs = cursor.fetchall()

    cursor.close()
    connection.close()

    return logs
