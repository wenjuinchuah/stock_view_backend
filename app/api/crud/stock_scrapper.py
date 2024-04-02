from bs4 import BeautifulSoup

import requests
import csv
import os
import pandas as pd


def scrape_stock_list(board_id: int):
    url = "https://www.klsescreener.com/v2/screener/quote_results"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://www.klsescreener.com",
        "referer": "https://www.klsescreener.com/v2/",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
    }
    data = {"getquote": "1", "board": board_id}
    response = requests.post(url, headers=headers, data=data)

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    stock_list = []
    for row in soup.find_all("tr", class_="list"):
        stock_full_name_td = row.find("td", title=True)
        stock = {
            "stock_full_name": stock_full_name_td["title"],
            "stock_name": stock_full_name_td.find("a").text,
            "stock_code": row.find("td", title="Code").text,
            "is_shariah": (
                True
                if stock_full_name_td.find("span", title="Shariah Compliant")
                else False
            ),
            "category": row.find("td", title="Category").find("small").text,
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
