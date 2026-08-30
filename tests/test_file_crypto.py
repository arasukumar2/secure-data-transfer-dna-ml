import os

from crypto.file_crypto import (
    encrypt_file,
    decrypt_file
)


INPUT_FILE = "tests/sample.txt"
ENCRYPTED_FILE = "tests/sample.encrypted"
DECRYPTED_FILE = "tests/sample_recovered.txt"


print("========================================")
print("       FILE ENCRYPTION TEST")
print("========================================")

print("\nOriginal file:")
print(INPUT_FILE)

print("\nEncrypting file...")

pseudo_key = encrypt_file(
    INPUT_FILE,
    ENCRYPTED_FILE
)

print("Encryption successful!")

print("\nEncrypted file:")
print(ENCRYPTED_FILE)

print("\nPseudo-key:")
print(pseudo_key)

print("\nDecrypting file...")

decrypt_file(
    ENCRYPTED_FILE,
    DECRYPTED_FILE,
    pseudo_key
)

print("Decryption successful!")

print("\nRecovered file:")
print(DECRYPTED_FILE)


with open(INPUT_FILE, "rb") as file:
    original_data = file.read()

with open(DECRYPTED_FILE, "rb") as file:
    recovered_data = file.read()


if original_data == recovered_data:

    print("\n========================================")
    print("SUCCESS: File encryption/decryption works!")
    print("Original and recovered files are identical.")
    print("========================================")

else:

    print("\nFAILED: Files are different!")