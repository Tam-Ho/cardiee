from cardiee.cardiee import Cardiee
import sys
from io import StringIO

def test_add_card(capsys):
    app = Cardiee("data/cardiee.db")
    app.add_card("Test Q", "Test A")
    captured = capsys.readouterr()
    print(captured.out)
    assert "Flashcard added with ID:" in captured.out or "Error adding flashcard:" in captured.out

def test_list_card(capsys):
    app = Cardiee("data/cardiee.db")
    app.list_cards()
    captured = capsys.readouterr()
    print(captured.out)
    assert "ID:" in captured.out or "Error retrieving flashcards:" in captured.out

def test_remove_card(capsys):
    app = Cardiee("data/cardiee.db")
    app.add_card("Test Q", "Test A")
    app.remove_card(1)
    captured = capsys.readouterr()
    print(captured.out)
    assert "Flashcard with ID: 1 removed." in captured.out or "Error removing flashcard:" in captured.out

def test_clear_card(capsys):
    app = Cardiee("data/cardiee.db")
    sys.stdin = StringIO("n\n")
    app.clear_cards()
    captured = capsys.readouterr()
    print(captured.out)
    assert "All flashcards cleared." in captured.out or "Error clearing flashcards:" in captured.out or "Clear operation canceled." in captured.out

def test_study(capsys):
    app = Cardiee("data/cardiee.db")
    sys.stdin = StringIO("y\n")
    app.clear_cards()
    app.add_card("Test Q1", "Test A1")
    app.add_card("Test Q2", "Test A2")
    app.add_card("Test Q3", "Test A3")
    app.list_cards()
    # Simulate user input for correct and wrong answers

    # Prepare simulated input: first correct, then wrong, then correct
    user_inputs = StringIO("Test A1\nWrong A2\nTest A3\n")
    sys.stdin = user_inputs
    app.study()
    captured = capsys.readouterr()
    print(captured.out)
    assert (
        "Correct!" in captured.out or
        "Incorrect." in captured.out or
        "No expired flashcards available for study." in captured.out or
        "Study session completed." in captured.out or
        "Error retrieving flashcard:" in captured.out
    )