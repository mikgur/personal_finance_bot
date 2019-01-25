import logging

from sqlalchemy.orm import sessionmaker

from .exceptions import WrongCategoryType
from .model import User, db


def is_existing_user(user_id):
    """Does this user exist in database?
    """
    logging.debug("is_existing_user")
    Session = sessionmaker(bind=db)
    session = Session()
    return bool(session.query(User).filter(User.user_id == user_id).all())


def get_category_type_by_alias(alias):
    """In database categories types are "expense" and "income". But telegram bot knows nothing about it and will try
    to send category types as expense/расходы or income/доходы due to different localizations
    """
    if alias.lower() in ["expense", "расходы"]:
        return "expense"
    elif alias.lower() in ["income", "доходы"]:
        return "income"
    else:
        raise WrongCategoryType(f"There is no such category class in database: {alias}")
