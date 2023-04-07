# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import datetime
import requests
import logging

logger = logging.getLogger('Main_Logger')


def get_title_of_todays_trending_wiki_article():
    today = datetime.datetime.now()
    date = today.strftime('%Y/%m/%d')

    logger.info(f'Finding trending article for {date}')

    url = F'https://en.wikipedia.org/api/rest_v1/feed/featured/{date}'

    headers = {
        'User-Agent': 'xPlain (severinjoburg@gmail.com)',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    title_of_currently_trending_article = data['mostread']['articles'][0]['titles']['normalized']

    return title_of_currently_trending_article
