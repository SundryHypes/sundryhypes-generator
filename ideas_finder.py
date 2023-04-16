# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import datetime
import requests
import logging

logger = logging.getLogger('Main_Logger')


def search_term_on_wikipedia(term):
    session = requests.Session()

    request_url = 'https://en.wikipedia.org/w/api.php'

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": term
    }

    response = session.get(url=request_url, params=params)
    data = response.json()

    if data['query']['search'][0]['title'].casefold():
        logger.info(f'Found article "{data["query"]["search"][0]["title"]}" for term "{term}"')
        return [data['query']['search'][0]['title']]
    else:
        logger.info(f'No article found for {term}')


def get_title_of_todays_trending_wiki_articles():
    today = datetime.datetime.now()
    date = today.strftime('%Y/%m/%d')

    logger.info(f'Finding trending article for {date}')

    url = F'https://en.wikipedia.org/api/rest_v1/feed/featured/{date}'

    headers = {
        'User-Agent': 'Sundry Hypes (hello@sundry-hypes.eu)',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    title_of_currently_trending_articles = [
        data['mostread']['articles'][0]['titles']['normalized'],
        data['mostread']['articles'][1]['titles']['normalized'],
        data['mostread']['articles'][2]['titles']['normalized'],
        data['mostread']['articles'][3]['titles']['normalized']
    ]

    return title_of_currently_trending_articles
