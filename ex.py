def calculate_formula(keysize, CpB, throughput, ROM, energy, weighted_sec_vulnerability):
    result = (keysize * ((10**6/CpB) + throughput)) / (ROM + 2 * ROM * energy * weighted_sec_vulnerability)
    return result

def main():
    keysize = float(input("Enter the value for keysize: "))
    CpB = float(input("Enter the value for CpB (Cycles per Byte): "))
    throughput = float(input("Enter the value for throughput: "))
    ROM = float(input("Enter the value for ROM: "))
    energy = float(input("Enter the value for energy: "))
    weighted_sec_vulnerability = float(input("Enter the value for weighted_sec_vulnerability: "))

    result = calculate_formula(keysize, CpB, throughput, ROM, energy, weighted_sec_vulnerability)
    print("Result:", result)

if __name__ == "__main__":
    main()



https://www.usenix.org/sites/default/files/sec24_cfp_040623.pdf
https://sp2025.ieee-security.org/cfpapers.html
https://www.usenix.org/conference/usenixsecurity25
https://tcc.iacr.org/2