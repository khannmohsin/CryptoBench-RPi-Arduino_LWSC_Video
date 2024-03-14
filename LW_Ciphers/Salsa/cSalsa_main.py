import ctypes
import time
import psutil

# Load the shared library
lib = ctypes.CDLL("LW_Ciphers/Salsa/ecrypt.so")  # Change the filename accordingly

# Define necessary types
class ECRYPT_ctx(ctypes.Structure):
    _fields_ = [("input", ctypes.c_uint32 * 16)]

u8 = ctypes.c_uint8
u32 = ctypes.c_uint32

# Define function prototypes

ECRYPT_keysetup = lib.ECRYPT_keysetup
ECRYPT_ivsetup = lib.ECRYPT_ivsetup
ECRYPT_encrypt_bytes = lib.ECRYPT_encrypt_bytes
ECRYPT_decrypt_bytes = lib.ECRYPT_decrypt_bytes

ECRYPT_keysetup.argtypes = [ctypes.POINTER(ECRYPT_ctx), ctypes.POINTER(u8), u32, u32]
ECRYPT_ivsetup.argtypes = [ctypes.POINTER(ECRYPT_ctx), ctypes.POINTER(u8)]
ECRYPT_encrypt_bytes.argtypes = [ctypes.POINTER(ECRYPT_ctx), ctypes.POINTER(u8), ctypes.POINTER(u8), u32]
ECRYPT_decrypt_bytes.argtypes = [ctypes.POINTER(ECRYPT_ctx), ctypes.POINTER(u8), ctypes.POINTER(u8), u32]

# Define encryption and decryption functions
def c_salsa_encrypt_file(plaintext, key):

    len_plaintext = len(plaintext)
    ctx = ECRYPT_ctx()

    key_ptr = (u8 * len(key))(*key)
    iv = (u8 * 16)(11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26)

    ECRYPT_keysetup(ctypes.byref(ctx), key_ptr, len(key) * 8, 128)
    ECRYPT_ivsetup(ctypes.byref(ctx), iv)

    ciphertext = (u8 * len(plaintext))()
    plaintext_buffer = ctypes.cast(plaintext, ctypes.POINTER(u8))

    start_time = time.perf_counter()

    ECRYPT_encrypt_bytes(ctypes.byref(ctx), plaintext_buffer, ciphertext, len(plaintext))

    end_time = time.perf_counter()

    Process = psutil.Process()
    avg_ram = Process.memory_info().rss / 1024 / 1024

    encryption_time = end_time - start_time

    formatted_encryption_time = round(encryption_time, 2)
    print(f"Encryption time: {formatted_encryption_time} seconds")

    throughput = round(len_plaintext / encryption_time, 2)   # Throughput in Kbps
    print(f"Encryption Throughput: {throughput} Kbps")

    ram = round(avg_ram, 2)
    print(f"Average memory usage: {ram} MB")

    return ciphertext, formatted_encryption_time, throughput, ram 

def c_salsa_decrypt_file(ciphertext, key):

    len_ciphertext = len(ciphertext)
    ctx = ECRYPT_ctx()

    key_ptr = (u8 * len(key))(*key)
    iv = (u8 * 16)(11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26)

    ECRYPT_keysetup(ctypes.byref(ctx), key_ptr, len(key) * 8, 128)
    ECRYPT_ivsetup(ctypes.byref(ctx), iv)

    plaintext = (u8 * len(ciphertext))()
    ciphertext_buffer = ctypes.cast(ciphertext, ctypes.POINTER(u8))

    start_time = time.perf_counter()

    ECRYPT_decrypt_bytes(ctypes.byref(ctx), ciphertext_buffer, plaintext, len(ciphertext))

    end_time = time.perf_counter()
    Process = psutil.Process()
    avg_ram = Process.memory_info().rss / 1024 / 1024

    decryption_time = end_time - start_time

    formatted_decryption_time = round(decryption_time, 2)
    print(f"Decryption time: {formatted_decryption_time} seconds")

    throughput = round(len_ciphertext / decryption_time, 2)   # Throughput in Kbps
    print(f"Decryption Throughput: {throughput} Kbps")

    ram = round(avg_ram, 2)
    print(f"Average memory usage: {ram} MB")

    return plaintext, formatted_decryption_time, throughput, ram


