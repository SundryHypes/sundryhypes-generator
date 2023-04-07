# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import json
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

logger = logging.getLogger('Main_Logger')


def add_entry_to_record(title: str):
    logger.info(f'Adding "{title}" to archive record')

    with open('archive/record.json', 'r') as file:
        record = json.load(file)

        today = datetime.today()
        year = f'{today.year}'
        month = format(today, '%B')

        new_entry = {
            'title': title,
            'episode_number': 0
        }

        if year not in record:
            record = {year: {month: [new_entry]}}
        elif month not in record[year]:
            record[year][month] = [new_entry]
        else:
            record[year][month].append(new_entry)

        episode_number = max(episode['episode_number'] for episode in record[year][month]) + 1
        record[year][month][-1]['episode_number'] = episode_number

    with open('archive/record.json', 'w') as file:
        json.dump(record, file, indent=1)

    return episode_number


def is_topic_in_month(month, record, topic, year):
    if year not in record:
        return False

    if month not in record[year]:
        return False

    for episode in record[year][month]:
        if topic == episode['title']:
            return True

    return False


def check_if_topic_discussed_recently(title: str = None):
    logger.info(f'Checking if "{title}" in archive')

    file = open('archive/record.json')
    record = json.load(file)

    today = datetime.today()
    shift_back_one_month = datetime.now() - relativedelta(months=1)

    year = today.year
    shift_back_one_month_year = shift_back_one_month.year
    current_month = format(today, '%B')
    last_month = format(shift_back_one_month, '%B')

    topic_found = is_topic_in_month(current_month, record, title, year)
    topic_found = topic_found or is_topic_in_month(
        last_month, record, title, shift_back_one_month_year)

    file.close()
    return topic_found

