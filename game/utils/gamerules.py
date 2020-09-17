from . import Card, Suits, Cards, List

class GameRules(object):

    def __init__(self, cards: List[Card] = None):
        self.cards = cards

    def set_card_collection(self, cards: List[Card]):
        self.cards = cards

    def is_card_valid(self, card: Card, opponent_card: Card, trump: Suits =Suits.NO_SUIT):
        return not((self.is_suit_present(opponent_card.suit) and
                    (card.suit is not opponent_card.suit or self.is_greater_present(card))) or
                   (self.is_suit_present(trump) and card.suit is not trump))

    def is_suit_present(self, suit: Suits):
        return any([card.suit is suit for card in self.cards])

    def is_greater_present(self, card: Card):
        return any([c > card for c in self.cards])

    def compute_forbidden_value(self):
        return 130 + sum([suit.value if any([card.suit is suit and card.value is Cards.KING for card in self.cards])
                         and any([card.suit is suit and card.value is Cards.QUEEN for card in self.cards]) 
                         else 0 for suit in list(Suits)])
