from aiogram.fsm.state import State, StatesGroup


class EditSchedule(StatesGroup):
    entering_desc = State()
    entering_media = State()


class ManageSchedule(StatesGroup):
    choosing_group = State()
    choosing_action = State()
    choosing_block = State()
    editing_desc = State()
    editing_media = State()
