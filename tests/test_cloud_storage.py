import os

from cloud_storage.local_storage import (
    upload_file,
    download_file,
    file_exists,
    list_files
)


print("Testing Cloud Storage Layer")


encrypted_folder = "encrypted"


files = os.listdir(
    encrypted_folder
)


if not files:

    print(
        "ERROR: No encrypted files found."
    )

    print(
        "Upload a file first."
    )

    raise SystemExit


encrypted_filename = files[0]

local_path = os.path.join(
    encrypted_folder,
    encrypted_filename
)


print()
print("Local encrypted file:")
print(local_path)


print()
print("Uploading to cloud storage...")


cloud_path = upload_file(
    local_path,
    encrypted_filename
)


print()
print("Cloud storage path:")
print(cloud_path)


print()
print("Checking cloud file...")


if file_exists(encrypted_filename):

    print(
        "Cloud file exists: YES"
    )

else:

    print(
        "Cloud file exists: NO"
    )


print()
print("Cloud files:")

for filename in list_files():

    print(
        " -",
        filename
    )


print()
print(
    "SUCCESS: Cloud storage layer works!"
)