# online_tour_admin_states.py
from aiogram.fsm.state import State, StatesGroup


class ManageTour(StatesGroup):
    choosing_action = State()


class AddTour(StatesGroup):
    waiting_for_desc = State()
    waiting_for_media = State()


class EditTour(StatesGroup):
    waiting_for_selection = State()
    waiting_for_desc = State()
    deleting_media = State()
    waiting_for_media = State()


class DeleteTour(StatesGroup):
    waiting_for_selection = State()
