from database.database import (
    initialize_database,
    get_all_files,
    get_file_count,
    get_encrypted_file_count
)


print("Initializing database...")

initialize_database()

print("\nTotal files:")
print(get_file_count())

print("\nEncrypted files:")
print(get_encrypted_file_count())

print("\nFile records:")

files = get_all_files()

for file in files:

    print("------------------------------")

    print("ID:", file["id"])

    print("Original:",
          file["original_filename"])

    print("Encrypted:",
          file["encrypted_filename"])

    print("Size:",
          file["file_size"], "bytes")

    print("Status:",
          file["status"])

    print("Uploaded:",
          file["uploaded_at"])
    print("User ID:", file["user_id"])
