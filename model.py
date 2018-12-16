"""Contains description of datamodel for postgreSQL
     in terms of sqlalcheny.
     Can be used for:
     - creating database and scheme from scratch
     - accessing existing database
    """

from sqlalchemy import Column, String, Integer, ForeignKey, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
        return f"<Currency(id='{self.id}', name='{self.name}', shortname='{self.shortname}')>"


class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(60), nullable=False)
    user_name = Column(String(60), nullable=False)

    transactions = relationship("Transaction", back_populates="user")

    def __repr__(self):
        return f"<User(id='{self.id}', user_id='{self.user_id}', user_name='{self.user_name}')>"


class Account(base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    user = Column(Integer, ForeignKey("users.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("account_types.id"), nullable=False)

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

    type = relationship("CategoryType")
    transactions = relationship("Transaction", back_populates="category")

    def __repr__(self):
        return f"<Category(id='{self.id}', name='{self.name}', type='{self.type}')>"


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
    type_id = Column(Integer, ForeignKey("transaction_types.id"), nullable=False)

    user = relationship("User")
    category = relationship("Category")
    account = relationship("Account")
    type = relationship("TransactionType")

    def __repr__(self):
        return f"<Transaction(id='{self.id}', date='{self.date}', user='{self.user}',\
                    category='{self.category}', amount='{self.amount}'\
                    account='{self.account}', type='{self.type}')>"
