import yaml
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from datetime import datetime
import schedule
import time
import json
from linebot import LineBotApi
from linebot.models import TextSendMessage

file = open('info.json','r')
info = json.load(file)
CHANNEL_ACCESS_TOKEN = info["CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

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

def dinf():
    worksheet = auth()
    df = pd.DataFrame(worksheet.get_all_records())
    timestamp = datetime.now()
    today = timestamp.strftime("%Y/%m/%d")
    d = df.iat[0,3]
    t = df.iat[0,2]
    return [today,d,t]

def main(a,b):
    USER_ID = info['USER_ID']
    [td, d,t]=dinf()
    timestamp = datetime.now()
    H = int(timestamp.strftime("%H"))
    M = int(timestamp.strftime("%M"))
    while True:
        if d != td:
            if H > a and M == b:
                messages = TextSendMessage(text = "今日も忘れずにピルを飲みましょう。")
                line_bot_api.push_message(USER_ID, messages = messages)
                [td, d,t]=dinf()
                timestamp = datetime.now()
                H = int(timestamp.strftime("%H"))
                M = int(timestamp.strftime("%M"))
                time.sleep(60)
            else:
                [td, d,t]=dinf()
                timestamp = datetime.now()
                H = int(timestamp.strftime("%H"))
                M = int(timestamp.strftime("%M"))
                time.sleep(60)
        else:
            break


[td,d,t]=dinf()
a = int(t[0:2])
b = int(t[3:5])
if a < 8:
  a = a + 14
else:
  a = a - 10
b=b-1

if __name__ =="__main__":
    main(a,b)
