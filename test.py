from game.card import Card
from game.enums import Cards, Suits
from game.utils.gamerules import GameRules

def test():
    rules = GameRules([Card(Suits.D, Cards.QUEEN), Card(Suits.D, Cards.KING), Card(Suits.D, Cards.JACK),  Card(Suits.H, Cards.JACK),
                     Card(Suits.C, Cards.JACK),  Card(Suits.S, Cards.JACK),  Card(Suits.D, Cards.NINE),  Card(Suits.H, Cards.NINE), 
                    Card(Suits.C, Cards.NINE),  Card(Suits.S, Cards.NINE)])

    assert rules.compute_forbidden_value() == 210


test()
