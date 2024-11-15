import csv
import os
import requests
import time
import json

with open("./configfile.json", 'r') as configfile:
    conf = json.load(configfile)

#Take variables from configuration file
conf_zabbix = conf['zabbix_info']

host_name = conf_zabbix['host_name']
url = conf_zabbix['url']
item_name = conf_zabbix['item_name']
auth_token = conf_zabbix['auth_token']
start_date = conf_zabbix['start_date']
end_date = conf_zabbix['end_date']
data_scope = conf_zabbix['data_scope']
file_path = conf_zabbix['dst_file']
headers = {"Content-Type": "application/json"}


def get_item_id(host_name, item_name):
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": ["itemid", "name"],
            "host": host_name,
            "search": {
                "name": item_name
            }
        },
        "auth": auth_token,
        "id": 2
    }
    response = requests.post(url, json=payload, headers=headers)
    items = response.json().get("result")
    return items[0]["itemid"] if items else None



item_id = get_item_id(host_name, item_name)

if not item_id:
    alert = "There is no item called <%s> for given host" % (item_name)
    print(alert)
    exit()


def get_icmp_response_time(item_id, start_time, end_time):
    payload = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": 0,
            "itemids": item_id,
            "time_from": start_time,
            "time_till": end_time,
            "sortfield": "clock",
            "sortorder": "ASC",
            "limit": data_scope
        },
        "auth": auth_token,
        "id": 3
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("result")


def is_data_newer(file_path, new_data):
    if not os.path.exists(file_path):
        return True

    with open(file_path, 'r', newline='') as infile:
        reader = csv.reader(infile)
        try:
            last_row = list(reader)[-1]
            last_time = int(last_row[-1])
        except (IndexError, ValueError):
            return True

    new_data_time = int(new_data[0]["clock"])
    return new_data_time > last_time



time_from = int(time.mktime(time.strptime(start_date, "%Y-%m-%d %H:%M:%S")))
time_till = int(time.mktime(time.strptime(end_date, "%Y-%m-%d %H:%M:%S")))

data = get_icmp_response_time(item_id, time_from, time_till)

if data and is_data_newer(file_path, data):
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        index = 0 if not os.path.exists(file_path) else sum(1 for _ in open(file_path))

        print(f"ICMP Response Time for host '{host_name}' since {start_date} to {end_date}:")
        for entry in data:
            timestamp = entry["clock"]
            value = entry["value"]
            value = round(float(value), 10)
            writer.writerow([index, value, timestamp])
            index += 1
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}, ICMP response: {value} ms")
    print("Data written to file")
else:
    print("Loaded data is older or file is up to date")