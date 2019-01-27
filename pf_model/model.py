"""Contains description of datamodel for postgreSQL
     in terms of sqlalcheny.
     Can be used for:
     - creating database and scheme from scratch
     - accessing existing database
    """

from flask_login import UserMixin
from sqlalchemy import (
    Boolean, Column, Date, Float, ForeignKey, Integer, String, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

import settings

db_string = f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}\
@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"

db = create_engine(db_string)
base = declarative_base()


class AccountType(base):
    __tablename__ = 'account_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)

    accounts = relationship("Account", back_populates="type")

    def __repr__(self):
        return f"<AccountType(id='{self.id}', name='{self.name}')>"


class Currency(base):
    __tablename__ = 'currencies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    shortname = Column(String(60), nullable=False)

    accounts = relationship("Account", back_populates="currency")

    def __repr__(self):
        return f"<Currency(id='{self.id}', name='{self.name}', \
        shortname='{self.shortname}')>"


class User(base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String(60), nullable=False)
    telegram_id = Column(String(60), nullable=False)
    otc = Column(String(128))
    password = Column(String(128))

    accounts = relationship("Account", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    categories = relationship("Category", back_populates="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_otc(self, otc):
        self.otc = generate_password_hash(otc)

    def check_otc(self, otc):
        return check_password_hash(self.otc, otc)

    def __repr__(self):
        return f"<User(id='{self.id}', \
        user_id='{self.user_id}', \
        user_name='{self.user_name}')>"


class Account(base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("account_types.id"), nullable=False)

    user = relationship("User")
    currency = relationship("Currency")
    type = relationship("AccountType")
    transactions = relationship("Transaction", back_populates="account")

    def __repr__(self):
        return f"<Account(id='{self.id}', name='{self.name}', user='{self.user}',\
                    currency='{self.currency}', type='{self.type}')>"


class CategoryType(base):
    __tablename__ = 'category_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)

    categories = relationship("Category", back_populates="type")

    def __repr__(self):
        return f"<CategoryType(id='{self.id}', name='{self.name}')>"


class Category(base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    type_id = Column(Integer, ForeignKey("category_types.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, nullable=False)

    type = relationship("CategoryType")
    user = relationship("User")
    transactions = relationship("Transaction", back_populates="category")

    def __repr__(self):
        return f"<Category(id='{self.id}', \
        name='{self.name}', \
        user='{self.user}, \
        type='{self.type}')>"


class TransactionType(base):
    __tablename__ = 'transaction_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)

    transactions = relationship("Transaction", back_populates="type")

    def __repr__(self):
        return f"<TransactionType(id='{self.id}', name='{self.name}')>"


class Transaction(base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    amount = Column(Float, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    type_id = Column(
        Integer, ForeignKey("transaction_types.id"), nullable=False
    )

    user = relationship("User")
    category = relationship("Category")
    account = relationship("Account")
    type = relationship("TransactionType")

    def __repr__(self):
        return f"<Transaction(id='{self.id}', date='{self.date}', user='{self.user}',\
                    category='{self.category}', amount='{self.amount}'\
                    account='{self.account}', type='{self.type}')>"
