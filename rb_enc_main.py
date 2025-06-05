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
import csv
import serial

arduino_serial = serial.Serial(port='/dev/ttyAMA0', baudrate=9600, timeout=.1)
Server_IP = '10.239.152.0'
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

def save_to_csv(algorithm, key_size, frame_enc_per_sec, avg_throughput, avg_ram, cycles_per_byte):
    headers = ["Algorithm", "Key Size", "Frames Encrypted Per Second", "Average Throughput", "Average RAM", "Cycles Per Byte"]
    enc_frames_per_sec_filename = 'Measurements/enc_frames_per_sec.csv'
    enc_throughput_filename = 'Measurements/enc_throughput.csv'
    enc_ram_filename = 'Measurements/enc_ram.csv'
    enc_cycles_per_byte_filename = 'Measurements/enc_cycles_per_byte.csv'

    update_csv_data(enc_frames_per_sec_filename, algorithm, key_size, frame_enc_per_sec)

    update_csv_data(enc_throughput_filename, algorithm, key_size, avg_throughput)

    update_csv_data(enc_ram_filename, algorithm, key_size, avg_ram)

    update_csv_data(enc_cycles_per_byte_filename, algorithm, key_size, cycles_per_byte)

def update_csv_data(filename, algorithm, key_size, value):
    if not os.path.isfile(filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Algorithm", "Key Size", "Value"])

    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        data = list(reader)
        algorithm_exists = False
        for row in data[1:]:
            if row[0] == algorithm and row[1] == str(key_size):
                algorithm_exists = True
                row.append(value)
                break   

        if not algorithm_exists:
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([algorithm, key_size, value])

        else:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Algorithm', 'Key Size', 'Value'])
                writer.writerows(data[1:])

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
    parser.add_argument("algorithm", help="The cryptographic algorithm to use", choices=["grain-128a", "grain-v1", "mickey", "trivium", "salsa", "sosemanuk"])

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
            algo_name = args.algorithm + "_enc"  # Name of the algorithm
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
            initial_start_time = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            arduino_serial.write(bytes(algo_name, 'utf-8'))
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
                elapsed_time_initial = time.time() - initial_start_time
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    arduino_serial.write(bytes("stop", 'utf-8'))
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list), 2)
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory footprint: ", avg_ram, "bytes")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    save_to_csv(args.algorithm, "128", frame_enc_per_sec, avg_throughput, avg_ram, cycles_per_byte)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')                   
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()
                
                elif elapsed_time_initial>=300:
                    print("Total time of 5 minutes has passed. Closing the connection and releasing the camera.")
                    os.remove('output.txt')
                    camera.release()
                    connection.close()
                    client_socket.close()
                    sys.exit()

        elif args.algorithm == "grain-v1":
            sys.path.append('LW_Ciphers/Grain-v1')
            from cGrain_main import c_grain_v1_encrypt_file
            algo_name = args.algorithm + "_enc"  # Name of the algorithm
            print("------------------------------------------------")
            print("Using Grain-v1 for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(80)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            frame_count = 0
            start_time = time.time()
            elapsed_time_initial = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            arduino_serial.write(bytes(algo_name, 'utf-8'))
            while True:
                ret, frame = camera.read()
                frame = cv2.resize(frame, (640, 480))
                frame_bytes = cv2.imencode('.JPEG', frame)[1].tobytes()
                #frame_hex = '0x' + ''.join(format(byte, '02x') for byte in frame_bytes)
                #hex_frames_bytes_literal = bytes(frame_hex.encode())
                # Encrypt the frame
                encrypted_bytes, enc_time, enc_throughput, enc_ram = c_grain_v1_encrypt_file(frame_bytes, key)
                # Send the encrypted frame
                connection.write(struct.pack('<L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time
                elapsed_time_initial = time.time() - start_time
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    arduino_serial.write(bytes("stop", 'utf-8'))
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "bytes")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    save_to_csv(args.algorithm, "80", frame_enc_per_sec, avg_throughput, avg_ram, cycles_per_byte)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

                elif elapsed_time_initial>=300:
                    print("Total time of 5 minutes has passed. Closing the connection and releasing the camera.")
                    os.remove('output.txt')
                    camera.release()
                    connection.close()
                    client_socket.close()
                    sys.exit()

        elif args.algorithm == "mickey":
            sys.path.append('LW_Ciphers/Mickey-v2')
            from cMickey_main import c_mickey_encrypt_file
            algo_name = args.algorithm + "_enc"  # Name of the algorithm
            print("------------------------------------------------")
            print("Using Mickey for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(80)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)
            
            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            frame_count = 0
            start_time = time.time()
            start_time_initial = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            arduino_serial.write(bytes(algo_name, 'utf-8'))
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
                elapsed_time_initial = time.time() - start_time_initial
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    arduino_serial.write(bytes("stop", 'utf-8'))
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "bytes")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    save_to_csv(args.algorithm, "80", frame_enc_per_sec, avg_throughput, avg_ram, cycles_per_byte)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

                elif elapsed_time_initial>=300:
                    print("Total time of 5 minutes has passed. Closing the connection and releasing the camera.")
                    os.remove('output.txt')
                    camera.release()
                    connection.close()
                    client_socket.close()
                    sys.exit()

        elif args.algorithm == "trivium":
            sys.path.append('LW_Ciphers/Trivium')
            from cTRivium_main import c_trivium_encrypt_file
            algo_name = args.algorithm + "_enc"  # Name of the algorithm
            print("------------------------------------------------")
            print("Using Trivium for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(80)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            frame_count = 0
            start_time = time.time()
            start_time_initial = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            arduino_serial.write(bytes(algo_name, 'utf-8'))
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
                elapsed_time_initial = time.time() - start_time_initial
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    arduino_serial.write(bytes("stop", 'utf-8'))
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "bytes")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    save_to_csv(args.algorithm, "80", frame_enc_per_sec, avg_throughput, avg_ram, cycles_per_byte)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

                elif elapsed_time_initial>=300:
                    print("Total time of 5 minutes has passed. Closing the connection and releasing the camera.")
                    os.remove('output.txt')
                    camera.release()
                    connection.close()
                    client_socket.close()
                    sys.exit()

        elif args.algorithm == "salsa":
            sys.path.append('LW_Ciphers/Salsa')
            from cSalsa_main import c_salsa_encrypt_file
            algo_name = args.algorithm + "_enc"  # Name of the algorithm
            print("------------------------------------------------")
            print("Using Salsa for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(128)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            frame_count = 0
            start_time = time.time()
            start_time_initial = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            arduino_serial.write(bytes(algo_name, 'utf-8'))
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
                elapsed_time_initial = time.time() - start_time_initial
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    arduino_serial.write(bytes("stop", 'utf-8'))
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "bytes")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    save_to_csv(args.algorithm, "128", frame_enc_per_sec, avg_throughput, avg_ram, cycles_per_byte)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

                elif elapsed_time_initial>=300:
                    print("Total time of 5 minutes has passed. Closing the connection and releasing the camera.")
                    os.remove('output.txt')
                    camera.release()
                    connection.close()
                    client_socket.close()
                    sys.exit()

        elif args.algorithm == "sosemanuk":

            sys.path.append('LW_Ciphers/Sosemanuk')
            from cSosemanuk_main import c_sosemanuk_encrypt_file
            algo_name = args.algorithm + "_enc"
            print("------------------------------------------------")
            print("Using Sosemanuk for encrypting the video stream")
            random_key_bits, random_bytes = generate_random_key(128)
            key = random_bytes
            # with open('key.txt', 'wb') as key_file:
            #     key_file.write(key)
            
            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            frame_count = 0
            start_time = time.time()
            start_time_initial = time.time()
            throughput_list = []
            ram_list = []
            cycle_count_enc = []
            total_frame_bytes = 0
            bcmticks_process = subprocess.Popen(["./first_cycles"])
            arduino_serial.write(bytes(algo_name, 'utf-8'))
            while True:  
                # arduino_serial.write(bytes(algo_name, 'utf-8'))
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
                connection.write(struct.pack('>L', len(encrypted_bytes)))
                connection.flush()
                connection.write(encrypted_bytes)
                connection.flush()

                frame_count += 1
                elapsed_time = time.time() - start_time
                elapsed_time_initial = time.time() - start_time_initial
                throughput_list.append(enc_throughput)
                ram_list.append(enc_ram)
                total_frame_bytes += len(frame_bytes)

                if elapsed_time >= 10:
                    bcmticks_process.terminate()
                    os.system(f"kill -9 {bcmticks_process.pid}")
                    arduino_serial.write(bytes("stop", 'utf-8'))
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed.")
                    print("\nEncryption Metrics for 10 seconds: ")
                    frame_enc_per_sec = round(frame_count / elapsed_time, 2)
                    print("Frames encrypted per second: ", frame_enc_per_sec)

                    avg_throughput = round(sum(throughput_list) / len(throughput_list))
                    print("Average throughput: ", avg_throughput, "Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print("Average memory usage: ", avg_ram, "bytes")

                    with open ('output.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        cycle_count_enc.append(int(line))

                    cycle_count_enc = [x - int(avg_cpu_cycles) for x in cycle_count_enc]
                    cycles_per_byte = sum(cycle_count_enc) / total_frame_bytes
                    cycles_per_byte = int(cycles_per_byte)

                    print("Average CPU cycles per byte: ", cycles_per_byte, "CpB")

                    save_to_csv(args.algorithm, "128", frame_enc_per_sec, avg_throughput, avg_ram, cycles_per_byte)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    cycle_count_enc = []
                    total_frame_bytes = 0
                    os.remove('output.txt')
                    bcmticks_process = subprocess.Popen(["./first_cycles"])
                    start_time = time.time()

                elif elapsed_time_initial>=300:
                    print("Total time of 5 minutes has passed. Closing the connection and releasing the camera.")
                    os.remove('output.txt')
                    camera.release()
                    connection.close()
                    client_socket.close()
                    sys.exit()


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
    # random_key_bits, random_bytes = generate_random_key(128)
    # print(random_bytes)
    main()
