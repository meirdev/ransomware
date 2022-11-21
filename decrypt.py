from common import *
from config import *

AES_KEY = b"""<<<AES_KEY>>>"""
AES_IV = b"""<<<AES_IV>>>"""


def main() -> None:
    cipher = create_cipher(AES_KEY, AES_IV)

    for file in get_dirs_and_files(
        __ROOT_DIRS__, __EXCLUDE_DIRS__, [__FILE_ADDITIONAL_EXT__], __INTEVAL__
    ):
        if os.path.isdir(file):
            delete_readme(file, __README_FILE__)
        else:
            decrypt_file(file, cipher, __AES_KEY_SIZE__, __FILE_ADDITIONAL_EXT__)


if __name__ == "__main__":
    main()
