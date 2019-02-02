import logging

from pf_bot import pf_bot

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='pf_bot.log'
)
logging.debug("Starting pf_bot")
pf_bot.run_bot()
