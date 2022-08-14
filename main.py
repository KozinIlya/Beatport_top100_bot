import time
import telegram
import pandas as pd
import requests
from bs4 import BeautifulSoup
import settings
import os

url = 'https://www.beatport.com/top-100-releases'
request = requests.get(url)
soup = BeautifulSoup(request.text, 'html.parser')


def fun(s):
    t = s.find_all('li', class_="bucket-item ec-item horz-release")
    title_top100 = []
    position_top100 = []
    lable_top100 = []
    link_top100 = []

    for i in t:
        title = i.find('p', class_='buk-horz-release-title').text
        position = i.find('p', class_="buk-horz-release-num").text
        lable = i.find('p', class_="buk-horz-release-labels").text
        link = i.find('a', href=True)['href']

        title_top100.append(title)
        position_top100.append(position)
        lable_top100.append(lable)
        link_top100.append(link)
    s = {position: position_top100, title: title_top100, lable: lable_top100, link: link_top100}
    df = pd.DataFrame(s)
    df.columns = ['position', 'title', 'lable', 'link']
    df['lable'] = df['lable'].str.replace("\n", "")
    df.set_index('position')
    return df


while request.status_code != 200:
    time.sleep(60)
    print('sleep')
df = fun(soup)

bot = telegram.Bot(token=os.getenv('TOKEN'))

