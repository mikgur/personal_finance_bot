personal_finance_bot
=======

personal_finance_bot это телеграм бот, который помогает вести учет личных финансов

Установка
---------

Создайте виртуальное окружение и активируйте его. Потом в нем выполните:

.. code-block:: text

    pip install -r requirements.txt


Вас также потребуется postgreSQL server.

Настройка
---------

Создайте файл settings.py и добавьте туда следующие настройки:

.. code-block:: python

    DB_USER = "user для postgreSQL"
    DB_PASSWORD = "password postgreSQL"
    DB_HOST = "postgreSQL server"
    DB_PORT = "port"
    DB_DATABASE = "database name"

Запуск
---------

Для создания базы данных запустите

.. code-block:: text

    python db_creator.py
