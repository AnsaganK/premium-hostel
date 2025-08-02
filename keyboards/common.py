from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TEMPLATE_OPTIONS = {
    "clean": "Чисто и уютно",
    "location": "Удобная локация",
    "staff": "Вежливый персонал",
    "food": "Вкусный завтрак",
    "quiet": "Тихо и спокойно",
    "view": "Красивый вид",
    "wifi": "Быстрый Wi-Fi",
    "service": "Отличный сервис",
    "price": "Хорошее соотношение цена/качество",
    "transport": "Удобное расположение",
    "bed": "Удобная кровать",
    "bathroom": "Чистая ванная комната",
    "parking": "Бесплатная парковка",
    "checkin": "Быстрая регистрация",
    "interior": "Современный интерьер",
    "security": "Чувствуется безопасность",
    "temperature": "Комфортная температура в номере",
    "noise": "Хорошая шумоизоляция",
    "tv": "Работающий телевизор",
    "furniture": "Удобная мебель"
}

TEMPLATE_KEYS = list(TEMPLATE_OPTIONS.keys())
TEMPLATES_PER_PAGE = 5


def rating_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{i} ⭐️", callback_data=f"rating:{i}")]
            for i in range(1, 6)
        ]
    )


def review_templates_keyboard(selected: list[str], page: int) -> InlineKeyboardMarkup:
    start = page * TEMPLATES_PER_PAGE
    end = start + TEMPLATES_PER_PAGE
    sliced_keys = TEMPLATE_KEYS[start:end]

    keyboard = []

    # 🔝 Пагинация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="template_page:prev"))
    if end < len(TEMPLATE_KEYS):
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data="template_page:next"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    # ✅ Шаблоны
    for key in sliced_keys:
        label = TEMPLATE_OPTIONS[key]
        prefix = "✅ " if key in selected else ""
        keyboard.append([
            InlineKeyboardButton(
                text=f"{prefix}{label}",
                callback_data=f"template_toggle:{key}"
            )
        ])

    # ⬇️ Кнопка "Готово" — всегда внизу
    keyboard.append([
        InlineKeyboardButton(text="✏️ Готово", callback_data="template_done")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)