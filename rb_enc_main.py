import socket 
import cv2
import numpy as np
import struct
import time
import secrets
import argparse
import sys
import os
import subprocess

Server_IP = '10.239.159.182'
Server_Port = 8000

avg_cpu_cycles = []
bcmticks_process = subprocess.Popen(["./first_cycles"])
time.sleep(10)
bcmticks_process.terminate() 
os.system(f"kill -9 {bcmticks_process.pid}")

if bcmticks_process.poll() is None:
    print("Process is still running. Lets terminate")
else:
	print("The initial calculation of average clock cycles for 10 seconds is done.")

with open ('output.txt', 'r') as file:
    lines = file.readlines()
for line in lines:
    line = line.strip()
    avg_cpu_cycles.append(int(line))

avg_cpu_cycles = avg_cpu_cycles[1:]
avg_cpu_cycles = sum(avg_cpu_cycles)/len(avg_cpu_cycles)

os.remove('output.txt')

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
            print("------------------------------------------------")
            print("Using Grain-128a for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(128)
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
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
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "MB")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')                   
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

        elif args.algorithm == "mickey":
            sys.path.append('LW_Ciphers/Mickey-v2')
            from cMickey_main import c_mickey_encrypt_file
            print("------------------------------------------------")
            print("Using Mickey for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(80)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)
            
            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex.encode())

                # Encrypt the frame
                encrypted_bytes, enc_time, enc_throughput, enc_ram = c_mickey_encrypt_file(frame_bytes, key)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    print("\n------------------------------------------------")
                    print("A discreet time of 60 seconds has passed.")
                    print("\nEncryption Metrics for 60 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "MB")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

        elif args.algorithm == "trivium":
            sys.path.append('LW_Ciphers/Trivium')
            from cTRivium_main import c_trivium_encrypt_file
            print("------------------------------------------------")
            print("Using Trivium for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(80)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex)
                # Encrypt the frame
                encrypted_bytes, enc_time, enc_throughput, enc_ram = c_trivium_encrypt_file(frame_bytes, key)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "MB")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

        elif args.algorithm == "salsa":
            sys.path.append('LW_Ciphers/Salsa')
            from cSalsa_main import c_salsa_encrypt_file
            print("------------------------------------------------")
            print("Using Salsa for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(128)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex.encode())
                # Encrypt the frame
                encrypted_bytes, enc_time, enc_throughput, enc_ram = c_salsa_encrypt_file(frame_bytes, key)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "MB")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

        elif args.algorithm == "sosemanuk":

            sys.path.append('LW_Ciphers/Sosemanuk')
            from cSosemanuk_main import c_sosemanuk_encrypt_file
            print("------------------------------------------------")
            print("Using Sosemanuk for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(128)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)
            
            key = b'\x0fB\xe8:Se\x9d~\x86\x1fy\\\x88#0\xd9'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex.encode())

                #with open('bird.jpeg', 'rb') as file:
                #    plaintext = file.read()
                    

                # Encrypt the frame
                encrypted_bytes, enc_time, enc_throughput, enc_ram = c_sosemanuk_encrypt_file(frame_bytes, key)
                #print(encrypted_bytes)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "MB")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()


    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Closing the connection and releasing the camera.")
        os.remove('output.txt')
        camera.release()
        connection.close()
        client_socket.close()
        sys.exit()
    finally:
        connection.close()
        client_socket.close()

if __name__ == "__main__":
    random_key_bits, random_bytes = generate_random_key(128)
    print(random_bytes)
    main()
