from aiogram.fsm.state import State, StatesGroup


class ManageService(StatesGroup):
    choosing_action = State()
    choosing_service = State()


class AddService(StatesGroup):
    waiting_for_title = State()
    waiting_for_desc = State()
    waiting_for_media = State()


class EditService(StatesGroup):
    waiting_for_choice = State()
    editing_desc = State()
    choosing_media_action = State()
    deleting_media = State()
    adding_media = State()


class DeleteService(StatesGroup):
    waiting_for_selection = State()
