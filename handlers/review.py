from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# from config import ADMIN_IDS
from keyboards.common import rating_keyboard, review_templates_keyboard, TEMPLATE_OPTIONS, TEMPLATE_KEYS, \
    TEMPLATES_PER_PAGE
from states.review import ReviewState
from storage.db import save_review, REVIEWS_STORAGE, load_reviews

router = Router()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Оставить отзыв")],
        [KeyboardButton(text="📋 Выбрать шаблон")],
        [KeyboardButton(text="📝 Мои отзывы")],
    ],
    resize_keyboard=True
)


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать! \nВы можете оставить отзыв или выбрать шаблон.", reply_markup=main_menu)


@router.message(ReviewState.waiting_for_text)
async def get_review_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Спасибо! Теперь, пожалуйста, поставьте оценку от 1 до 5.", reply_markup=rating_keyboard())
    await state.set_state(ReviewState.waiting_for_rating)


@router.callback_query(F.data.startswith("rating:"), ReviewState.waiting_for_rating)
async def get_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split(":")[1])
    data = await state.get_data()
    text = data.get("text")
    selected_templates = data.get("selected_templates")
    user = callback.from_user

    save_review(
        user_id=user.id,
        text=text if not selected_templates else None,
        rating=rating,
        templates=selected_templates
    )

    # Уведомление админам
    # for admin_id in ADMIN_IDS:
    #     await callback.bot.send_message(
    #         admin_id,
    #         f"📩 Новый отзыв!\n"
    #         f"От: @{user.username or user.full_name} (ID: {user.id})\n"
    #         f"Оценка: {rating}⭐\n"
    #         f"Сообщение: {text}"
    #     )

    await callback.message.answer("Отзыв сохранен\nБлагодарим за уделенное время!")
    await state.clear()
    await callback.answer()


@router.message(F.text.lower() == "📋 выбрать шаблон")
async def choose_template(message: Message, state: FSMContext):
    await state.update_data(selected_templates=[], template_page=0)
    await message.answer(
        "Выберите шаблоны отзыва:",
        reply_markup=review_templates_keyboard([], 0)
    )
    await state.set_state(ReviewState.waiting_for_text)


@router.message(F.text.lower() == "📄 оставить отзыв")
async def start_review(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, напишите ваш отзыв.")
    await state.set_state(ReviewState.waiting_for_text)


@router.callback_query(F.data.startswith("template_toggle:"), ReviewState.waiting_for_text)
async def toggle_template(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get("selected_templates", [])
    page = data.get("template_page", 0)

    if key in selected:
        selected.remove(key)
    else:
        selected.append(key)

    await state.update_data(selected_templates=selected)
    text = "📝 Вы выбрали:\n" + "\n".join(
        [f"• {TEMPLATE_OPTIONS[k]}" for k in selected]) if selected else "Ничего не выбрано"
    await callback.message.edit_text(
        text,
        reply_markup=review_templates_keyboard(selected, page)
    )
    await callback.answer()


@router.callback_query(F.data == "template_done", ReviewState.waiting_for_text)
async def done_template_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_templates", [])
    if not selected:
        await callback.answer("Выберите хотя бы один пункт.", show_alert=True)
        return

    # Генерируем текст отзыва
    review_text = "\n".join([TEMPLATE_OPTIONS[k] for k in selected])
    await state.update_data(text=review_text)
    await state.set_state(ReviewState.waiting_for_rating)

    await callback.message.edit_text("Спасибо! Теперь поставьте оценку:", reply_markup=rating_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("template_page:"), ReviewState.waiting_for_text)
async def change_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get("template_page", 0)
    selected = data.get("selected_templates", [])

    direction = callback.data.split(":")[1]
    if direction == "next":
        page += 1
    elif direction == "prev":
        page -= 1

    page = max(0, min(page, (len(TEMPLATE_KEYS) - 1) // TEMPLATES_PER_PAGE))

    await state.update_data(template_page=page)
    text = "📝 Вы выбрали:\n" + "\n".join(
        [f"• {TEMPLATE_OPTIONS[k]}" for k in selected]) if selected else "Ничего не выбрано"
    await callback.message.edit_text(
        text,
        reply_markup=review_templates_keyboard(selected, page)
    )
    await callback.answer()


# @router.message(F.text == "/myreviews")
@router.message(F.text.lower() == "📝 мои отзывы")
async def handle_my_reviews(message: Message):
    user_id = str(message.from_user.id)
    data = load_reviews()

    reviews = data.get(user_id)
    if not reviews:
        await message.answer("Вы пока не оставляли отзывов.")
        return

    text = "Ваши отзывы:\n\n"
    for idx, r in enumerate(reviews[-5:], 1):  # последние 5
        templates_text = ", ".join(TEMPLATE_OPTIONS.get(t, t) for t in r["templates"]) if r["templates"] else r['text']
        time_str = datetime.fromisoformat(r["timestamp"]).strftime('%d.%m.%Y %H:%M')
        text += f"{idx}. ⭐ {r['rating']}/5\n{templates_text}\n🕓 {time_str}\n\n"

    await message.answer(text)
