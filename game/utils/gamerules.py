from . import Card, Suits, Cards, List


class GameRules(object):

    MAX_SCORE = 1000
    THE_BARREL = 900

    @classmethod
    def is_card_valid(cls, cards: List[Card], card: Card, opponent_card: Card, trump: Suits =Suits.NO_SUIT) -> bool:
        if opponent_card is None and card in cards: 
            return True
        if card.suit is not opponent_card.suit:
            if cls.is_suit_present(cards, opponent_card.suit):
                return False
            elif card.suit is not trump and cls.is_suit_present(cards, trump):
                return False
            else:
                return True
        else:
            return card > opponent_card or (card < opponent_card and not cls.is_greater_present(cards, card))

    @classmethod
    def has_pair(cls, cards: List[Card], card: Card) -> bool:
        return any([card.is_pair(c) for c in cards])

    @classmethod
    def does_card_beat_opponents_one(cls, card: Card, opponent_card: Card, trump: Suits):
        return card > opponent_card or card.suit is trump and not (card.suit is opponent_card.suit)

    @classmethod
    def is_suit_present(cls, cards: List[Card], suit: Suits) -> bool:
        return any([card.suit is suit for card in cards])

    @classmethod
    def is_greater_present(cls, cards: List[Card], card: Card) -> bool:
        return any([c > card for c in cards])

    @classmethod
    def compute_forbidden_value(cls, cards: List[Card]) -> int:
        return 130 + sum([suit.value if any([card.suit is suit and card.value is Cards.KING for card in cards])
                         and any([card.suit is suit and card.value is Cards.QUEEN for card in cards]) 
                         else 0 for suit in list(Suits)])
