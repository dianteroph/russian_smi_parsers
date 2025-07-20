#!/usr/bin/env python
# coding: utf-8

# In[20]:


get_ipython().system('jupyter nbconvert --to script config_template.ipynb')
import requests
import random
import pandas as pd
import urllib.parse
import undetected_chromedriver as uc
from time import sleep
from datetime import datetime
from math import ceil
from typing import Optional
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC


# In[2]:


with open('user-agents.txt') as file:
    user_agents = file.read().splitlines()


# In[47]:


class KommersantParser:
    def __init__(self, 
                 query: str, 
                 date_from: str, 
                 date_to: str):

        self.base_url = 'https://www.kommersant.ru/search/results?'
        self.df = date_from
        self.dt = date_to
        self.params = {
            'search_query': query 
        }

    def get_driver(self):
        '''Getting ChromeDriver to imitate 
        user behaviour in browser.
        '''
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        driver = uc.Chrome(version_main=138, options=options)
        return driver



    def get_links(self, url: str) -> Optional[list]:
        '''Getting articles links on website 
        page.
        '''
        links = []
        driver = self.get_driver()

        try:
            driver.delete_all_cookies() 
            driver.get(url)
            wait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 
                                                  'article.uho')))
            articles = driver.find_elements(
                By.CSS_SELECTOR, 'article.uho')

        except TimeoutException:
            return None

        for article in articles:
            link = article.find_element(
                By.CSS_SELECTOR, 'a.uho__link').get_attribute('href')
            links.append(link)

        driver.close()   
        return links


    def select_part(self, soup, css_selector: str) -> Optional[str]:
        page_object = soup.select_one(
            css_selector).text.strip()
        return page_object if page_object else ''


    def get_metadata(self, article_link: str) -> dict:
        '''Getting the metadata and article 
        text.
        '''
        html = requests.get(article_link).text
        soup = BeautifulSoup(html, 'html.parser')

        title = self.select_part(soup, 
                                 'h1.doc_header__name')
        date = self.select_part(soup, 
                                 'time.doc_header__publish_time')
        text = self.select_part(soup, 
                                 'div.doc__body')

        article_data = {
            'title': title,
            'date': date,
            'link': article_link,
            'text': text
        }

        return article_data


    def iterate_pages(self) -> list:
        '''Iteration through the date 
        range and pages
        '''
        article_links = []
        dates = pd.date_range(
            self.df, self.dt, freq='31D')
        dates = dates.strftime('%Y-%m-%d').tolist()

        for i in tqdm(range(1, len(dates))):
            print(dates[i])
            params = {
                **self.params,
                'datestart': dates[i-1],
                'dateend': dates[i]
            }

            for page in range(1, 101):
                request_payload = {
                    **params,
                    'page': page
                }
                url = self.base_url + urllib.parse.urlencode(
                    request_payload)
                links = self.get_links(url)

                if links:
                    article_links.extend(links)
                else:
                    break

        print(f'Found {len(article_links)} article links.')          
        return article_links


    def get_articles(self) -> pd.DataFrame:
        '''Getting the final results
        with articles in DataFrame
        '''
        articles_data = []
        article_links = self.iterate_pages()
        for link in article_links:
            data = self.get_metadata(link)
            if data:
                articles_data.append(data)

        return pd.DataFrame(articles_data)




# In[39]:


parser = KommersantParser('протесты', '2022-07-16', '2022-09-16')
data = parser.get_articles()

