# covid19_bot
Telegram bot develop in Python3 that proived information about coronavirus

covid19 bot provides information about Covid19 pandemic.

## Commands:
* ```start```
* ```covid19 country1 country2 ...```
* ```chart country1 country2 ...```
* ```chartConfirmed country1 country2 ...```
* ```chartDeaths country1 country2 ...```
* ```chartRecovered country1 country2 ...```

## Functionality:
* __start__: displays this information message.
* __covid19__: shows information of the selected countries (Confirmed, Recovered, Deaths). One message per country. Spain is a default country.
* __chartConfirmed__: Shows a bar graph with the confirmed, deaths and recovered cases per day (during the last 30 days). One message per country. Spain is a default country.
* __chartConfirmed__: Shows a bar graph with the new cases per day (during the last 30 days). One message per country. Spain is a default country.
* __chartDeaths__: Shows a bar graph with the new deaths per day (during the last 30 days). One message per country. Spain is a default country.
* __chartRecovered__: Shows a bar graph with the new recovered per day (during the last 30 days). One message per country. Spain is a default country.

##### this bot get information from this [API](https://covid19api.com/)
