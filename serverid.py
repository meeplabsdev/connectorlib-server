import hashlib
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


def generate_server_id() -> str:
    sha1 = hashlib.sha1()
    sha1.update("".encode("iso-8859-1"))
    sha1.update(get_random_bytes(16))
    sha1.update(RSA.generate(2048).publickey().export_key("DER"))
    digest = sha1.digest()

    return int.from_bytes(digest, byteorder="big", signed=False).to_bytes(20, byteorder="big").hex()


server_id = generate_server_id()
print("serverId (hex):", server_id)
