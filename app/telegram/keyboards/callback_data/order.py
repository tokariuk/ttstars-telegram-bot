from aiogram.filters.callback_data import CallbackData


class CDOrderCheckoutCancel(CallbackData, prefix="order_cancel"):
    order_id: int


class CDStarsSellInvoiceCancel(CallbackData, prefix="stars_sell_cancel"):
    order_id: int
