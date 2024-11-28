from statistics import median
import numpy as np
import matplotlib.pyplot as plt
import csv
import json

with open("./configfile.json", 'r') as configfile:
    conf = json.load(configfile)

conf_zabbix = conf['zabbix_info']
file_path = conf_zabbix['dst_file']
data = []

with open(file_path, 'r', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        value = float(row[1])
        data.append(value)

std_deviation = np.std(data)
mean = np.mean(data)
print(f"Standard deviation: {std_deviation}")

coeff_variation = std_deviation / mean
print(coeff_variation*100)

q1_data = np.quantile(data, 0.25)
q3_data = np.quantile(data, 0.75)
IQR=q3_data - q1_data

median_dataset = median(data)

k = 1.5 #distance from IQR

lower_bound = q1_data - k*IQR
upper_bound = q3_data + k*IQR

anomalies = [x for x in data if x < lower_bound or x > upper_bound]

#print(q1_data, q3_data, IQR, anomalies)
print(f"Q1: {q1_data},\nQ3: {q3_data},\nIQR: {IQR},\nAnomalies: {anomalies}")
plt.figure(figsize=(10, 6))
plt.hist(data, bins=50, density=True, alpha=0.6, color='skyblue', edgecolor='black', label='Histogram')
plt.axvline(float(q1_data), color='blue', linestyle='--', label=f'Q1 ({q1_data:.6f})')
plt.axvline(lower_bound, color='blue', linestyle=':', label=f'Lower bound ({lower_bound:.6f})')
plt.axvline(median_dataset, color='black', linestyle='--', label=f'Median ({median_dataset:.6f})')
plt.axvline(float(q3_data), color='red', linestyle='--', label=f'Q3 ({q3_data:.6f})')
plt.axvline(upper_bound, color='red', linestyle=':', label=f'Upper bound ({upper_bound:.6f})')
plt.scatter(anomalies, np.zeros_like(anomalies), color='red', s=50, label='Anomalies', zorder=5)
plt.legend()
plt.grid()
plt.show()