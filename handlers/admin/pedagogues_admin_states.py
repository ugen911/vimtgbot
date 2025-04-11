from aiogram.fsm.state import State, StatesGroup


class EditPedagogue(StatesGroup):
    waiting_for_role = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_media = State()
    waiting_for_new_name = State()
    waiting_for_new_role = State()


class ManagePedagogue(StatesGroup):
    choosing_role = State()
    choosing_action = State()
    choosing_name = State()
    editing_name = State()
    editing_role = State()
    editing_description = State()
    editing_media = State()
    deleting_media = State()
