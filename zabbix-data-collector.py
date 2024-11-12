import requests
import time
import json

with open("./configfile.json", 'r') as configfile:
    conf = json.load(configfile)

conf_zabbix = conf['zabbix_info']

host_name = conf_zabbix['host_name']
url = conf_zabbix['url']
item_name = conf_zabbix['item_name']
auth_token = conf_zabbix['auth_token']
start_date = conf_zabbix['start_date']
end_date = conf_zabbix['end_date']
data_scope = conf_zabbix['data_scope']


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



time_from = int(time.mktime(time.strptime(start_date, "%Y-%m-%d %H:%M:%S")))
time_till = int(time.mktime(time.strptime(end_date, "%Y-%m-%d %H:%M:%S")))

data = get_icmp_response_time(item_id, time_from, time_till)

with open('./collected_data', 'w', newline='') as f:
    line = 0

    if data:
        print(f"ICMP Response Time for host '{host_name}' since {start_date} to {end_date}:")
        for entry in data:
            timestamp = entry["clock"]
            value = entry["value"]
            f.write(str(line) +"," + value + "\n")
            line += 1
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}, ICMP response: {value} ms")
    else:
        print("No data for given time.")

