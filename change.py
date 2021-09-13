import yaml
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import datetime
import schedule

def auth():
    SP_CREDENTIAL_FILE = 'secret.json'
    SP_SCOPE = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    SP_SHEET_KEY = '10kETiIVNeVsqqeCgAhMYMmN3FOZeOlh2xWzwA8ED-tA'
    SP_SHEET = 'sheet'

    credentials =ServiceAccountCredentials.from_json_keyfile_name(SP_CREDENTIAL_FILE, SP_SCOPE)
    gc = gspread.authorize(credentials)

    worksheet = gc.open_by_key(SP_SHEET_KEY).worksheet(SP_SHEET)
    return worksheet
  
worksheet = auth()
df = pd.DataFrame(worksheet.get_all_records())
t = df.iat[0,2]
a = int(t[0:2])
b = int(t[3:5])
if a < 8:
  a = a + 15
else:
  a = a - 9

a=str(a)
b=str(b)
s = """
name: chat_hatbot

on:
  schedule:
    - cron: '"""+b+""" """+a+""" * * *'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2
      - name: Set up Python 3.8
        uses: actions/setup-python@v1
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install line-bot-sdk
      - name: Run script
        run: |
          python main.py

"""
with open("main.yml", "w") as yf:
    yf.write(s)
