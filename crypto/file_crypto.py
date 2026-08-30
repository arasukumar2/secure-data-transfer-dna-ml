import os

from crypto.secure_crypto import encrypt_data, decrypt_data


def encrypt_file(input_path, output_path):
    """
    Read a file, encrypt its contents, and save
    the encrypted data to a new file.
    """

    with open(input_path, "rb") as file:
        original_data = file.read()

    encrypted_data, pseudo_key = encrypt_data(original_data)

    with open(output_path, "wb") as file:
        file.write(encrypted_data)

    return pseudo_key


def decrypt_file(encrypted_path, output_path, pseudo_key):
    """
    Read an encrypted file, decrypt its contents,
    and restore the original file.
    """

    with open(encrypted_path, "rb") as file:
        encrypted_data = file.read()

    original_data = decrypt_data(
        encrypted_data,
        pseudo_key
    )

    with open(output_path, "wb") as file:
        file.write(original_data)


def file_exists(path):
    return os.path.exists(path)

def decrypt_encrypted_file(
    encrypted_path,
    output_path,
    pseudo_key
):
    """
    Decrypt an encrypted file and restore
    the original file.
    """

    with open(encrypted_path, "rb") as file:
        encrypted_data = file.read()

    original_data = decrypt_data(
        encrypted_data,
        pseudo_key
    )

    with open(output_path, "wb") as file:
        file.write(original_data)