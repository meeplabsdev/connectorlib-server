import asyncio
import binascii
import websockets
import msgpack

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes


async def send_identity_request():
    uri = "ws://localhost:3000"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            await websocket.send(msgpack.packb(["IdentityRequest", ["62eaea5762cb458c8007d6c5e652c2a7", "floridarosie"]]))

            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                if isinstance(response, bytes):
                    decoded_response = msgpack.unpackb(response, raw=False)

                    plaintext = f"{decoded_response[1][0]}62eaea5762cb458c8007d6c5e652c2a7floridarosie"
                    cipher = AES.new(b"This is the key!", AES.MODE_CBC, decoded_response[1][1].encode("utf-8"))
                    result = cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))

                    await websocket.send(msgpack.packb(["IdentityChallenge", [binascii.hexlify(result)]]))
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    if isinstance(response, bytes):
                        decoded_response = msgpack.unpackb(response, raw=False)
                        print(f"Received token: {decoded_response[1][0]}")

                        iv = get_random_bytes(AES.block_size)
                        cipher = AES.new(decoded_response[1][0].encode("utf-8"), AES.MODE_CBC, iv)
                        result = iv + cipher.encrypt(pad(msgpack.packb(["testa", ["hi"]]), AES.block_size))
                        await websocket.send(result)

            except asyncio.TimeoutError:
                print("No response received within 5 seconds")
            except msgpack.exceptions.ExtraData:
                print("Error: Invalid MessagePack data received")
            except Exception as decode_error:
                print(f"Error decoding response: {decode_error}")

    except websockets.exceptions.ConnectionRefused:
        print("Connection refused. Make sure the WebSocket server is running on localhost:3000")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(send_identity_request())
