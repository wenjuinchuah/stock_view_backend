# import csv
# from bs4 import BeautifulSoup


# class StockScrape:
#     def scrape():
#         with open("src/assets/klse_stocks.html", "r", encoding="utf-8") as file:
#             html_content = file.read()

#         soup = BeautifulSoup(html_content, "html.parser")
#         data = []

#         # Find the table containing stock information
#         table = soup.find(
#             "table",
#             class_="table table-sm table-theme table-hover tablesorter-bootstrap tablesorter",
#         )

#         if table:
#             rows = table.find_all("tr")

#             for row in rows[1:]:  # Skip the header row
#                 columns = row.find_all("td")
#                 if len(columns) >= 2:
#                     stock_name = columns[0].a.text
#                     is_shariah = "[s]" in columns[0].text
#                     stock_code = columns[1].text.strip()
#                     category_small = columns[2].find("small")
#                     category = category_small.text.strip() if category_small else ""

#                     data.append([stock_name, stock_code, is_shariah, category])

#             # Save data as CSV
#             with open("klse_stocks.csv", "w", newline="", encoding="utf-8") as csvfile:
#                 csv_writer = csv.writer(csvfile)
#                 csv_writer.writerow(
#                     ["stock_name", "stock_code", "is_shariah", "category"]
#                 )
#                 csv_writer.writerows(data)
