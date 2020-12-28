from . import Card, Suits, Cards, List


class GameRules(object):

    MAX_SCORE = 1000
    THE_BARREL = 900


    def __init__(self, cards: List[Card] = None):
        self.cards = cards

    def set_card_collection(self, cards: List[Card]) -> None:
        self.cards = cards

    def is_card_valid(self, card: Card, opponent_card: Card, trump: Suits =Suits.NO_SUIT) -> bool:
        if card.suit is not opponent_card.suit:
            if self.is_suit_present(opponent_card.suit):
                return False
            elif card.suit is not trump and self.is_suit_present(trump):
                return False
            else:
                return True
        else:
            return card > opponent_card or (card < opponent_card and not self.is_greater_present(card))


    def has_pair(self, card: Card) -> bool:
        
        return any([card.is_pair(c) for c in self.cards])

    def is_suit_present(self, suit: Suits) -> bool:
        return any([card.suit is suit for card in self.cards])

    def is_greater_present(self, card: Card) -> bool:
        return any([c > card for c in self.cards])

    def compute_forbidden_value(self) -> int:
        return 130 + sum([suit.value if any([card.suit is suit and card.value is Cards.KING for card in self.cards])
                         and any([card.suit is suit and card.value is Cards.QUEEN for card in self.cards]) 
                         else 0 for suit in list(Suits)])
