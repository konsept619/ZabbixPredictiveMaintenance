import numpy as np
import matplotlib.pyplot as plt
import csv
import json

with open("./configfile.json", 'r') as configfile:
    conf = json.load(configfile)

conf_zabbix = conf['zabbix_info']
file_path = conf_zabbix['dst_file']
data = []

with open("./collected_data", 'r', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        value = float(row[1])
        data.append(value)

median = np.median(data)
mad = np.median(np.abs(data - median))


modified_z_scores = 0.6745 * (np.array(data) - median) / mad


threshold = 2.5
lower_bound = median - threshold * (mad / 0.6745)
upper_bound = median + threshold * (mad / 0.6745)


anomalies = [x for x, score in zip(data, modified_z_scores) if np.abs(score) > threshold]

print(f"Number of detected anomalies: {len(anomalies)}")
print(f"Anomalies: {anomalies}")


plt.figure(figsize=(12, 6))
plt.hist(data, bins=50, color='skyblue', edgecolor='black', alpha=0.6, label='Dane')
plt.scatter(anomalies, np.zeros_like(anomalies), color='red', s=50, label='Anomalies', zorder=5)

plt.axvline(lower_bound, color='blue', linestyle='--', label=f'Lower bound ({lower_bound:.6f})')
plt.axvline(upper_bound, color='red', linestyle='--', label=f'Upper bound ({upper_bound:.6f})')

plt.title("Detecting anomalies with modified z-score method")
plt.xlabel("ICMP response times (ms)")
plt.ylabel("Frequency")
plt.legend()
plt.grid()
plt.show()