from aiogram.fsm.state import State, StatesGroup

class PartnershipStates(StatesGroup):
    name = State()
    phone = State()
    company = State()
    address_text = State()
    wait_geo = State()
    services = State()
    working_days = State()
    working_hours = State()
    confirm = State()