from typing import List, Optional, Tuple

from . import DB_PATH, ERRORS, SUCCESS
from .database import DatabaseHandler
from .models import Flashcard


class Cardiee:
    def __init__(self):
        self.db_handler = DatabaseHandler(DB_PATH)

    def add_card(self, question: str, answer: str) -> Tuple[Optional[Flashcard], int]:
        return self.db_handler.add_card(question, answer)

    def remove_card(self, card_id: int) -> int:
        return self.db_handler.remove_card(card_id)

    def list_cards(
        self, expired_only: bool = False
    ) -> Tuple[Optional[List[Flashcard]], int]:
        return self.db_handler.list_cards(expired_only)

    def clear_cards(self) -> int:
        return self.db_handler.clear_cards()

    def update_cards(self, card_id: int, reset: bool) -> int:
        return self.db_handler.update_card_deadline(card_id, reset)

    def study(self) -> None:
        cards, code = self.db_handler.list_cards(expired_only=True)
        if code != SUCCESS:
            print(f"Error retrieving flashcards: {ERRORS[code]}")
            return

        if not cards:
            print("No expired flashcards available for study.")
            return

        for card in cards:
            print(f"ID: {card.id}, Question: {card.question}")
            user_input = input("Enter your answer: ").strip().lower()
            correct_answer = card.answer.strip().lower()
            if user_input == correct_answer:
                print("Correct!")
                update_code = self.db_handler.update_card_deadline(card.id, reset=False)
                if update_code == SUCCESS:
                    print("Card deadline updated.")
                else:
                    print(f"Error updating card deadline: {ERRORS[update_code]}")
            else:
                print(f"Incorrect. The correct answer is: {card.answer}")
                reset_code = self.db_handler.update_card_deadline(card.id, reset=True)
                if reset_code == SUCCESS:
                    print("Card deadline reset.")
                else:
                    print(f"Error resetting card deadline: {ERRORS[reset_code]}")
        print("Study session completed.")
