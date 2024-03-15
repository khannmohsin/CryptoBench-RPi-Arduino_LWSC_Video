import socket
import sys
import cv2
import numpy as np
import socket 
import time
import struct
import argparse
import sys
import os
import csv

def save_to_csv(algorithm, key_size, frame_dec_per_sec, avg_throughput, avg_ram):
    headers = ["Algorithm", "Key Size", "Frames Decrypted Per Second", "Average Throughput", "Average RAM"]
    enc_frames_per_sec_filename = 'Measurements/enc_frames_per_sec.csv'
    enc_throughput_filename = 'Measurements/enc_throughput.csv'
    enc_ram_filename = 'Measurements/enc_ram.csv'

    update_csv_data(enc_frames_per_sec_filename, algorithm, key_size, frame_dec_per_sec)

    update_csv_data(enc_throughput_filename, algorithm, key_size, avg_throughput)

    update_csv_data(enc_ram_filename, algorithm, key_size, avg_ram)


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
            print("------------------------------------------------")
            print("Using Grain-128a for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            total_frame_bytes = 0
            while True:
                chunk = connection_io.read(4)
                if not chunk:
                    break

                # print("Chunk: ", chunk)
                chunk = struct.unpack('<L', chunk)[0]
                # print("Chunk: ", chunk)
                ciphertext_bytes = connection_io.read(int(chunk))
                # print("Ciphertext bytes: ", ciphertext_bytes)

                decrypted_output, dec_time, dec_throughput, dec_ram = c_grain128_decrypt_file(ciphertext_bytes, key)
                #print("Decrypted output: ", decrypted_output)
                # Deserialize the frame
                #hex_image = decrypted_output.decode()[2:]
                #image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(dec_throughput)
                ram_list.append(dec_ram)
                total_frame_bytes += len(ciphertext_bytes)

                if elapsed_time >= 10:
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed")
                    print("\nDecryption metrics for 10 seconds:")

                    frame_dec_per_sec = round(frame_count / elapsed_time, 2)
                    print(f"Frames decrypted per second: {frame_dec_per_sec}")

                    avg_throughput = round(sum(throughput_list) / len(throughput_list), 2)
                    print(f"Average throughput: {avg_throughput} Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print(f"Average memory usage: {avg_ram} MB")

                    save_to_csv(args.algorithm, "128", frame_dec_per_sec, avg_throughput, avg_ram)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    total_frame_bytes = 0
                    start_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        elif args.algorithm == "mickey":
            sys.path.append('LW_Ciphers/Mickey-v2')
            from cMickey_main import c_mickey_decrypt_file
            print("------------------------------------------------")
            print("Using Mickey for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            total_frame_bytes = 0
            while True:
                chunk = connection_io.read(4)
                if not chunk:
                    break
                chunk = struct.unpack('<L', chunk)[0]
                ciphertext_bytes = connection_io.read(int(chunk))
                decrypted_output, dec_time, dec_throughput, dec_ram = c_mickey_decrypt_file(ciphertext_bytes, key)
                # Deserialize the frame
                #hex_image = decrypted_output.decode()[2:]
                #image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(dec_throughput)
                ram_list.append(dec_ram)
                total_frame_bytes += len(ciphertext_bytes)

                if elapsed_time >= 10:
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed")
                    print("\nDecryption metrics for 10 seconds:")

                    frame_dec_per_sec = round(frame_count / elapsed_time, 2)
                    print(f"Frames decrypted per second: {frame_dec_per_sec}")

                    avg_throughput = round(sum(throughput_list) / len(throughput_list), 2)
                    print(f"Average throughput: {avg_throughput} Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print(f"Average memory usage: {avg_ram} MB")

                    save_to_csv(args.algorithm, "80", frame_dec_per_sec, avg_throughput, avg_ram)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    total_frame_bytes = 0
                    start_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        elif args.algorithm == "trivium":
            sys.path.append('LW_Ciphers/Trivium')
            from cTRivium_main import c_trivium_decrypt_file
            print("------------------------------------------------")
            print("Using Trivium for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x03\x0e\x8d\xfd\xb13v\x88\xae\xff'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            total_frame_bytes = 0
            while True:
                chunk = connection_io.read(4)
                if not chunk:
                    break
                chunk = struct.unpack('<L', chunk)[0]
                ciphertext_bytes = connection_io.read(int(chunk))
                decrypted_output, dec_time, dec_throughput, dec_ram = c_trivium_decrypt_file(ciphertext_bytes, key)
                # Deserialize the frame
                # hex_image = decrypted_output[2:]
                # image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(dec_throughput)
                ram_list.append(dec_ram)
                total_frame_bytes += len(ciphertext_bytes)
                
                if elapsed_time >= 10:
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed")
                    print("\nDecryption metrics for 10 seconds:")

                    frame_dec_per_sec = round(frame_count / elapsed_time, 2)
                    print(f"Frames decrypted per second: {frame_dec_per_sec}")

                    avg_throughput = round(sum(throughput_list) / len(throughput_list), 2)
                    print(f"Average throughput: {avg_throughput} Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print(f"Average memory usage: {avg_ram} MB")

                    save_to_csv(args.algorithm, "80", frame_dec_per_sec, avg_throughput, avg_ram)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    total_frame_bytes = 0
                    start_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


        elif args.algorithm == "salsa":
            sys.path.append('LW_Ciphers/Salsa')
            from cSalsa_main import c_salsa_decrypt_file
            print("------------------------------------------------")
            print("Using Salsa for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x9a`\x94cn5\x13\xbc\xd0\\Q\xa3\x8f\x07\xd0\xa0'
            frame_count = 0
            start_time = time.time()
            throughput_list = []
            ram_list = []
            total_frame_bytes = 0
            while True:
                chunk = connection_io.read(4)
                chunk = struct.unpack('<L', chunk)[0]
                ciphertext_bytes = connection_io.read(int(chunk))
                decrypted_output, dec_time, dec_throughput, dec_ram =c_salsa_decrypt_file(ciphertext_bytes, key)
                # Deserialize the frame
                # hex_image = decrypted_output.decode()[2:]
                # image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(dec_throughput)
                ram_list.append(dec_ram)
                total_frame_bytes += len(ciphertext_bytes)

                if elapsed_time >= 10:
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed")
                    print("\nDecryption metrics for 10 seconds:")

                    frame_dec_per_sec = round(frame_count / elapsed_time, 2)
                    print(f"Frames decrypted per second: {frame_dec_per_sec}")

                    avg_throughput = round(sum(throughput_list) / len(throughput_list), 2)
                    print(f"Average throughput: {avg_throughput} Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print(f"Average memory usage: {avg_ram} MB")

                    save_to_csv(args.algorithm, "128", frame_dec_per_sec, avg_throughput, avg_ram)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    total_frame_bytes = 0
                    start_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        elif args.algorithm == "sosemanuk":
            sys.path.append('LW_Ciphers/Sosemanuk')
            from cSosemanuk_main import c_sosemanuk_decrypt_file
            print("------------------------------------------------")
            print("Using Sosemanuk for decrypting the video stream")
            # with open('key.txt', 'rb') as key_file:
            #     key = key_file.read()

            key = b'\x0fB\xe8:Se\x9d~\x86\x1fy\\\x88#0\xd9'
            while True:
                chunk = connection_io.read(4)
                chunk = struct.unpack('<L', chunk)[0]
                ciphertext_bytes = connection_io.read(chunk)
                decrypted_output, dec_time, dec_throughput, dec_ram = c_sosemanuk_decrypt_file(ciphertext_bytes, key)
                # Deserialize the frame
                # hex_image = decrypted_output.decode()[2:]
                # image_bytes = bytes.fromhex(hex_image)
                frame = cv2.imdecode(np.frombuffer(decrypted_output, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)

                frame_count += 1
                elapsed_time = time.time() - start_time
                throughput_list.append(dec_throughput)
                ram_list.append(dec_ram)
                total_frame_bytes += len(ciphertext_bytes)

                if elapsed_time >= 10:
                    print("\n------------------------------------------------")
                    print("A discreet time of 10 seconds has passed")
                    print("\nDecryption metrics for 10 seconds:")

                    frame_dec_per_sec = round(frame_count / elapsed_time, 2)
                    print(f"Frames decrypted per second: {frame_dec_per_sec}")

                    avg_throughput = round(sum(throughput_list) / len(throughput_list), 2)
                    print(f"Average throughput: {avg_throughput} Kbps")

                    avg_ram = round(sum(ram_list) / len(ram_list), 2)
                    print(f"Average memory usage: {avg_ram} MB")

                    save_to_csv(args.algorithm, "128", frame_dec_per_sec, avg_throughput, avg_ram)

                    frame_count = 0
                    throughput_list = []
                    ram_list = []
                    total_frame_bytes = 0
                    start_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        connection.close()
        server_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()