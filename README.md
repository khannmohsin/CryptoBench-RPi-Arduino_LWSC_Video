# CryptoBench-RPi-Arduino_LWSC_Video: Lightweight Stream Cipher Benchmarking Framework for Real-Time Video Encryption on ARM Devices

## Overview

This project provides a complete benchmarking framework for evaluating the performance of **Lightweight Stream Ciphers (LWSCs)** in **resource-intensive applications** such as real-time video feed encryption on **ARM-based IoT devices** (e.g., Raspberry Pi Zero). It implements, integrates, and measures several cryptographic ciphers under strict constraints and quantifies their suitability using advanced performance metrics including **encryption throughput**, **memory footprint**, **energy consumption**, and a unified efficiency score called **E-Rank**.


## Project Architecture

The framework is split across two systems:

- **Client**: Raspberry Pi Zero W with camera module — captures, encrypts, and streams video.
- **Server**: Host machine — receives and decrypts video for benchmarking and visualization.

A custom benchmarking tool is developed in **Python**, integrating **C implementations of LWSCs** through `.so` shared libraries using the `ctypes` library.

## Supported Ciphers

1. **Grain-v1**
2. **Grain-128a** (optimized)
3. **Trivium**
4. **Mickey-v1**
5. **Salsa20**
6. **Sosemanuk**

These are either finalists of the eSTREAM project or optimized versions used in constrained environments.

## Hardware Setup

- **Client**
  - Raspberry Pi Zero W (ARM11, 512MB RAM)
  - Raspberry Pi Camera Module
  - INA219 Power Sensor
  - Connected to Arduino Uno for energy monitoring
- **Server**
  - Local machine connected on the same network

**Power Measurement**: Controlled via GPIO signaling from Pi to Arduino to capture cipher-specific energy data per frame.

## Installation & Setup

### On Raspberry Pi (Client)

```bash
sudo apt update
sudo apt install python3 python3-opencv gcc cmake
pip install psutil
```

### Build Cipher Shared Libraries

Navigate to each cipher directory under `LW_Ciphers/` and compile with:

```bash
gcc -fPIC -shared -o grain.so grain.c
# Repeat for each cipher
```

## How to Run

### Encrypt Video (Client)

```bash
python3 enc_main.py
```

### Decrypt Video (Server)

```bash
python3 dec_main.py
```

### Rank Calculation

```bash
python3 RANK_cal.py
```

This calculates the **E-Rank** metric based on performance logs.

## Evaluation Metrics

| Metric               | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| FPSenc               | Frames encrypted per second                                                 |
| Throughput           | Kilobits per second                                                         |
| CpB                  | Processor Cycles per Byte                                                   |
| Code Size            | ROM/Flash usage in bytes                                                    |
| Memory Footprint     | RAM usage per byte of input                                                 |
| Energy Consumption   | Energy used per frame (mJ), measured via INA219                             |
| **E-Rank**           | Unified metric: Throughput / ((ROM + 2 × RAM) × Energy)                     |

These metrics are computed in real-time and aggregated using statistical analysis for stability.

## File Structure

```
LWC-VIDEO/
├── enc_main.py           # Client-side encryption handler
├── dec_main.py           # Server-side decryption handler
├── rb_enc_main.py        # Round-based encryption (experimental)
├── ex.py                 # Auxiliary experiment runner
├── RANK_cal.py           # Post-execution E-Rank metric calculator
├── first_cycles          # CpB measurement baseline
├── run_conversions.sh    # Format conversions for testing
├── LW_Ciphers/           # Directory with each cipher's source
│   ├── Grain-v1/
│   ├── Grain-128a/
│   ├── Trivium/
│   ├── Mickey/
│   ├── Salsa/
│   └── Sosemanuk/
```

## License

This project is distributed under the [MIT License](https://opensource.org/licenses/MIT).  
See the `LICENSE` file in the root of the repository for more details.
"""

## Academic Reference

If you use this codebase in your work, please consider citing the following:

This repository serves as the code companion to the paper:

**Citation**:  
Khan, M.; Dagenborg, H.; Johansen, D.  
_Performance Evaluation of Lightweight Stream Ciphers for Real-Time Video Feed Encryption on ARM Processor_.  
**Journal**: Future Internet  
**Year**: 2024  
**Volume**: 16  
**Issue**: 8  
**Article**: 261  
**DOI**: [10.3390/fi16080261](https://doi.org/10.3390/fi16080261)
