import socket 
import cv2
import numpy as np
import struct
import time
import secrets
import argparse
import sys

Server_IP = '10.239.148.76'
Server_Port = 8000

def generate_random_key(num_bits):
    # Generate a random byte array of appropriate length
    num_bytes = (num_bits + 7) // 8  # Round up to the nearest whole number of bytes
    random_bytes = secrets.token_bytes(num_bytes)
    # random_integer = int.from_bytes(random_bytes, byteorder='big')
    
    # Convert the byte array to a bit string
    random_key_bits = ''.join(format(byte, '08b') for byte in random_bytes)
    
    # Trim any excess bits
    random_key_bits = random_key_bits[:num_bits]
    
    return random_key_bits, random_bytes


def main():
    parser = argparse.ArgumentParser(description="Encrypt video streams using different cryptographic algorithms")
    parser.add_argument("algorithm", help="The cryptographic algorithm to use", choices=["grain-128a", "mickey", "trivium", "salsa", "sosemanuk"])

    args = parser.parse_args()

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((Server_IP, Server_Port))

    connection = client_socket.makefile('wb')
    try:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Width of the frames in the video stream.
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)   # Height of the frames in the video stream.
        camera.set(cv2.CAP_PROP_FPS, 30)   # Frame rate.
        time.sleep(2) 

        if args.algorithm == "grain-128a":
            sys.path.append('LW_Ciphers/Grain-128a')
            from cGrain128a_main import c_grain128_encrypt_file
            print("Using Grain-128a for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(128)
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex.encode())
                # Encrypt the frame
                encrypted_bytes, enc_time, enc_throughput, enc_ram = c_grain128_encrypt_file(frame_bytes, key)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)

                if elapsed_time >= 10:
                    print("Frames encrypted in 10 seconds: ", frame_count)
                    frame_count = 0

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "MB")

                    throughput_list = []
                    ram_list = []
                    start_time = time.time()

        elif args.algorithm == "mickey":
            sys.path.append('LW_Ciphers/Mickey-v2')
            from cMickey_main import c_mickey_encrypt_file
            print("Using Mickey for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(80)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)
            
            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            frame_count = 0
            start_time = time.time()
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex.encode())

                # Encrypt the frame
                encrypted_bytes, _, _ = c_mickey_encrypt_file(frame_bytes, key)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time

                if elapsed_time >= 60:
                    print("Frames encrypted in 60 seconds: ", frame_count)
                    frame_count = 0
                    start_time = time.time()

        elif args.algorithm == "trivium":
            sys.path.append('LW_Ciphers/Trivium')
            from cTRivium_main import c_trivium_encrypt_file
            print("Using Trivium for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(80)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            frame_count = 0
            start_time = time.time()
            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex)
                # Encrypt the frame
                encrypted_bytes, _, _ = c_trivium_encrypt_file(frame_bytes, key)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1

                elapsed_time = time.time() - start_time
                if elapsed_time >= 60:
                    print("Frames encrypted in 60 seconds: ", frame_count)
                    frame_count = 0
                    start_time = time.time()

        elif args.algorithm == "salsa":
            sys.path.append('LW_Ciphers/Salsa')
            from cSalsa_main import c_salsa_encrypt_file
            print("Using Salsa for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(128)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            frame_count = 0
            start_time = time.time()
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex.encode())
                # Encrypt the frame
                encrypted_bytes, _, _ = c_salsa_encrypt_file(frame_bytes, key)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time

                if elapsed_time >= 60:
                    print("Frames encrypted in 60 seconds: ", frame_count)
                    frame_count = 0
                    start_time = time.time()

        elif args.algorithm == "sosemanuk":

            sys.path.append('LW_Ciphers/Sosemanuk')
            from cSosemanuk_main import c_sosemanuk_encrypt_file
            print("Using Sosemanuk for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(128)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)
            
            key = b'\x0fB\xe8:Se\x9d~\x86\x1fy\\\x88#0\xd9'
            frame_count = 0
            start_time = time.time()
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex.encode())

                #with open('bird.jpeg', 'rb') as file:
                #    plaintext = file.read()
                    

                # Encrypt the frame
                encrypted_bytes, _, _ = c_sosemanuk_encrypt_file(frame_bytes, key)
                #print(encrypted_bytes)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time

                if elapsed_time >= 60:
                    print("Frames encrypted in 60 seconds: ", frame_count)
                    frame_count = 0
                    start_time = time.time()

    finally:
        connection.close()
        client_socket.close()

if __name__ == "__main__":
    random_key_bits, random_bytes = generate_random_key(128)
    print(random_bytes)
    main()
