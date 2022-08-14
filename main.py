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

df_old = pd.read_csv('/Users/ilakozin/PycharmProjects/Beatport_top100_bot/Beatport_top100_releases.csv')

# df_old = df_old.drop(labels=[1,2,3], axis=0)
df_old.columns = (['Unnamed: 0', 'position_old', 'title', 'lable', 'link'])

new_releases_df = df.merge(df_old, how='left', on=['title', 'lable', 'link'], indicator=True) \
    .query("_merge == 'left_only'") \
    .drop(['_merge', 'Unnamed: 0', 'position_old'], axis=1)

n = 0

for index, row in new_releases_df.iterrows():
    t = row['title']
    l = row['lable']
    p = row['position']
    li = 'https://www.beatport.com' + row['link']
    n = n + 1
    s = (f"Название:        {t}\nЛейбл:          {l}\nМесто в Топ100:    {p}\nСсылка: {li}\n\n\n")
    bot.send_message(chat_id= os.getenv('CHAT_ID'), text=s)
if n > 0:
    df.to_csv('/Users/ilakozin/PycharmProjects/Beatport_top100_bot/Beatport_top100_releases.csv')
