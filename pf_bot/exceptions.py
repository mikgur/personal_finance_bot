class NoCurrencies(Exception):
    pass


class WrongCategory(Exception):
    pass


class WrongCategoryType(Exception):
    pass


class PFBCategoryAlreadyExist(PFBException):
    pass


class PFBCategoryTypeNotInUserData(PFBException):
    pass
