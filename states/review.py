from aiogram.fsm.state import StatesGroup, State

class ReviewState(StatesGroup):
    waiting_for_text = State()
    waiting_for_rating = State()