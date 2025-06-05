import ctypes
import time 
import psutil
import os 
import subprocess

# Define types
u8 = ctypes.c_uint8
u32 = ctypes.c_uint32

# Load the shared library
lib = ctypes.CDLL("LW_Ciphers/Mickey-v2/mickey2.so")

# Define the ECRYPT_ctx structure
class ECRYPT_ctx(ctypes.Structure):
    _fields_ = [("R", u32 * 4),
                ("S", u32 * 4),
                ("key", u8 * 10),
                ("ivsize", u32)]

# Define function prototypes
ECRYPT_init = lib.ECRYPT_init
ECRYPT_init.argtypes = []
ECRYPT_init.restype = None

ECRYPT_keysetup = lib.ECRYPT_keysetup
ECRYPT_keysetup.argtypes = [ctypes.POINTER(ECRYPT_ctx), ctypes.POINTER(u8), u32, u32]
ECRYPT_keysetup.restype = None

ECRYPT_ivsetup = lib.ECRYPT_ivsetup
ECRYPT_ivsetup.argtypes = [ctypes.POINTER(ECRYPT_ctx), ctypes.POINTER(u8)]
ECRYPT_ivsetup.restype = None

ECRYPT_keystream_bytes = lib.ECRYPT_keystream_bytes
ECRYPT_keystream_bytes.argtypes = [ctypes.POINTER(ECRYPT_ctx), ctypes.POINTER(u8), u32]
ECRYPT_keystream_bytes.restype = None

ECRYPT_process_bytes = lib.ECRYPT_process_bytes
ECRYPT_process_bytes.argtypes = [u32, ctypes.POINTER(ECRYPT_ctx), ctypes.POINTER(u8), ctypes.POINTER(u8), u32]
ECRYPT_process_bytes.restype = None

# Initialize the library
ECRYPT_init()

def get_memory_usage():
    """Get the current memory usage of the process.

    Returns:
    int: The memory usage in bytes.
    """
    process = subprocess.Popen("ps -p %d -o rss | tail -n 1" % os.getpid(), shell=True, stdout=subprocess.PIPE)
    out, _ = process.communicate()
    memory = int(out.strip()) * 1024  # Convert from KB to bytes
    return memory

def c_mickey_encrypt_file(plaintext, key):

    len_plaintext = len(plaintext)
    # print("Length of frame:", len_plaintext)
    file_size_Kb = len_plaintext * 8 / 1000  # File size in Kilobits

    # pid = os.getpid()
    # print("PID:", pid)
    # start_memory = get_memory_usage_proc(pid)

    memory_before = get_memory_usage()

    ctx = ECRYPT_ctx()
    key = (u8 * 10)(*key)
    iv = (u8 * 16)(11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26)  # Example IV
    ECRYPT_keysetup(ctypes.byref(ctx), key, 80, len(iv)*8)
    ECRYPT_ivsetup(ctypes.byref(ctx), iv)
 
    keystream = (u8 * len(plaintext))()

    ciphertext = bytearray(len(plaintext))
    start_time = time.perf_counter()
    ECRYPT_keystream_bytes(ctypes.byref(ctx), keystream, len(plaintext))

    for i in range(len(plaintext)):
        ciphertext[i] = plaintext[i] ^ keystream[i]

    end_time = time.perf_counter()
    memory_after = get_memory_usage()

    # end_memory = get_memory_usage_proc(pid)

    encryption_time = end_time - start_time

    formatted_encryption_time = round(encryption_time, 2)
    # print("Total encryption time:", formatted_encryption_time, "seconds")

    throughput = round(file_size_Kb / encryption_time, 2)   # Throughput in Kbps
    # print("Encryption Throughput:", throughput, "Kbps")

    memory_consumption = round((memory_after), 2)
    memory_footprint = round((memory_after)/len_plaintext, 2)
    # print("Memory usage:", memory_consumption, "bytes")
    # print("Memory footprint:", memory_footprint, "bytes per byte of plaintext")

    # memory_consumption = end_memory - start_memory
    # print("Memory usage:", memory_consumption, "bytes")

    return ciphertext, formatted_encryption_time, throughput, memory_footprint

# Decryption function
def c_mickey_decrypt_file(ciphertext, key):

    len_ciphertext = len(ciphertext)
    file_size_Kb = len_ciphertext * 8 / 1000

    ctx = ECRYPT_ctx()
    key = (u8 * 10)(*key)
    iv = (u8 * 16)(11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26)
    ECRYPT_keysetup(ctypes.byref(ctx), key, 80, len(iv)*8)
    ECRYPT_ivsetup(ctypes.byref(ctx), iv)

    keystream = (u8 * len(ciphertext))()

    plaintext = bytearray(len(ciphertext))

    start_time = time.perf_counter()

    ECRYPT_keystream_bytes(ctypes.byref(ctx), keystream, len(ciphertext))
    for i in range(len(ciphertext)):
        plaintext[i] = ciphertext[i] ^ keystream[i]

    end_time = time.perf_counter()

    Process = psutil.Process()
    avg_ram = Process.memory_info().rss / 1024 / 1024

    decryption_time = end_time - start_time

    formatted_decryption_time = round(decryption_time, 2)

    #print("Total decryption time:", formatted_decryption_time, "seconds")

    throughput = round(file_size_Kb / decryption_time, 2)   # Throughput in Kbps
    #print("Decryption Throughput:", throughput, "Kbps")

    ram = round(avg_ram, 2)
    #print("Average memory usage:", ram, "MB")

    return plaintext, formatted_decryption_time, throughput, ram 

