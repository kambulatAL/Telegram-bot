from loader import dp

from .admin_filter import ForAdmins

if __name__ == "filters":
    dp.filters_factory.bind(ForAdmins)
