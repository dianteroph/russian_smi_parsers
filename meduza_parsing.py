#!/usr/bin/env python
# coding: utf-8

# In[12]:


get_ipython().system('jupyter nbconvert --to script meduza_parsing.ipynb')


# In[94]:


import os
import requests
import random 
import json
import locale
import pandas as pd
import certifi 
from pprint import pprint
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import Optional
from selenium import webdriver 
from datetime import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, ElementClickInterceptedException


# In[2]:


locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


# In[4]:


with open('user-agents.txt') as file:
    user_agents = file.read().splitlines()


# In[170]:


class MeduzaParser:
    def __init__(self, phrase_search: str):
        self.phrase_search = phrase_search
        self.headers = {'User-Agent': random.choice(user_agents)}
        self.api = 'https://meduza.io/api/w5/new_search'
        self.proxies = {
                    'http': your_proxy,
                    'https': your_proxy,
        }
        self.request_body = {'term': self.phrase_search,
                             'per_page': 15,
                             'locale': 'ru'}


    def send_request(self, page: int) -> Optional[tuple]:
        '''Get the json responce from the Meduza
        hidden API.
        '''
        params = {
            **self.request_body,
            'page': page
        }
        for attempt in range(5):
            try:
                response = requests.get(self.api, params=params, 
                                        proxies=self.proxies, headers=self.headers, 
                                        verify=False).json()
                print('Got a response')
                return response['documents'], response['_count']

            except Exception as e:
                print(f"Can't get a response for api request - {e}")
                continue

        return None


    def get_page(self, link: str) -> Optional[str]:
        '''Get the html page of article
        from url request.
        '''
        try:
            html = requests.get(link, proxies=self.proxies, 
                                                headers=self.headers).text
            return html

        except Exception as e:
            print(f"Can't get a response from page")
            return None



    def parse_article(self, link: str, data: dict) -> Optional[dict]:
        '''Get article metadata and main text.
        Using BeautifulSoup to parse html page.
        '''
        try:
            tag = data['tag']['name']
        except KeyError:
            tag = 'новости'

        title = data['title'].replace('\xa0', ' ')

        url = 'https://meduza.io/' + link
        html = self.get_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        date = None
        date_tag = soup.find('time', 
                             attrs={'data-testid': 'timestamp'})
        if date_tag:
            date_str = date_tag.text
            if 'назад' not in date_str:
                date = str(datetime.strptime(date_str.split(', ')[1], 
                                                 '%d %B %Y').date())
        text = None
        text_tag = soup.find('div', class_=[
            'GeneralMaterial-module-article', 
            'SlidesMaterial-module-slides'
        ])
        if text_tag:
            text = text_tag.text.replace('\xa0', ' ')


        article_data = {
            'title': title,
            'tag': tag,
            'date': date, 
            'link': url,
            'text': text
        }


        return article_data


    def page_iterate(self) -> list:
        '''Get all articles as a DataFrame with 
        the use of page iteration.
        '''

        articles_data = []
        articles_total = 0
        page = 0

        while True:
            data = self.send_request(page) 
            if data is None:
                print(f'Got None for this request on page {page}')
                page += 1
                continue

            article_data, articles_num = data

            if  articles_num == 0:
                print('No more articles found')
                break

            for link, metadata in article_data.items():
                parsed_data = self.parse_article(link, metadata)
                if parsed_data:
                    articles_data.append(parsed_data)

            articles_total += articles_num
            page += 1

            print(f'Parsed {articles_total} articles')

        return pd.DataFrame(articles_data)









# In[ ]:


data


# In[27]:


get_ipython().system('uv add pyopenssl ndg-httpsclient pyasn1')


# In[174]:


data.to_csv('meduza_usa_articles.csv')


# In[172]:


get_ipython().run_cell_magic('time', '', "parser = MeduzaParser('выборы в сша')\ndata = parser.page_iterate()\n")

