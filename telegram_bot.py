import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config.json_rw import config_dict
from requests import get
import matplotlib.pyplot as plt
import numpy as np

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Covid19 Bot')


def start(update: Update, context: CallbackContext):
    logger.info('start command received')
    text = 'covid19 bot provides information about Covid19 pandemic.\n' \
           '\n*Commands:*\n' \
           '\t/start\n' \
           '\t/covid19 country1 country2 ...\n' \
           '\t/chart country1 country2 ...\n' \
           '\t/chartConfirmed country1 country2 ...\n'\
           '\t/chartDeaths country1 country2 ...\n' \
           '\t/chartRecovered country1 country2 ...\n' \\
           '\n*Functionality:*\n' \
           '_start_: displays this information message.\n' \
           '\n_covid19_: shows information of the selected countries (Confirmed, Recovered, Deaths). One message per country. Spain is a default country.\n' \
           '\n_chart_: Shows a bar graph with the confirmed, deaths and recovered cases per day (during the last 30 days). One message per country. Spain is a default country.\n' \
           '\n_chartConfirmed_: Shows a bar graph with the new cases per day (during the last 30 days). One message per country. Spain is a default country.\n' \
           '\n_chartDeaths_: Shows a bar graph with the new deaths per day (during the last 30 days). One message per country. Spain is a default country.\n' \
           '\n_chartRecovered_: Shows a bar graph with the new recovered cases per day (during the last 30 days). One message per country. Spain is a default country.\n' \
           '\nthis bot get information from this [API](https://covid19api.com/)' \
           '\n[My GitHub Account](https://github.com/NovelleP)'
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview = True
    )


def covid19(update: Update, context: CallbackContext):
    logger.info('covid19 command received')
    countries = context.args if context.args else ['spain']
    for country in countries:
        try:
            resp_confirmeds = get(f'https://api.covid19api.com/total/country/{country}/status/confirmed')
            last_confirmeds = resp_confirmeds.json()[-1]
            resp_recovereds = get(f'https://api.covid19api.com/total/country/{country}/status/recovered')
            last_recovereds = resp_recovereds.json()[-1]
            resp_deaths = get(f'https://api.covid19api.com/total/country/{country}/status/deaths')
            last_deaths = resp_deaths.json()[-1]
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f'{country.capitalize()}\n\tConfirmed: {last_confirmeds["Cases"]}\n\tRecovered: {last_recovereds["Cases"]}\n\tDeaths: {last_deaths["Cases"]}'
            )
        except Exception as e:
            logger.exception(f'covid19 command fail for country: {country}')


def make_multiple_barchart(country):
    days = 30
    width = 0.8
    x_axis = np.arange(days)
    factor = (-1, 0, 1)
    type_to_color = {'confirmed': 'blue', 'deaths': 'red', 'recovered': 'green'}
    fig, ax = plt.subplots(figsize=(10,5))
    for idx, type in enumerate(type_to_color):
        resp = get(f'https://api.covid19api.com/total/dayone/country/{country}/status/{type}')
        days_dict = resp.json()
        dates = [day['Date'] for day in days_dict]
        new_cases_per_day = [day['Cases'] - days_dict[idx - 1]['Cases'] if idx > 0 else day['Cases'] for idx, day in enumerate(days_dict)]
        y_axis = new_cases_per_day[-days:]
        ax.bar(x_axis + (factor[idx] * width/3),
                y_axis,
                width=width/3,
                color=type_to_color[type],
                label=type)
    labels = [date[5:10] for date in dates[-days:]]
    ax.set_xticks(x_axis)
    ax.set_xticklabels(labels, rotation='vertical')
    ax.set_title(f'{country.capitalize()}: confirmed/deaths/recovered per day in the last {days} days')
    ax.set_xlabel('Date (mm-dd)')
    ax.set_ylabel(f'New confirmed/deaths/recovered')
    ax.legend()
    fig.tight_layout
    return plt


def chart(update: Update, context: CallbackContext):
    logger.info('chart command received')
    countries = context.args if context.args else ['spain']
    for country in countries:
        try:
            resp = get(f'https://api.covid19api.com/total/dayone/country/{country}/status/confirmed')
            days_dict = resp.json()
            if not days_dict:
                raise Exception('Empty json')
            multi_plt = make_multiple_barchart(country)
            img_path = r'.\images\img.png'
            multi_plt.savefig(img_path)
            context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=open(img_path, 'rb')
            )
            plt.close()
        except:
            logger.exception(f'covid19 command fail for country: {country}')


def make_barchart(days_dict, country, type):
    days = 30
    dates = [day['Date'] for day in days_dict]
    new_cases_per_day = [day['Cases'] - days_dict[idx - 1]['Cases'] if idx > 0 else day['Cases'] for idx, day in enumerate(days_dict)]
    x_axis = [idx + 1 for idx, _ in enumerate(new_cases_per_day[-days:])]
    y_axis = new_cases_per_day[-days:]
    plt.bar(x_axis, y_axis)
    labels = [date[5:10] for date in dates[-days:]]
    plt.xticks([idx + 1 for idx, _ in enumerate(labels)], labels, rotation='vertical')
    plt.title(f'{country.capitalize()}: {type} per day in the last {days} days')
    plt.xlabel('Date (mm-dd)')
    plt.ylabel(f'New {type}')
    return plt


def chart_confirmed(update: Update, context: CallbackContext):
    logger.info('chartConfirmed command received')
    countries = context.args if context.args else ['spain']
    for country in countries:
        try:
            resp = get(f'https://api.covid19api.com/total/dayone/country/{country}/status/confirmed')
            days_dict = resp.json()
            if not days_dict:
                raise Exception('Empty json')
            plt_confirmed = make_barchart(days_dict, country, 'confirmed')
            img_path = r'.\images\img.png'
            plt_confirmed.savefig(img_path)
            context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=open(img_path, 'rb')
            )
            plt.close()
        except:
            logger.exception(f'covid19 command fail for country: {country}')


def chart_deaths(update: Update, context: CallbackContext):
    logger.info('chartDeaths command received')
    countries = context.args if context.args else ['spain']
    for country in countries:
        try:
            resp = get(f'https://api.covid19api.com/total/dayone/country/{country}/status/deaths')
            days_dict = resp.json()
            if not days_dict:
                raise Exception('Empty json')
            plt_deaths = make_barchart(days_dict, country, 'deaths')
            img_path = r'.\images\img.png'
            plt_deaths.savefig(img_path)
            context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=open(img_path, 'rb')
            )
            plt.close()
        except:
            logger.exception(f'covid19 command fail for country: {country}')


def chart_recovered(update: Update, context: CallbackContext):
    logger.info('chartRecovered command received')
    countries = context.args if context.args else ['spain']
    for country in countries:
        try:
            resp = get(f'https://api.covid19api.com/total/dayone/country/{country}/status/recovered')
            days_dict = resp.json()
            if not days_dict:
                raise Exception('Empty json')
            plt_recovered = make_barchart(days_dict, country, 'recovered')
            img_path = r'.\images\img.png'
            plt_recovered.savefig(img_path)
            context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=open(img_path, 'rb')
            )
            plt.close()
        except:
            logger.exception(f'covid19 command fail for country: {country}')


if __name__ == '__main__':
    updater = Updater(token=config_dict['token'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('covid19', covid19))
    dispatcher.add_handler(CommandHandler('chart', chart))
    dispatcher.add_handler(CommandHandler('chartConfirmed', chart_confirmed))
    dispatcher.add_handler(CommandHandler('chartDeaths', chart_deaths))
    dispatcher.add_handler(CommandHandler('chartRecovered', chart_recovered))
    updater.start_polling()
    updater.idle()
