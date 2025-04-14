from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from handlers.admin.base_crud import load_json, save_json
from keyboards.main_menu import back_menu
from .services_admin_states import DeleteService, ManageService

router = Router()

SECTION_TITLE = "📚 Услуги"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageService.choosing_action, F.text == "🗑 Удалить услугу")
async def start_delete_service(message: types.Message, state: FSMContext):
    services = load_json(JSON_PATH)
    if not services:
        return await message.answer("Список услуг пуст.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in services]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(DeleteService.waiting_for_selection)
    await message.answer("Выберите услугу для удаления:", reply_markup=keyboard)


@router.message(DeleteService.waiting_for_selection)
async def delete_service_by_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    services = load_json(JSON_PATH)
    new_services = []
    found = False

    for svc in services:
        if svc["title"] == title:
            for file in svc.get("media", []):
                try:
                    os.remove(os.path.join(MEDIA_PATH, file))
                except FileNotFoundError:
                    pass
            found = True
        else:
            new_services.append(svc)

    if not found:
        return await message.answer("❌ Услуга не найдена")

    save_json(JSON_PATH, new_services)
    await message.answer("🗑 Услуга удалена")

    if not new_services:
        await state.set_state(ManageService.choosing_action)
        return await message.answer("Список услуг теперь пуст.", reply_markup=back_menu)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in new_services]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await message.answer("Хотите удалить ещё одну? Выберите:", reply_markup=keyboard)
