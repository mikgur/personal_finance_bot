class AccountNotFoundOrMultipleAccounts(Exception):
    pass


class CategoryNotFoundOrMultipleCategories(Exception):
    pass


class CategoryTypeNotInUserData(Exception):
    pass


class NoCurrencies(Exception):
    pass


class ObjectAlreadyExist(Exception):
    pass


class TransactionTypeNotFoundOrMultipleTransactionTypes(Exception):
    pass


class UserNotFoundOrMultipleUsers(Exception):
    pass


class WrongCategory(Exception):
    pass


class WrongCategoryType(Exception):
    pass
