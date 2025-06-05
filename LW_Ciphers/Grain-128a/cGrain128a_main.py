import ctypes
import time
import psutil
import subprocess
import os

crypto_lib = ctypes.CDLL('LW_Ciphers/Grain-128a/grain128aead_32p.so')

# Define the argument types and return type for the function
crypto_lib.crypto_aead_encrypt.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),  # unsigned char *c
    ctypes.POINTER(ctypes.c_ulonglong),  # unsigned long long *clen
    ctypes.POINTER(ctypes.c_ubyte),  # const unsigned char *m
    ctypes.c_ulonglong,  # unsigned long long mlen
    ctypes.POINTER(ctypes.c_ubyte),  # const unsigned char *ad
    ctypes.c_ulonglong,  # unsigned long long adlen
    ctypes.POINTER(ctypes.c_ubyte),  # const unsigned char *nsec
    ctypes.POINTER(ctypes.c_ubyte),  # const unsigned char *npub
    ctypes.POINTER(ctypes.c_ubyte)   # const unsigned char *k
]
crypto_lib.crypto_aead_encrypt.restype = ctypes.c_int  # Return type int

# Define the argument types and return type for the function
crypto_lib.crypto_aead_decrypt.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),  # unsigned char *m
    ctypes.POINTER(ctypes.c_ulonglong),  # unsigned long long *mlen
    ctypes.POINTER(ctypes.c_ubyte),  # unsigned char *nsec
    ctypes.POINTER(ctypes.c_ubyte),  # const unsigned char *cp
    ctypes.c_ulonglong,  # unsigned long long clen
    ctypes.POINTER(ctypes.c_ubyte),  # const unsigned char *adp
    ctypes.c_ulonglong,  # unsigned long long adlen
    ctypes.POINTER(ctypes.c_ubyte),  # const unsigned char *npubp
    ctypes.POINTER(ctypes.c_ubyte)   # const unsigned char *kp
]
crypto_lib.crypto_aead_decrypt.restype = ctypes.c_int  # Return type int


def crypto_aead_decrypt(m, mlen, nsec, cp, clen, adp, adlen, npubp, kp):
    return crypto_lib.crypto_aead_decrypt(m, mlen, nsec, cp, clen, adp, adlen, npubp, kp)

def crypto_aead_encrypt(c, clen, m, mlen, ad, adlen, nsec, npub, k):
    return crypto_lib.crypto_aead_encrypt(c, clen, m, mlen, ad, adlen, nsec, npub, k)

def get_memory_usage():
    """Get the current memory usage of the process.

    Returns:
    int: The memory usage in bytes.
    """
    process = subprocess.Popen("ps -p %d -o rss | tail -n 1" % os.getpid(), shell=True, stdout=subprocess.PIPE)
    out, _ = process.communicate()
    memory = int(out.strip()) * 1024  # Convert from KB to bytes
    return memory

# def get_memory_usage_proc(pid):
#     """Get the memory usage of a process using the /proc filesystem."""
#     try:
#         with open(f"/proc/{pid}/status", "r") as status_file:
#             for line in status_file:
#                 if line.startswith("VmRSS:"):
#                     return int(line.split()[1])  # Memory usage in kilobytes
#     except FileNotFoundError:
#         print(f"Error: Process with PID {pid} not found.")
#         return None

def c_grain128_encrypt_file(plaintext, key):

    len_key = len(key)
    len_plaintext = len(plaintext)
    # print("Length of frame:", len_plaintext)
    file_size_Kb = len_plaintext * 8 / 1000  # File size in Kilobits

    # pid = os.getpid()
    # print("PID:", pid)
    # start_memory = get_memory_usage_proc(pid)
    memory_before = get_memory_usage()
    hex_image_bytes_literal = plaintext

    # Example usage
    m = plaintext  # Example plaintext
    m_buffer = ctypes.create_string_buffer(hex_image_bytes_literal)  # Example buffer for plaintext
    m_ptr = ctypes.cast(m_buffer, ctypes.POINTER(ctypes.c_ubyte))
    mlen = ctypes.c_ulonglong(len(m))  # Length of the message
    ad = b"additional data"  # Example additional data
    ad_buffer = ctypes.create_string_buffer(ad)
    ad_ptr = ctypes.cast(ad_buffer, ctypes.POINTER(ctypes.c_ubyte))
    adlen = ctypes.c_ulonglong(len(ad))  # Length of additional data
    nsec = None  # Example value for nsec (can be None)
    npub = b"nonce"  # Example nonce
    npub_buffer = ctypes.create_string_buffer(npub)
    npub_ptr = ctypes.cast(npub_buffer, ctypes.POINTER(ctypes.c_ubyte))
    k = key  # Example key
    k_buffer = ctypes.create_string_buffer(k)
    k_ptr = ctypes.cast(k_buffer, ctypes.POINTER(ctypes.c_ubyte))
    c_len = ctypes.c_ulonglong()  # Example variable for clen
    
    c_buffer = ctypes.create_string_buffer(len(m) + 16)  # Example buffer for ciphertext
    c_ptr = ctypes.cast(c_buffer, ctypes.POINTER(ctypes.c_ubyte))

    start_time = time.perf_counter()
    # Call the function
    result_encrypt = crypto_aead_encrypt(c_ptr, ctypes.byref(c_len), m_ptr, mlen, ad_ptr, adlen, nsec, npub_ptr, k_ptr)
    end_time = time.perf_counter()
    encryption_time = end_time - start_time
    memory_after = get_memory_usage()
    # end_memory = get_memory_usage_proc(pid)

    if result_encrypt == 0:
        # print("Encryption successful!")
        buffer_contents = ctypes.string_at(c_buffer, c_len.value)

        formatted_encryption_time = round(encryption_time, 2)

        # print("Total encryption time:", formatted_encryption_time, "seconds")

        throughput = round(file_size_Kb / encryption_time, 2)   # Throughput in Kbps

        # print("Encryption Throughput:", throughput, "Kbps")

        memory_consumption = round(memory_after, 2)
        memory_footprint = round((memory_after) / len(plaintext), 2)
        # print("Memory usage:", memory_consumption, "bytes")
        # print("Memory footprint:", memory_footprint, "bytes per byte of plaintext")
        # memory_consumption = end_memory - start_memory
        # print("Memory usage:", memory_consumption, "bytes")

        return buffer_contents, formatted_encryption_time, throughput, memory_footprint 
    else:
        print("Encryption failed!")


def c_grain128_decrypt_file(ciphertext, key):

    len_key = len(key)
    len_ciphertext = len(ciphertext)
    file_size_Kb = len_ciphertext * 8 / 1000
    
    k_buffer = ctypes.create_string_buffer(key)
    k_ptr = ctypes.cast(k_buffer, ctypes.POINTER(ctypes.c_ubyte))

    ad = b"additional data"  # Example additional data
    ad_buffer = ctypes.create_string_buffer(ad)
    ad_ptr = ctypes.cast(ad_buffer, ctypes.POINTER(ctypes.c_ubyte))
    adlen = ctypes.c_ulonglong(len(ad))  # Length of additional data

    npub = b"nonce"  # Example nonce
    npub_buffer = ctypes.create_string_buffer(npub)
    npub_ptr = ctypes.cast(npub_buffer, ctypes.POINTER(ctypes.c_ubyte))

    ciphertext_buffer = ctypes.create_string_buffer(ciphertext)
    ciphertext_ptr = ctypes.cast(ciphertext_buffer, ctypes.POINTER(ctypes.c_ubyte))

    clen = ctypes.c_ulonglong(len(ciphertext))

    nsec = None  # Example value for nsec (can be None)

    m_len = ctypes.c_ulonglong()

    m_buffer = ctypes.create_string_buffer(len(ciphertext) - 16)  # Example buffer for decrypted message

    m_ptr = ctypes.cast(m_buffer, ctypes.POINTER(ctypes.c_ubyte))

    start_time = time.perf_counter()

    # Call the function
    result_decrypt = crypto_aead_decrypt(m_ptr, ctypes.byref(m_len), nsec, ciphertext_ptr, clen, ad_ptr, adlen, npub_ptr, k_ptr)

    end_time = time.perf_counter()

    Process = psutil.Process()
    avg_ram = Process.memory_info().rss / 1024 / 1024

    decryption_time = end_time - start_time
    if result_decrypt == 0:
        # print("Decryption successful!")
        buffer_contents = ctypes.string_at(m_buffer, m_len.value)

        formatted_decryption_time = round(decryption_time, 2)

        # print("Total decryption time:", formatted_decryption_time, "seconds")

        throughput = round(file_size_Kb / decryption_time, 2)   # Throughput in Kbps
        # print("Decryption Throughput:", throughput)

        ram = round(avg_ram, 2)
        #print("Average memory usage:", ram, "MB")

        return buffer_contents, formatted_decryption_time, throughput, ram

    else:
        print("Decryption failed!")
