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
    d = df.iat[0,3] #最終確認日
    t = df.iat[0,2] #通知時刻
    s = df.iat[0,4] #生理初日
    p = df.iat[0,0] #ピル初日
    return [today,d,t,s,p]

def main(a,b):
    USER_ID = info['USER_ID']
    [td, d, t, s, p] = dinf()
    JST = timezone(timedelta(hours=+9), 'JST')
    timestamp = datetime.now(JST)
    H = int(timestamp.strftime("%H"))
    M = int(timestamp.strftime("%M"))
    ys = s[0:4]
    ms = s[5:7]
    ds = s[8:10]
    yp = p[0:4]
    mp = p[5:7]
    dp = p[8:10]
    sdt = ys + '/' + ms + '/' + ds
    pdt = yp + '/' + mp + '/' + dp
    dts = datetime.strptime(sdt,'%Y/%m/%d')
    dtp = datetime.strptime(pdt,'%Y/%m/%d')
    tdt = datetime.strptime(td,'%Y/%m/%d')
    dds = tdt - dts
    ddp = tdt - dtp
    mdp = ddp.days % 28 + 1
    sb = '前回の生理から'+str(dds.days+1)+'日目です。'
    if mdp == 22:
        sa = '前回の生理から'+str(dds.days+1)+'日目。今日から偽薬(休薬)期間です。28錠タイプの場合は気にせず今日も1錠飲みましょう。'
    elif mdp == 28:
        sa = '前回の生理から'+str(dds.days+1)+'日目。今日で偽薬(休薬)期間が終了します。28錠タイプの場合は気にせず今日も1錠飲みましょう。'
    elif mdp >= 23 and mdp <=27:
        sa = '前回の生理から'+str(dds.days+1)+'日目、今日で偽薬(休薬)期間'+str(mdp-21)+'日目です。28錠タイプの場合は気にせず今日も1錠飲みましょう。'
    else:
        sa='前回の生理から'+str(dds.days+1)+'日目。今日も忘れずにピルを飲みましょう。'
    while True:
        if d != td:
            if H == a and M == b:
                messages = TextSendMessage(text = sa)
                line_bot_api.broadcast(messages = messages)
                time.sleep(60)
                [td, d, t, s, p] = dinf()
                JST = timezone(timedelta(hours=+9), 'JST')
                timestamp = datetime.now(JST)
                H = int(timestamp.strftime("%H"))
                M = int(timestamp.strftime("%M")) 
            elif H > a and M == b:
                messages = TextSendMessage(text = "リマインドです。今日も忘れずにピルを飲みましょう。\nこの通知を止める場合は「飲んだ」と送信してください。")
                line_bot_api.broadcast(messages = messages)
                time.sleep(60)
                [td, d, t, s, p] = dinf()
                JST = timezone(timedelta(hours=+9), 'JST')
                timestamp = datetime.now(JST)
                H = int(timestamp.strftime("%H"))
                M = int(timestamp.strftime("%M"))
            else:
                time.sleep(60)
                [td, d, t, s, p] = dinf()
                JST = timezone(timedelta(hours=+9), 'JST')
                timestamp = datetime.now(JST)
                H = int(timestamp.strftime("%H"))
                M = int(timestamp.strftime("%M"))
        else:
            if H <= a:
                if H == a and M ==b:
                    messages = TextSendMessage(text = sb)
                    line_bot_api.broadcast(messages = messages)
                    break
                else:
                    time.sleep(60)
                    [td, d, t, s, p] = dinf()
                    JST = timezone(timedelta(hours=+9), 'JST')
                    timestamp = datetime.now(JST)
                    H = int(timestamp.strftime("%H"))
                    M = int(timestamp.strftime("%M")) 
            else:
                break


[td, d, t, s, p] = dinf()
a = int(t[0:2])
b = int(t[3:5])

if __name__ =="__main__":
    main(a,b)
