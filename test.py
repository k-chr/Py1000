from game.utils.randomcardgenerator import RandomCardGenerator
from game.card import Card
from game.enums import Cards, Suits
from game.utils.gamerules import GameRules
from net.utils import get_address_of_interfaces_that_are_up
def test():
    rules = GameRules([Card(Suits.D, Cards.QUEEN), Card(Suits.D, Cards.KING), Card(Suits.D, Cards.JACK),  Card(Suits.H, Cards.JACK),
                     Card(Suits.C, Cards.JACK),  Card(Suits.S, Cards.TEN),  Card(Suits.D, Cards.NINE),  Card(Suits.H, Cards.NINE), 
                    Card(Suits.C, Cards.NINE),  Card(Suits.S, Cards.ACE)])

    assert rules.compute_forbidden_value() == 210
    gen = RandomCardGenerator()
    print(get_address_of_interfaces_that_are_up())
    assert rules.is_card_valid(Card(Suits.S, Cards.TEN), Card(Suits.S, Cards.NINE) )
    assert not rules.is_card_valid(Card(Suits.D, Cards.NINE), Card(Suits.S, Cards.NINE) )
    assert rules.is_card_valid(Card(Suits.S, Cards.TEN), Card(Suits.S, Cards.NINE), Suits.H)
    #assert rules.is_card_valid(Card(Suits.S, Cards.TEN), Card(Suits.S, Cards.NINE) )
    #assert rules.is_card_valid(Card(Suits.S, Cards.TEN), Card(Suits.S, Cards.NINE) )
    #assert rules.is_card_valid(Card(Suits.S, Cards.TEN), Card(Suits.S, Cards.NINE) )
    #assert rules.is_card_valid(Card(Suits.S, Cards.TEN), Card(Suits.S, Cards.NINE) )
    #assert rules.is_card_valid(Card(Suits.S, Cards.TEN), Card(Suits.S, Cards.NINE) )
    cards = gen.get_cards()
    print(cards)
    print([card.id() for card in cards])
test()
