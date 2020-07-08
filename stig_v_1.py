# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 01:09:58 2020

@author: System Meltdown
@program_name :StiG - Subtitle Grabber
@ver : 1.0
"""


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import wx
import pandas as pd
import random
import requests, zipfile, io


#driver = webdriver.PhantomJS(executable_path='D:/projects/Tools/phantom/bin/phantomjs')
#driver.get('https://youtube.com')

def get_path(wildcard):
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Select the Movie', wildcard=wildcard, style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    return path

full_path = get_path('*')
path_list = []
path_list = full_path.split("\\")
path_list = path_list[:-1]
save_path = "/".join(path_list)

m = full_path
m = m.split("\\")
n = m[-1]
n = n.split(".")
n = n[:-1]

letter_counter = 0
for i in n:
    if (i[0].isnumeric()) and (i[-1] == "p"):
        break
    else:
        letter_counter += 1
movie_name = n[:letter_counter]
movie_name = " ".join(movie_name)


options = webdriver.ChromeOptions()

prefer_ = {'download.default_directory': save_path,
         'profile.default_content_settings.popups': 0,
         'directory_upgrade': True}

options.add_experimental_option('prefs',prefer_)
options.add_argument("disable-gpu")
options.add_argument("headless")
driver = webdriver.Chrome(executable_path = 'D:\projects\Tools\Chromedriver.exe',chrome_options = options)
driver.get("https://imdb.com")
searchbox = driver.find_element_by_xpath('//*[@id="suggestion-search"]')
searchbox.send_keys(movie_name+Keys.ENTER)

html = driver.page_source

soup = BeautifulSoup(html)
result = soup.find("table")
result = result.find("a")
links = result.get("href")

count = 0
letter_counter = 0
for i in links[6:]:
    #print (i)
    letter_counter +=1
    if i == "/":
        count+=1
    if count == 2:
        break
letter_counter
movie_id = links[6:(letter_counter+6)]        

url = "https://yts-subs.com/movie-imdb"+movie_id
req = requests.get(url)
soup = BeautifulSoup(req.content)
container = soup.find_all("tr",class_="high-rating")
#rating
#language
#link
rating_list = []
language_list = []
link_list = []
rating_list.clear()
language_list.clear()
link_list.clear()
yifi = "https://www.yifysubtitles.com"
for i in container:
    language = i.find("span",class_="sub-lang")
    languages = language.text
    rating = i.find("td",class_="rating-cell")
    rating = rating.span.text
    rating = int(rating)
    link = i.find("a",class_="subtitle-download")
    link = link.get("href")
    links = link.split("/")
    link = links[-1]
    link = yifi +"/"+"subtitle"+"/"+ link +".zip"
    
    rating_list.append(rating)
    language_list.append(languages)
    link_list.append(link)

data = {"Rating" :rating_list, "Language" : language_list, "Link" : link_list }
df = pd.DataFrame(data)
df = df[df.Language == "English"]
max_rating = df[df.Rating == (df.Rating.max())]
if len(max_rating)>1:
    indices = max_rating.index.values
    max_rating = random.choice(indices)
    max_rating = df[df.index == max_rating]
subtitle_link = max_rating.iloc[0][2]
r = requests.get(subtitle_link)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(save_path)








