#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
import random
import pandas as pd
from time import sleep
from datetime import datetime
from math import ceil
from typing import Optional
from bs4 import BeautifulSoup


# In[3]:


with open('user-agents.txt') as file:
    user_agents = file.read().splitlines()


# In[4]:


base_url = 'https://russian.rt.com'


# In[5]:


class RussiaTodayParser:

    def __init__(self, query, date_from, date_to):
        self.api = f'{base_url}/search'
        self.headers = {'User-Agent': random.choice(user_agents)}
        self.date_from = date_from
        self.date_to = date_to
        self.params = {
            'q': query,
            'df': date_from,
            'dt': date_to,
            'pageSize': 100,
            'format': 'json'
        }

    def get_response(self, page: int) -> Optional[dict]:
        '''Sending the request to the RT api.
        Geting the json dict with data.
        '''
        request_payload = {
                **self.params, 
                'page': page
            }

        for attempt in range(3):
            try:
                response = requests.get(self.api, headers=self.headers, 
                                            params=request_payload, verify=False).json()
                return response

            except Exception as e:
                print(f'Error sending the request - {e}, have another try')

        return None


    def get_article_text(self, link: str) -> Optional[str]:
        '''Get the main text part
        of article.
        '''
        try:
            html = requests.get(link).text
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.find('div', class_='article__text').text
            return text
        except:
            print(f'The current object is not an article - {link}')
            return None



    def get_metadata(self, article: dict) -> dict:
        '''Get metadata of article'''
        link = f'{self.base_url}{article['href']}'
        text = self.get_article_text(link)

        category = article['category'] if 'category' in article else None
        date = str(datetime.fromtimestamp(
                int(article['date'])).date())

        article_data = {
            'id': article['id'],
            'link': link,
            'date': date,
            'type': article['type'],
            'category': category,
            'title': article['title'],
            'summary': article['summary'],
            'text': text 
        }

        return article_data


    def iterate_pages(self) -> pd.DataFrame:
        '''Iteration throught pages
        with the final number of articles.
        '''
        self.articles_data = []
        articles_num = self.get_responce(1)['totalCount']
        print(f'Number of articles: {articles_num}')
        total_count = ceil(articles_num / 100)

        for page in range(1, total_count + 1):
            response = self.get_response(page) 
            if response:
                for article in response['docs']:
                    data = self.get_metadata(article)
                    self.articles_data.append(data)

        return pd.DataFrame(self.articles_data)






