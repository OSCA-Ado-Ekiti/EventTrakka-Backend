# class EventSource(str, Enum):
#     EVENTTRAKKA = "EVENTTRAKKA"
#     EXTERNAL = "EXTERNAL"
#
#
# class EventMode(str, Enum):
#     VIRTUAL = "VIRTUAL"
#     PHYSICAL = "PHYSICAL"
#
#
# class EventFeeMode(str, Enum):
#     FREE = "FREE"
#     PAID = "PAID"
#
#
# class Currency(str, Enum):
#     USD = "USD"
#     NGN = "NGN"
#
#
# class EventFee(SQLModel):
#     mode: EventFeeMode
#     amount: Decimal | None
#     currency: Currency | None
#
#
# class Event(BaseDBModel):
#     __tablename__ = "events"
#
#     source: EventSource
#     mode_of_attending: EventMode
#     title: str
#     fee: EventFee
#     date: datetime
#     location: str | None
#     link: str | None
