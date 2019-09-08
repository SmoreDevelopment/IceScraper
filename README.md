# Overview

This is a python script scrapes the AZ ICE Gilbert website for game and practice schedules for a specified team.  An iCalender file is generated from the collected data.

# Requirements

- Python - 3.6 or greater
- Ics.py - 0.4 & 0.5
- requests - 2.21.0
- lxml - 4.3.3.0


# Usage

## Configuration

1. Configure the JSON configuration file `IceScraper.json`.
   1. `team`: `string` - The team name of the team. ***(case insensitive)***
   1. `proxies`: `dictionary` - List or proxy servers, this list is optional you only need to include it if you need to use a proxy server to access the internet.
      1. `enable`: `boolean` - Enables or disables the use of a proxy server to access the internet.
      1. `http`: `string` - http proxy server and port number.  ***(must include the `http://`)***
      1. `https`: `string` - secure https proxy server and port number.  ***(must include the `https://`)***
   1. `practice`: `dictionary` - Information about the practice schedule
      1. `url`: `string` - URL of the practice schedule page for the league ***(i.e. 8U Mite Practices)***
      1. `xpath`: `string` - XPATH to the first table cell `<td>` element that contains schedule information, this path was determined by inspecting the document in Firefox/Chrome. 
   1. `games`: `dictionary` - Information about the game schedule
      1. `url`: `string` - URL of the game schedule page for the league ***(i.e. 8U Mite Games)***
      1. `xpath`: `string` - XPATH to the table body `<tbody>` element that contains schedule information, this path was determined by inspecting the document in Firefox/Chrome.
   1. `location`: `string` - Street address of the arena.
   1. `ics_file`: `string` - Filename of the output iCalander file.
1. Call the script: `python IceScraper.py`
 
Example configuration file:

```json
{
    "team": "team_name",
    "proxies":
    {
        "enable": <true/false>,
        "http": "http://your.proxy.com:port",
        "https": "https://your.proxy.com:port"
    },
    "practice":
    {
        "url": "https://gilbert.frontline-connect.com/leagueschedule.cfm?fac=gilbert&facid=1&Sched_id=356",
        "xpath": "/html/body/div/div[2]/div[1]/div/form/div/div[2]/div[1]/table/tbody/tr/td"
    },
    "games":
    {
        "url": "https://gilbert.frontline-connect.com/leagueschedule.cfm?fac=gilbert&facid=1&Sched_id=360",
        "xpath": "/html/body/div/div[2]/div[1]/div/form/div/div[2]/div/table/tbody"
    },
    "location": "Street address of arena",
    "ics_file": "output_filename.ics"
}
```



