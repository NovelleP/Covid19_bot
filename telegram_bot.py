import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config.json_rw import config_dict
from requests import get
import matplotlib.pyplot as plt

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
           '\n*Functionality:*\n' \
           '_start_: displays this information message.\n' \
           '\n_covid19_: shows information of the selected countries (Confirmed, Recovered, Deaths). One message per country. Spain is a default country.\n' \
           '\n_chart_: Shows a bar graph with the new cases per day (during the last 30 days). One message per country. Spain is a default country.\n' \
           '\nthis bot get information from this [API](https://documenter.getpostman.com/view/10808728/SzS8rjbc?version=latest)' \
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
            resp_confirmeds = get(f'https://api.covid19api.com/country/{country}/status/confirmed/live')
            last_confirmeds = resp_confirmeds.json()[-1]
            resp_recovereds = get(f'https://api.covid19api.com/country/{country}/status/recovered/live')
            last_recovereds = resp_recovereds.json()[-1]
            resp_deaths = get(f'https://api.covid19api.com/country/{country}/status/deaths/live')
            last_deaths = resp_deaths.json()[-1]
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f'{country.capitalize()}\n\tConfirmed: {last_confirmeds["Cases"]}\n\tRecovered: {last_recovereds["Cases"]}\n\tDeaths: {last_deaths["Cases"]}'
            )
        except Exception as e:
            logger.exception(f'covid19 command fail for country: {country}')


def make_chart(days_dict, country, type):
    dates = [day['Date'] for day in days_dict]
    new_cases_per_day = [day['Cases'] - days_dict[idx - 1]['Cases'] if idx > 0 else day['Cases'] for idx, day in enumerate(days_dict)]
    x_axis = [idx + 1 for idx, _ in enumerate(new_cases_per_day[-30:])]
    y_axis = new_cases_per_day[-30:]
    plt.bar(x_axis, y_axis)
    labels = [date[5:10] for date in dates[-30:]]
    plt.xticks([idx + 1 for idx, _ in enumerate(new_cases_per_day[-30:])], labels, rotation='vertical')
    plt.title(f'{country.capitalize()}: {type} per day in the last 30 days')
    plt.xlabel('Date (mm-dd)')
    plt.ylabel('New cases')
    img_path = r'.\images\img.png'
    plt.savefig(img_path)
    return img_path


def chart_confirmed(update: Update, context: CallbackContext):
    logger.info('chartConfirmed command received')
    countries = context.args if context.args else ['spain']
    for country in countries:
        try:
            resp = get(f'https://api.covid19api.com/dayone/country/{country}/status/confirmed')
            days_dict = resp.json()
            if not days_dict:
                raise Exception('Empty json')
            img_path = make_chart(days_dict, country, 'confirmed')
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
            resp = get(f'https://api.covid19api.com/dayone/country/{country}/status/deaths')
            days_dict = resp.json()
            if not days_dict:
                raise Exception('Empty json')
            img_path = make_chart(days_dict, country, 'deaths')
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
            resp = get(f'https://api.covid19api.com/dayone/country/{country}/status/recovered')
            days_dict = resp.json()
            if not days_dict:
                raise Exception('Empty json')
            img_path = make_chart(days_dict, country, 'recovered')
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
    dispatcher.add_handler(CommandHandler('chartConfirmed', chart_confirmed))
    dispatcher.add_handler(CommandHandler('chartDeaths', chart_deaths))
    dispatcher.add_handler(CommandHandler('chartRecovered', chart_recovered))
    updater.start_polling()
    updater.idle()
