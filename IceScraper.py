#!/usr/bin/env python
# ------------------------------------------------------------------------------
#
#   @brief          Scrapes the AZ ICE website for team schedule information
#
#   @description    This script scrapes the AZ ICE Gilbert website for game and
#                   practice schedules for a specified team and generates an
#                   iCalender file from the collected data.
#
#   @dependencies   Python (>= 3.6), Ics.py (>= 0.4), requests, lxml
#
#   @usage          python IceScraper.py
#
#                   IceScraper.json is used as a configuration file. See
#                   load_config_file for file format details.
#
#   @author         J Graham
#
# ------------------------------------------------------------------------------

import json
import requests
from lxml import html
import ics
from ics import Calendar, Event

# Script configuration data
config = {}

date_map = {'Jan': '01',
            'Feb': '02',
            'Mar': '03',
            'Apr': '04',
            'May': '05',
            'Jun': '06',
            'Jul': '07',
            'Aug': '08',
            'Sep': '09',
            'Oct': '10',
            'Nov': '11',
            'Dec': '12'
           }


# ------------------------------------------------------------------------------
def format_date_time(raw_date: str, raw_time: str) -> str:
    """
    Converts from the date time format on the website to a ISO standard format
    required for the Calendar.  The raw_time string has the start and end times,
    we ignore the end time.

    input format:
    raw_date: 'DDD MMM dd, YYYY'
    raw_time: 'hh:mm AM/PM - hh:mm AM/PM'

    output format:  'YYYYMMDD HH:mm:ss' or 'YYYY-MM-DD HH:mm:ss' depending on
                    ICS version
    """

    # Reformat the date
    tokenized_date = raw_date.split(' ')
    if float(ics.__version__) < 0.5:
        date = tokenized_date[3] + date_map[tokenized_date[1]] + \
               tokenized_date[2].strip(',')
    else:           
        date = tokenized_date[3] + '-' + date_map[tokenized_date[1]] + '-'  + \
               tokenized_date[2].strip(',')

    start_time_data = raw_time.strip().split(' ')

    # Reformat the time
    tokenized_time = start_time_data[0].split(':')

    hour = tokenized_time[0]

    if 'PM' in start_time_data[1]:
        hour = str(int(tokenized_time[0]) + 12)

    time = hour + ':' + tokenized_time[1] + ':00'

    # Return the whole thing as one string

    return date + ' ' + time


# ------------------------------------------------------------------------------
def load_config_file() -> None:
    """
    Loads the IceScraper.json configuration file.

    File format:
    {
        "team": "team_name",
        # The proxies field is optional, define it if you have to go through a
        # proxy server to access the internet.
        "proxies":
        {
            "enable": <true/false>,
            "http": "http://<your.proxy.com:port>",
            "https": "https://<your.proxy.com:port>"
        },
        "practice":
        {
            "url": "http url to top level practice schedule",
            "xpath": "xpath to table cell (td) that contains schedule elements"
        },
        "games":
        {
            "url": "http url to top level practice schedule",
            "xpath": "xpath to table body (tbody) that contains schedule elements"
        },
        "location": "Street address of arena",
        "ics_file": "output_filename.ics"
    }
    """

    global config

    try:
        with open('IceScraper.json', 'r') as f:
            config.update(json.load(f))

    except FileNotFoundError:

        print('ERROR:', filename, 'not found.')
        sys.exit()

    except PermissionError:

        print('ERROR: You do not have sufficient permissions to read', filename)
        sys.exit()

    # If no proxy servers have been defined, set the proxies flag to false

    if 'proxies' not in config:
        config.update({'proxies':{'enable':False}})


# ------------------------------------------------------------------------------
def process_practice_schedule(cal: Calendar) -> None:
    """
    This processes the practice schedule, unfortunately the page formats for the
    practices and the games are completely different and require different
    parsers.
    """

    print('\nPractice')
    print('========\n')

    # Determine if we need to use a proxy then request the target web page.

    if True == config['proxies']['enable']:
        page = requests.get(config['practice']['url'], proxies=config['proxies'])
    else:
        page = requests.get(config['practice']['url'])

    # Parse the document into a HTML document
    tree = html.fromstring(page.content)

    # Find all the td elements with schedule data.  The xpath was determined by
    # inspecting elements in Chrome/Firefox and copying the xpath.
    nodes = tree.xpath(config['practice']['xpath'])
    for node in nodes:

        element = node.xpath('@title|@data-content')

        # print('type: ', type(element), ', len:', len(element))

        if 0 < len(element):

            # raw_title is the team match up i.e. 'TEAM1 vs TEAM2'
            # details is a list 0 = date, 1 = time, 2 = location
            # - date 'DDD MMM dd, YYYY'
            # - time 'hh:mm AM/PM - hh:mm AM/PM'
            # - location 'Location: <North/South> Pole'

            raw_title = str(element[0])
            details = str(element[1]).split('<br>')

            # Filter on our team

            if config['team'].lower() in raw_title.lower():

                # Pretty print the team match up.

                teams = raw_title.split(' vs ')
                pretty_title = teams[0].title() + ' vs ' + teams[1].title()

                # Reformat the date time string

                event_time = format_date_time(details[0], details[1])

                rink = details[2].strip('Location: ')

                print('{:24} - {} on {}'.format(pretty_title, event_time, rink))

                event = Event()

                event.name = pretty_title + ' (prac)'
                event.begin = event_time
                event.duration = {'hours': 1}
                event.description = rink
                event.location = config['location']

                cal.events.append(event)


# ------------------------------------------------------------------------------
def process_game_schedule(cal: Calendar) -> None:
    """
    This processes the game schedule, unfortunately the page formats for the
    practices and the games are completely different and require different
    parsers.
    """

    print('\nGames')
    print('=====\n')

    # Determine if we need to use a proxy then request the target web page.

    if True == config['proxies']['enable']:
        page = requests.get(config['practice']['url'], proxies=config['proxies'])
    else:
        page = requests.get(config['practice']['url'])

    # Parse the document into a HTML document
    tree = html.fromstring(page.content)

    # Find the table body with schedule data.  The xpath was determined by
    # inspecting elements in Chrome/Firefox and copying the xpath.
    nodes = tree.xpath(config['practice']['xpath'])

    row_num = 0
    for node in nodes:

        # The schedule data we want is in every other row.  Each cell within
        # that row contains a separate piece of schedule data. So the relative
        # xpath we need to use is /tr[row_num]/td[cell_num]/div

        row_num += 1

        # Skip even numbered rows as they contain hidden table data, its data we
        # actually want but it is in a form harder to parse.

        if 0 == (row_num % 2):
            continue

        date      = node.xpath('//tr[{}]/td[1]/div/text()'.format(row_num))
        time      = node.xpath('//tr[{}]/td[2]/div/text()'.format(row_num))
        home_team = node.xpath('//tr[{}]/td[3]/div/text()'.format(row_num))
        away_team = node.xpath('//tr[{}]/td[4]/div/text()'.format(row_num))
        rink      = node.xpath('//tr[{}]/td[5]/div/text()'.format(row_num))

        # Not sure why but there seem to be way more nodes than there are rows
        # in the table, so we just do a quick check here.  If date is empty then
        # we have hit the end of the schedule and can exit.

        if not date:
            break

        # print(date[0], time[0], home_team[0], away_team[0], rink[0])

        if config['team'].lower() == home_team[0].lower().strip() or \
           config['team'].lower() == away_team[0].lower().strip():

            # Pretty print the team match up.

            pretty_title = home_team[0].title().strip() + ' vs ' + \
                           away_team[0].title().strip()

            # Reformat the date time string

            start_time = time[0].split('-')

            event_time = format_date_time(date[0], start_time[0])

            print('{:24} - {} on {}'.format(pretty_title, event_time, rink[0]))
            event = Event()
            event.name = pretty_title + ' (game)'
            event.begin = event_time
            event.duration = {'hours': 1}
            event.description = rink[0]
            event.location = config['location']
            cal.events.append(event)


# ------------------------------------------------------------------------------
def ice_scraper() -> None:

    load_config_file()

    # Create our calendar
    cal = Calendar()
    cal.events = []

    process_practice_schedule(cal)
    process_game_schedule(cal)

    # Write the calendar out to a file.
    if 0 < len(cal.events):
        try:
            with open(config['ics_file'], 'w') as f:
                f.writelines(cal)

        except PermissionError:

            print('ERROR: You do not have sufficient permissions to write to', filename)
            sys.exit()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    ice_scraper()
