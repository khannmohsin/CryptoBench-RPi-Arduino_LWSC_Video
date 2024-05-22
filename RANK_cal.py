import math 

def calculate_rank(throughput_kb_sec, rom, ram, energy_consumption):
    # Convert throughput from kilobits/sec to bytes/sec
    throughput_bytes_sec = throughput_kb_sec * 125  # 1 kilobit = 125 bytes

    # Calculate RANK
    rank = throughput_bytes_sec / ((rom + 2 * ram) * energy_consumption)
    rank = round(rank, 2)
    return rank

def main():
    # Get input values
    rom = float(input("Enter ROM value: "))
    ram = float(input("Enter RAM value: "))
    throughput_kb_sec = float(input("Enter throughput (in Kilobits/sec): "))
    energy_consumption = float(input("Enter energy consumption: "))

    # Calculate RANK
    rank = calculate_rank(throughput_kb_sec, rom, ram, energy_consumption)

    # Print result
    print("RANK:", rank)

if __name__ == "__main__":
    main()