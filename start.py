import logging
import os
import sys
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, MessageHandler
import pandas as pd
from pandas_datareader import data as web
from datetime import datetime, timedelta

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Test Mode
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


# Commands
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/buy + ticker para ver cotação atual;\n/info para mais informações sobre o criador.')


def buy(update: Update, context: CallbackContext) -> None:
    data = context.args[0]
    ticker = data.upper()
    stock = ticker + '.SA'
    try:
        df = pd.DataFrame()
        delayed = datetime.now() - timedelta(minutes=15, hours=3)
        df = web.DataReader(stock, data_source='yahoo', start='01-11-2020')
        p_today = (df.iloc[-1][5])
        p_yesterday = (df.iloc[-2][5])
        var = ((p_today - p_yesterday) / p_yesterday) * 100
        msg = str(
            f'''Hora: {str(delayed.hour)}:{'%02d'%(int(delayed.minute))} (15-min delay)\nCotação {ticker}: R${round(p_today, 2)} ({round(var, 2)}%)''')
    except:
        msg = 'Não encontrado.'

    update.message.reply_text(msg)


def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Comando não encontrado!\nTente /buy + ticker para cotação")


def info(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Criado por Cristian Webber\nGit: cristianwebber\nTwitter: @aicristian')


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('buy', buy))
    updater.dispatcher.add_handler(CommandHandler('info', info))
    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    run(updater)