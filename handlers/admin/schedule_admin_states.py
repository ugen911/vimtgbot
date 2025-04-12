from aiogram.fsm.state import State, StatesGroup


class ManageSchedule(StatesGroup):
    choosing_group = State()
    choosing_action = State()

    # Редактирование
    choosing_block_to_edit = State()
    editing_desc = State()
    deleting_media = State()
    editing_media = State()

    # Удаление
    choosing_block_to_delete = State()


class EditSchedule(StatesGroup):
    entering_desc = State()
    entering_media = State()
