from game.enums import Cards, Suits

class Card(object):

    def __init__(self, suit: Suits, value: Cards):
        self.suit = suit
        self.value = value

    def __hash__(self):
        return hash(self.value) + hash(self.suit)

    def __repr__(self):
        return f"{self.suit.name}_{self.value.name}"

    def __cmp__(self, obj: Card):
        return (0 if isinstance(obj, Card) and obj.suit is self.suit
                and self.value is obj.value else 1 if self < obj else -1)

    def __ne__(self,obj: Card):
        return (not isinstance(obj, Card) or obj.suit is not self.suit
                or self.value is not obj.value)

    def __eq__(self, obj: Card):
        return isinstance(obj, Card) and obj.suit is self.suit and self.value is obj.value

    def __gt__(self, obj: Card):
        return (isinstance(obj, Card) and obj.suit is self.suit
                and obj.value.value < self.value.value)

    def __lt__(self, obj: Card):
        return (isinstance(obj, Card) and obj.suit is self.suit
                and obj.value.value > self.value.value)

    def is_pair(self, obj: Card):
        return (self.suit is obj.suit and
                (self.value is Cards.KING and obj.value is Cards.QUEEN or
                 self.value is Cards.QUEEN and obj.value is Cards.KING))
