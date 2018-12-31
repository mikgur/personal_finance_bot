class PFBException(Exception):
    pass


class PFBNoCurrencies(PFBException):
    pass


class PFBWrongCategory(PFBException):
    pass


class PFBWrongCategoryType(PFBException):
    pass
