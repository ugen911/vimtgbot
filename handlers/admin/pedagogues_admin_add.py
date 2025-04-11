from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import MEDIA_DIR
from handlers.admin.base_crud import save_media_file
from keyboards.main_menu import back_menu
from .pedagogues_admin_states import EditPedagogue

import os

router = Router()
MEDIA_PATH = os.path.join(MEDIA_DIR, "педагоги")


@router.message(EditPedagogue.waiting_for_name)
async def add_pedagogue_name(message: types.Message, state: FSMContext):
    if message.text.strip().lower() != "пропустить":
        await state.update_data(name=message.text.strip())
    else:
        await state.update_data(name="Без имени")
    await state.set_state(EditPedagogue.waiting_for_role)
    await message.answer(
        "Введите должность (роль) педагога или напишите 'Пропустить':",
        reply_markup=back_menu,
    )


@router.message(EditPedagogue.waiting_for_role)
async def add_pedagogue_role(message: types.Message, state: FSMContext):
    if (message.text or "").strip().lower() == "пропустить":
        await state.update_data(role_title=message.text.strip())
    else:
        await state.update_data(role_title="Педагог")
    await state.set_state(EditPedagogue.waiting_for_description)
    await message.answer(
        "Введите описание педагога или напишите 'Пропустить':", reply_markup=back_menu
    )


@router.message(EditPedagogue.waiting_for_description)
async def add_pedagogue_description(message: types.Message, state: FSMContext):
    if (message.text or "").strip().lower() == "пропустить":
        await state.update_data(description=message.text.strip())
    else:
        await state.update_data(description="")
    await state.update_data(media=[])
    await state.set_state(EditPedagogue.waiting_for_media)
    await message.answer(
        "Отправьте медиа (фото/видео), или напишите 'Готово'", reply_markup=back_menu
    )
