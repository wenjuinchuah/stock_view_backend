import json


import requests
import csv
import os
import pandas as pd
from bs4 import BeautifulSoup


def scrape_stock_list():
    url = "https://klse.i3investor.com/wapi/web/stock/listing/datatables"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://klse.i3investor.com",
        "referer": "https://klse.i3investor.com/web/stock/list",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
    }
    json_data = {
        "dtDraw": 1,
        "start": 0,
        "order": [
            {
                "column": 1,
                "dir": "asc",
            },
        ],
        "page": 0,
        "size": 1500,
        "marketList": [
            "ACE",
            "LEAP",
            "MAIN",
        ],
        "sectorList": [],
        "subsectorList": [],
        "type": "",
        "stockType": "",
    }
    response = requests.post(url, headers=headers, json=json_data)
    response_json = json.loads(response.text)

    stock_list = []
    for data in response_json["data"]:
        stock = {
            "stock_code": data[14],
            "stock_name": data[13],
            "stock_full_name": BeautifulSoup(data[1], "html.parser")
            .find("a")
            .find_next_sibling("br")
            .next_sibling,
            "category": data[10],
            "is_shariah": False,  # Temporary setting all to False
        }
        stock_list.append(stock)

    # Write/Append to CSV
    file_path = "app/assets/stock_list.csv"
    if not os.path.isfile(file_path):
        # Write to CSV
        with open(file_path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=stock_list[0].keys())
            writer.writeheader()
            writer.writerows(stock_list)
    else:
        # Read existing data
        existing_data = pd.read_csv(file_path)
        new_data = pd.DataFrame(stock_list)

        # Check if stock exists in existing data
        merged_data = pd.concat([existing_data, new_data])
        merged_data.drop_duplicates(subset=["stock_code"], keep="first", inplace=True)

        # Write the updated data back to the CSV file
        merged_data.to_csv(file_path, index=False)
