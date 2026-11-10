import requests
import datetime
import csv
from pathlib import Path
import os
import json

def fetch_connections(origin,destination):
    url = "https://api.irail.be/connections/"
    params = {
        "from": origin,
        "to": destination,
        "format": "json",
    }
    headers = {
        "User-Agent": "irailTracker/1.0 (github.com/NazarCode)"
    }
    response = requests.get(url,params,headers=headers,timeout=(3,8))
    if response.ok:
        connections = response.json()["connection"]
        return connections
    elif response.status_code == 400:
        raise requests.exceptions.HTTPError("Requested stop not found. Check the spelling or contact the API provider at docs.irail.be")
    else:
        raise requests.exceptions.HTTPError(f"{response.status_code, response.text}")

def parse_connections(connection):
    train_info = {
        "train_name": connection['departure']['vehicleinfo']['shortname'],
        "scheduled_departure_time": datetime.datetime.fromtimestamp(int(connection['departure']['time'])).strftime("%H:%M"),
        "delay": int(connection['departure']['delay']) // 60, # Floor division is the pragmatic choice here
        "canceled": bool(int(connection['departure']['canceled'])), # Boolean representation for better readability
    }
    return train_info

def print_next_trains(origin,destination,number=3):
    connections = fetch_connections(origin,destination)
    next_trains_ls = []
    for i in range(number):
        train_info = parse_connections(connections[i])
        if train_info['delay'] == 0:
            delay = "on time"
        else:
            delay = f"+{train_info['delay']} min"
        if train_info['canceled']:
            canceled = "CANCELLED"
        else:
            canceled = ""
        row_info = f"{train_info['train_name']} {train_info['scheduled_departure_time']} {delay} {canceled}"
        next_trains_ls.append(row_info)
    for train in next_trains_ls:
        print(train)

def get_info_rows(connections):
    rows = []
    for connection in connections:
        rows.append(parse_connections(connection))
    return rows

def save_connections(rows,path=Path.cwd()):
    if len(rows) == 0:
        print("No connections found")
        return
    file_path = f"{path}/train_info.csv"
    if not os.path.exists(file_path) or (os.path.getsize(file_path) == 0):
        header_needed = True
    else:
        header_needed = False
    with open(file_path, "a", newline='') as csvfile:
        for row in rows:
            datetime_now = datetime.datetime.now()
            row["date"] = datetime_now.strftime('%d/%m/%y')
            row["time"] = datetime_now.strftime('%T')
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if header_needed:
            writer.writeheader()
        writer.writerows(rows)

def test_function(path=Path.cwd()):
    with open(path / "sample_response.json","r",encoding="utf-8") as f:
        sample = json.load(f)
        con_sample = sample[0]
        info_sample = parse_connections(con_sample)
        assert isinstance(info_sample['canceled'],bool) and info_sample['canceled'] == int(con_sample['departure']['canceled'])
        assert info_sample['delay'] == int(con_sample['departure']['delay']) // 60
        assert datetime.datetime.strptime(info_sample['scheduled_departure_time'],"%H:%M") 

if __name__ == "__main__":
    try:
        rows = get_info_rows(fetch_connections("Brussels-Central","Leuven"))
        save_connections(rows)
    except requests.exceptions.RequestException as e:
        print(e)

    #with open(Path.cwd() / "sample_response.json", "w", encoding="utf-8") as sample_response:
    #    sample_response.write(json.dumps(fetch_connections("Brussels-Central","Leuven")))

