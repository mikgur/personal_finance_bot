import logging

from pf_model.create_db import create_db
from pf_model.populate_db import populate_db

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='pf_bot.log'
                    )
create_db()
populate_db()
