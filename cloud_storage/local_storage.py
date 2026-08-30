import os
import shutil


CLOUD_FOLDER = "cloud_storage/data"


os.makedirs(
    CLOUD_FOLDER,
    exist_ok=True
)


def upload_file(
    local_file_path,
    cloud_filename
):

    destination = os.path.join(
        CLOUD_FOLDER,
        cloud_filename
    )

    shutil.copy2(
        local_file_path,
        destination
    )

    return destination


def download_file(
    cloud_filename,
    local_file_path
):

    source = os.path.join(
        CLOUD_FOLDER,
        cloud_filename
    )

    if not os.path.exists(source):

        raise FileNotFoundError(
            "Encrypted cloud file not found."
        )

    os.makedirs(
        os.path.dirname(local_file_path),
        exist_ok=True
    )

    shutil.copy2(
        source,
        local_file_path
    )

    return local_file_path


def delete_file(
    cloud_filename
):

    cloud_path = os.path.join(
        CLOUD_FOLDER,
        cloud_filename
    )

    if os.path.exists(cloud_path):

        os.remove(cloud_path)

        return True

    return False


def file_exists(
    cloud_filename
):

    cloud_path = os.path.join(
        CLOUD_FOLDER,
        cloud_filename
    )

    return os.path.exists(
        cloud_path
    )


def list_files():

    return os.listdir(
        CLOUD_FOLDER
    )