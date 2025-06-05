import ctypes
import time 
import psutil
import os
import subprocess

# Load the shared library
libgrain = ctypes.CDLL("LW_Ciphers/Grain-v1/grain.so")

# Define necessary types
class ECRYPT_ctx(ctypes.Structure):
    _fields_ = [("p_key", ctypes.POINTER(ctypes.c_uint8)),
                ("keysize", ctypes.c_uint32),
                ("ivsize", ctypes.c_uint32),
                ("NFSR", ctypes.c_uint8 * 80),
                ("LFSR", ctypes.c_uint8 * 80)]

# Define function prototypes
libgrain.grain_keystream.argtypes = [ctypes.POINTER(ECRYPT_ctx)]
libgrain.grain_keystream.restype = ctypes.c_uint8

libgrain.ECRYPT_init.argtypes = []

libgrain.ECRYPT_keysetup.argtypes = [ctypes.POINTER(ECRYPT_ctx),
                                     ctypes.POINTER(ctypes.c_uint8),
                                     ctypes.c_uint32,
                                     ctypes.c_uint32]

libgrain.ECRYPT_ivsetup.argtypes = [ctypes.POINTER(ECRYPT_ctx),
                                    ctypes.POINTER(ctypes.c_uint8)]

libgrain.ECRYPT_keystream_bytes.argtypes = [ctypes.POINTER(ECRYPT_ctx),
                                            ctypes.POINTER(ctypes.c_uint8),
                                            ctypes.c_uint32]

libgrain.ECRYPT_encrypt_bytes.argtypes = [ctypes.POINTER(ECRYPT_ctx),
                                          ctypes.POINTER(ctypes.c_uint8),
                                          ctypes.POINTER(ctypes.c_uint8),
                                          ctypes.c_uint32]

libgrain.ECRYPT_decrypt_bytes.argtypes = [ctypes.POINTER(ECRYPT_ctx),
                                          ctypes.POINTER(ctypes.c_uint8),
                                          ctypes.POINTER(ctypes.c_uint8),
                                          ctypes.c_uint32]

ctx = ECRYPT_ctx()

def get_memory_usage():
    """Get the current memory usage of the process.

    Returns:
    int: The memory usage in bytes.
    """
    process = subprocess.Popen("ps -p %d -o rss | tail -n 1" % os.getpid(), shell=True, stdout=subprocess.PIPE)
    out, _ = process.communicate()
    memory = int(out.strip()) * 1024  # Convert from KB to bytes
    return memory

# Helper functions
def c_grain_v1_encrypt_file(plaintext, key):
    len_plaintext = len(plaintext)
    # print("Length of frame:", len_plaintext)
    file_size_Kb = len_plaintext * 8 / 1000  # File size in Kilobits

    # pid = os.getpid()
    # print("PID:", pid)
    # start_memory = get_memory_usage_proc(pid)

    memory_before = get_memory_usage()
    ctx = ECRYPT_ctx()

    key_ptr = (ctypes.c_uint8 * len(key))(*key)
    iv = (ctypes.c_uint8 * 8)(11, 12, 13, 14, 15, 16, 17, 18)

    libgrain.ECRYPT_keysetup(ctypes.byref(ctx), key_ptr, 80, 64)
    libgrain.ECRYPT_ivsetup(ctypes.byref(ctx), iv)

    plaintext_buffer = ctypes.cast(plaintext, ctypes.POINTER(ctypes.c_uint8))

    ciphertext = (ctypes.c_uint8 * len(plaintext))()
    start_time = time.perf_counter()

    libgrain.ECRYPT_encrypt_bytes(ctypes.byref(ctx), plaintext_buffer, ciphertext, len(plaintext))

    end_time = time.perf_counter()

    encryption_time = end_time - start_time
    memory_after = get_memory_usage()

    # end_memory = get_memory_usage_proc(pid)

    formatted_encryption_time = round(encryption_time, 2)
    # print(f"Encryption time: {formatted_encryption_time} seconds")

    throughput = round(file_size_Kb / encryption_time, 2)   # Throughput in Kbps
    # print(f"Encryption Throughput: {throughput} Kbps")

    memory_consumption = round(memory_after, 2)
    mem_footprint = round((memory_after)/len(plaintext), 2)
    # print(f"Memory usage: {memory_consumption} bytes")
    # print("Memory footprint:", mem_footprint, "bytes per byte of plaintext")

    # memory_consumption = end_memory - start_memory
    # print("Memory usage:", memory_consumption, "bytes")

    return ciphertext, formatted_encryption_time, throughput, mem_footprint


def c_grain_v1_decrypt_file(ciphertext, key):
    len_ciphertext = len(ciphertext)
    file_size_Kb = len_ciphertext * 8 / 1000
    # ctx = ECRYPT_ctx()

    key_ptr = (ctypes.c_uint8 * len(key))(*key)
    iv = (ctypes.c_uint8 * 8)(11, 12, 13, 14, 15, 16, 17, 18)

    libgrain.ECRYPT_keysetup(ctypes.byref(ctx), key_ptr, 80, 64)
    libgrain.ECRYPT_ivsetup(ctypes.byref(ctx), iv)

    plaintext = (ctypes.c_uint8 * len(ciphertext))()
    ciphertext_buffer = ctypes.cast(ciphertext, ctypes.POINTER(ctypes.c_uint8))

    start_time = time.perf_counter()

    libgrain.ECRYPT_decrypt_bytes(ctypes.byref(ctx), ciphertext_buffer, plaintext, len(ciphertext))

    end_time = time.perf_counter()

    Process = psutil.Process()
    avg_ram = Process.memory_info().rss / 1024 / 1024

    decryption_time = end_time - start_time

    formatted_decryption_time = round(decryption_time, 2)
    #print(f"Decryption time: {formatted_decryption_time} seconds")

    throughput = round(file_size_Kb / decryption_time, 2)   # Throughput in Kbps
    #print(f"Decryption Throughput: {throughput} Kbps")

    ram = round(avg_ram, 2)
    #print(f"Average memory usage: {ram} MB")

    return plaintext, formatted_decryption_time, throughput, ram
