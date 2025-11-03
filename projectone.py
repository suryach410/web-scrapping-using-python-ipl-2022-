import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import openpyxl
url = "https://www.iplt20.com/auction/2022"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36")
}
try:
    r = requests.get(url, headers=HEADERS, timeout=15)
except requests.RequestException as e:
    print("Network error while requesting the page:", e)
    sys.exit(1)
if r.status_code != 200:
    print(f"Server returned status code {r.status_code}.")
    print("Response headers:", r.headers)
    sys.exit(1)
soup = BeautifulSoup(r.content, 'lxml')
header_row = soup.select_one('tr.ih-pt-tbl') or soup.find('tr', class_='ih-pt-tbl')
if not header_row:
    header_row = soup.find('thead')
    if header_row:
        header_row = header_row.find('tr')
table_headers = []
if header_row:
    for th in header_row.find_all(['th', 'td']):
        text = th.get_text(strip=True)
        if text:
            table_headers.append(text)
else:
    print("Warning: could not find header row. Will try to infer columns from rows.")
body = soup.select_one('tbody#pointsdata') or soup.find('tbody', id='pointsdata')
if body is None:
    body = soup.find('tbody')
if body is None:
    print("No tbody found on the page. The table may be rendered by JavaScript.")
    print("If the site is JS-driven you'll need a renderer (selenium/playwright) or an API endpoint.")
    sys.exit(1)
rows = body.find_all('tr')
if not rows:
    print("No table rows found inside the selected tbody. The table may be empty or rendered dynamically.")
    sys.exit(1)
table_rows = []
max_cols = 0
for row in rows:
    cols = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
    if not cols:
        continue
    table_rows.append(cols)
    max_cols = max(max_cols, len(cols))
if not table_headers or len(table_headers) != max_cols:
    print("Header columns not found or count mismatch. Creating fallback headers.")
    table_headers = [f"col_{i+1}" for i in range(max_cols)]
normalized_rows = []
for r in table_rows:
    if len(r) < len(table_headers):
        r = r + [""] * (len(table_headers) - len(r))
    elif len(r) > len(table_headers):
        r = r[:len(table_headers)]
    normalized_rows.append(r)
df = pd.DataFrame(normalized_rows, columns=table_headers)
print(df.head(20))
df.to_excel(r"D:\\web scraping.xlsx", index=False)
print("Saved to D:\\web scraping.xlsx")