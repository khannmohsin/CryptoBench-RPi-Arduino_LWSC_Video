import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
import sys


import argparse

# Argument Parser
parser = argparse.ArgumentParser(description='Enter your filepath you want to results of.')
parser.add_argument('file_path', type=str, help='Path to the CSV file')
args = parser.parse_args()

# Now you can access the file path using args.file_path
print("File Path:", args.file_path)


file_name = args.file_path

# Read the CSV file into a DataFrame
df = pd.read_csv(file_name, names=["Algorithm", "Key Size", *range(10)])


# Trim the first two rows
trimmed_df = df.iloc[1:]

# print(trimmed_df)

# Select columns
df_algorithm = df.iloc[:, 0] 
df_key_size = df.iloc[:, 1]
df_values = df.iloc[:, 2:]

# Convert columns to lists
first_column_list = df_algorithm.values.tolist()    
second_column_list = df_key_size.values.tolist()
third_column_list = df_values.values.tolist()

# Merge the three lists
merged_list = [f"{alg}_{key}" for alg, block, key in zip(first_column_list, second_column_list, third_column_list)]

# Remove the first element from the merged list
merged_list = merged_list[1:]

trimmed_values_list = third_column_list[1:]
# print(trimmed_values_list)
# print(trimmed_values_list)
y_axis = []
mean_list = []
std_dev_list = []
confidence_interval_list = []

for sublist in trimmed_values_list:
    # print(sublist)
    sublist_list = []

    for val in sublist:
        sublist_list.append(val)

    # print(sublist_list)
        
    # Remove 'nan' values from the list
    data_without_nan = [value for value in sublist_list if not isinstance(value, float) or not math.isnan(value)]

    # print(data_without_nan)

    # Convert every element to float
    data_float = [float(val) for val in data_without_nan]

    mean = np.mean(data_float)
    std_dev = np.std(data_float)
    confidence_interval = 1.96 * (std_dev / np.sqrt(len(data_float)))

    rounded_mean = round(mean, 2)
    rounded_std_dev = round(std_dev, 2)
    confidence_interval = round(confidence_interval, 2)

    mean_list.append(rounded_mean)
    std_dev_list.append(rounded_std_dev)
    confidence_interval_list.append(confidence_interval)


print(mean_list)
# print(std_dev_list)
print(confidence_interval_list)

print(mean_list)
plt.figure(figsize=(12, 8))
plt.xlabel('Ciphers')
plt.bar(merged_list, mean_list, yerr=confidence_interval_list, capsize=4, color='turquoise', ecolor='black')


# If file name has decryption_throughput
if "encryption_time" in file_name:
    print("Encryption Time")
    plt.ylabel('Time (seconds)')
    plt.title('Encryption Time of the Ciphers')

elif "decryption_time" in file_name:
    print("Decryption Time")
    plt.ylabel('Time (seconds)')
    plt.title('Decryption Time of the Ciphers')

elif "encryption_throughput" in file_name:
    for i, value in enumerate(mean_list):
        plt.text(i, value,  "  "  + str(value), ha = 'center', va = 'bottom', rotation=90)
    plt.yscale('log')
    print("Encryption Throughput")
    plt.ylabel('Throughput (Kbps)')
    plt.title('Encryption Throughput of the Ciphers')

elif "decryption_throughput" in file_name:
    for i, value in enumerate(mean_list):
        plt.text(i, value,  "  "  + str(value), ha = 'center', va = 'bottom', rotation=90)
    plt.yscale('log')
    print("Decryption Throughput")
    plt.ylabel('Throughput (Kbps)')
    plt.title('Decryption Throughput of the Ciphers')

plt.legend()
plt.tight_layout()
plt.xticks(rotation=90)
plt.subplots_adjust(bottom=0.3)
plt.show()


