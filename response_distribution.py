import matplotlib.pyplot as plt
import seaborn as sns
import csv
import scipy.stats as stats
import numpy as np
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


plt.figure(figsize=(10, 6))
plt.hist(data, bins=50, color='skyblue', edgecolor='black', density=True)
plt.title("Histogram of ICMP times")
plt.xlabel("ICMP response time (ms)")
plt.ylabel("Density of apperances")
plt.grid()
plt.show()

plt.figure(figsize=(10, 6))
sns.kdeplot(data, fill=True, color='skyblue')
plt.title("KDE of ICMP response times")
plt.xlabel("Response time")
plt.ylabel("Density of apperances")
plt.grid()
plt.show()



gamma_params = stats.gamma.fit(data)
lognorm_params = stats.lognorm.fit(data)


x = np.linspace(min(data), max(data), 1000)
gamma_pdf = stats.gamma.pdf(x, *gamma_params)
lognorm_pdf = stats.lognorm.pdf(x, *lognorm_params)

plt.figure(figsize=(10, 6))
plt.hist(data, bins=50, density=True, alpha=0.6, color='skyblue', edgecolor='black', label='Histogram')
plt.plot(x, gamma_pdf, color='red', label='Gamma distribution')
plt.plot(x, lognorm_pdf, color='green', label='Log-normal distribution')
plt.title("Histogram with matched theoretical distributions")
plt.xlabel("Response time")
plt.ylabel("Density of probability")
plt.legend()
plt.grid()
plt.show()
