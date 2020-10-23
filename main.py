import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials 
import json
import time
from bs4 import BeautifulSoup

API_KEY=""

# 変数呼び出し
with open('.env') as f:
    API_KEY = f.read()

channelIdList = []
pageToken = ""

def main(pageToken, loopCount):
    response = getChannelTitle(pageToken)
    if response['error']:
        raise Exception('❌エラー：' + response['error']['message'])
    pageToken = response['nextPageToken']
    count = len(response['items'])
    channelTitle = ""
    channelId = ""
    subscriberCount = ""
    channelUrl = ""

    for num in range(count):
        time.sleep(1)
        channelId = response['items'][num]['snippet']['channelId']
        if channelId not in channelIdList:
            channelIdList.append(channelId)
            channelTitle = response['items'][num]['snippet']['channelTitle']
            channelInfo = getChannelInfo(channelId)
            subscriberCount = int(channelInfo['items'][0]['statistics']['subscriberCount']) / 10000
            if subscriberCount > 1:
                channelUrl = "https://www.youtube.com/channel/" + channelId
                twitterId = getTwitterId(channelUrl)
                writeSheet(loopCount, channelTitle, subscriberCount, channelUrl, twitterId)
                loopCount += 1
    if loopCount < 200:
        main(pageToken, loopCount)

def getChannelTitle(pageToken):
    url = "https://www.googleapis.com/youtube/v3/search?type=video&part=snippet&maxResults=50&order=viewCount&key="
    keyword = "歌ってみた"
    response = requests.get(url + API_KEY + "&q=" + keyword + "&pageToken=" + pageToken)

    return response.json()

def getChannelInfo(channelId):
    url = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id="

    response = requests.get(url + channelId + "&key=" + API_KEY)

    return response.json()

def getTwitterId(channelUrl):
    response = requests.get(channelUrl)
    soup = BeautifulSoup(response.text, 'html.parser')
    twitterId = soup.find(id="links-holder").find_all('a')[0].get('href')
    return twitterId

def writeSheet(loopCount, channelTitle, subscriberCount, channelUrl, twitterId):
    scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('lucky-cosine-243210-1f142f0bce4e.json', scope)
    gc = gspread.authorize(credentials)
    wks = gc.open('pythonで書き込みテスト').sheet1

    # チャンネル名書き込み
    wks.update_acell('A' + str(loopCount), channelTitle)
    print(wks.acell('A' + str(loopCount)))

    # 登録者数書き込み
    wks.update_acell('B' + str(loopCount), subscriberCount)
    print(wks.acell('B' + str(loopCount)))

    # YouTubeUrl書き込み
    wks.update_acell('C' + str(loopCount), channelUrl)
    print(wks.acell('C' + str(loopCount)))
    
    # TwitterID書き込み
    wks.update_acell('D' + str(loopCount), twitterId)
    print(wks.acell('D' + str(loopCount)))

    # TwitterURL書き込み
    wks.update_acell('E' + str(loopCount), "https://twitter.com/" + twitterId)
    print(wks.acell('E' + str(loopCount)))

try:
    main(pageToken, 2)
except Exception as e:
    print(e)

