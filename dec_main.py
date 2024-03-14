import socket
import sys
import cv2
import numpy as np
import socket 
import time
import struct
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Decrypt video streams using different cryptographic algorithms")
    parser.add_argument("algorithm", help="The cryptographic algorithm to use", choices=["grain-128a", "mickey", "trivium", "salsa", "sosemanuk"])

    args = parser.parse_args()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(0)

    connection, address = server_socket.accept()
    connection_io = connection.makefile('rb')

    try:
        if args.algorithm == "grain-128a":
            sys.path.append('LW_Ciphers/Grain-128a')
            from cGrain128a_main import c_grain128_decrypt_file
            print("Using Grain-128a for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            while True:
                chunk = connection_io.read(4)
                if not chunk:
                    break

                # print("Chunk: ", chunk)
                chunk = struct.unpack('<L', chunk)[0]
                # print("Chunk: ", chunk)
                ciphertext_bytes = connection_io.read(int(chunk))
                # print("Ciphertext bytes: ", ciphertext_bytes)

                decrypted_output, _, _, _ = c_grain128_decrypt_file(ciphertext_bytes, key)
                #print("Decrypted output: ", decrypted_output)
                # Deserialize the frame
                #hex_image = decrypted_output.decode()[2:]
                #image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        elif args.algorithm == "mickey":
            sys.path.append('LW_Ciphers/Mickey-v2')
            from cMickey_main import c_mickey_decrypt_file
            print("Using Mickey for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            while True:
                chunk = connection_io.read(4)
                if not chunk:
                    break
                chunk = struct.unpack('<L', chunk)[0]
                ciphertext_bytes = connection_io.read(int(chunk))
                decrypted_output, _, _ = c_mickey_decrypt_file(ciphertext_bytes, key)
                # Deserialize the frame
                #hex_image = decrypted_output.decode()[2:]
                #image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        elif args.algorithm == "trivium":
            sys.path.append('LW_Ciphers/Trivium')
            from cTRivium_main import c_trivium_decrypt_file
            print("Using Trivium for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            while True:
                chunk = connection_io.read(4)
                if not chunk:
                    break
                chunk = struct.unpack('<L', chunk)[0]
                ciphertext_bytes = connection_io.read(int(chunk))
                decrypted_output, _, _, = c_trivium_decrypt_file(ciphertext_bytes, key)
                # Deserialize the frame
                # hex_image = decrypted_output[2:]
                # image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


        elif args.algorithm == "salsa":
            sys.path.append('LW_Ciphers/Salsa')
            from cSalsa_main import c_salsa_decrypt_file
            print("Using Salsa for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            while True:
                chunk = connection_io.read(4)
                chunk = struct.unpack('<L', chunk)[0]
                ciphertext_bytes = connection_io.read(int(chunk))
                decrypted_output, _, _, =c_salsa_decrypt_file(ciphertext_bytes, key)
                # Deserialize the frame
                # hex_image = decrypted_output.decode()[2:]
                # image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        elif args.algorithm == "sosemanuk":
            sys.path.append('LW_Ciphers/Sosemanuk')
            from cSosemanuk_main import c_sosemanuk_decrypt_file
            print("Using Sosemanuk for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x0fB\xe8:Se\x9d~\x86\x1fy\\\x88#0\xd9'
            while True:
                chunk = connection_io.read(4)
                chunk = struct.unpack('<L', chunk)[0]
                ciphertext_bytes = connection_io.read(chunk)
                print("Ciphertext_bytes: ", chunk)
                decrypted_output, _, _ = c_sosemanuk_decrypt_file(ciphertext_bytes, key)
                print("Decrypted Output: ", decrypted_output[:4])
                # Deserialize the frame
                # hex_image = decrypted_output.decode()[2:]
                # image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        connection.close()
        server_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()