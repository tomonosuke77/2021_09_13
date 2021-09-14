import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from datetime import datetime, timedelta, timezone, date
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
    JST = timezone(timedelta(hours=+9), 'JST')
    timestamp = datetime.now(JST)
    today = timestamp.strftime("%Y/%m/%d")
    d = df.iat[0,3]
    t = df.iat[0,2]
    s = df.iat[0,4]
    return [today,d,t,s]

def main(a,b):
    USER_ID = info['USER_ID']
    [td, d, t, s] = dinf()
    JST = timezone(timedelta(hours=+9), 'JST')
    timestamp = datetime.now(JST)
    H = int(timestamp.strftime("%H"))
    M = int(timestamp.strftime("%M"))
    y=s[0:4]
    m=s[5:7]
    d=s[8:10]
    sdt=y + '/' + m + '/' + d
    dt=datetime.strptime(sdt,'%Y/%m/%d')
    tdt=datetime.strptime(td,'%Y/%m/%d')
    dd=tdt-dt
    sa='前回の生理から'+str(dd.days+1)+'日目。今日も忘れずにピルを飲みましょう。'
    while True:
        if d != td:
            if H == a and M == b:
                messages = TextSendMessage(text = sa)
                line_bot_api.broadcast(messages = messages)
                time.sleep(60)
                [td, d, t, s] = dinf()
                JST = timezone(timedelta(hours=+9), 'JST')
                timestamp = datetime.now(JST)
                H = int(timestamp.strftime("%H"))
                M = int(timestamp.strftime("%M")) 
            elif H > a and M == b:
                messages = TextSendMessage(text = "リマインドです。今日も忘れずにピルを飲みましょう。")
                line_bot_api.broadcast(messages = messages)
                time.sleep(60)
                [td, d, t, s] = dinf()
                JST = timezone(timedelta(hours=+9), 'JST')
                timestamp = datetime.now(JST)
                H = int(timestamp.strftime("%H"))
                M = int(timestamp.strftime("%M"))
            else:
                time.sleep(60)
                [td, d, t, s] = dinf()
                JST = timezone(timedelta(hours=+9), 'JST')
                timestamp = datetime.now(JST)
                H = int(timestamp.strftime("%H"))
                M = int(timestamp.strftime("%M"))
        else:
            break


[td, d, t, s] = dinf()
a = int(t[0:2])
b = int(t[3:5])

if __name__ =="__main__":
    main(a,b)
