# eat_admin_states.py
from aiogram.fsm.state import State, StatesGroup


class ManageMenu(StatesGroup):
    choosing_action = State()


class AddMenu(StatesGroup):
    waiting_for_desc = State()
    waiting_for_media = State()


class EditMenu(StatesGroup):
    waiting_for_choice = State()
    editing_desc = State()
    deleting_media = State()
    adding_media = State()


class DeleteMenu(StatesGroup):
    waiting_for_selection = State()
