from aiogram.fsm.state import State, StatesGroup


class ManageAnnouncements(StatesGroup):
    choosing_action = State()


class AddAnnouncement(StatesGroup):
    waiting_for_title = State()
    waiting_for_desc = State()
    waiting_for_media = State()


class DeleteAnnouncement(StatesGroup):
    waiting_for_selection = State()


class EditAnnouncement(StatesGroup):
    waiting_for_choice = State()
    editing_desc = State()
    deleting_media = State()
    adding_media = State()
