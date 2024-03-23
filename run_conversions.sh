# -----------------C compilation of GRAIN CIPHER -----------------
gcc -fPIC -shared -o LW_Ciphers/Grain-128a/grain128aead_32p.so LW_Ciphers/Grain-128a/grain128aead_32p.c

# -----------------C compilation of GRAIN-v1 CIPHER -----------------
gcc -fPIC -shared -o LW_Ciphers/Grain-v1/grain.so LW_Ciphers/Grain-v1/grain.c

# -----------------C compilation of MICKEY-v2 CIPHER -----------------
gcc -fPIC -shared -o LW_Ciphers/Mickey-v2/mickey2.so LW_Ciphers/Mickey-v2/mickey2.c

# -----------------C compilation of SALSA CIPHER -----------------
gcc -fPIC -shared -o LW_Ciphers/Salsa/ecrypt.so LW_Ciphers/Salsa/ecrypt.c

# -----------------C compilation of SOSEMANUK CIPHER -----------------
gcc -fPIC -shared -o LW_Ciphers/Sosemanuk/sosemanuk.so LW_Ciphers/Sosemanuk/sosemanuk.c

# -----------------C compilation of TRIVIUM CIPHER -----------------
gcc -fPIC -shared -o LW_Ciphers/Trivium/trivium.so LW_Ciphers/Trivium/trivium.c