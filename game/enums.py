from . import Enum

class Suits(Enum):
    S = 40
    C = 60
    D = 80
    H = 100
    NO_SUIT = 0

class TrainingEnum(Enum):
    FULL_TRAINING = 0x0
    PRETRAINING_OWN_CARDS = 0x1
    PRETRAINING_VALID_CARDS = 0x2

class NetworkMode(Enum):
    CLUSTER = 0x02
    SINGLE = 0X01
    SINGLE_LARGE = 0x03

class RewardMapperMode(Enum):
    DISCOUNTED = 0x00
    DISCOUNTED_REVERSED = 0x01
    NOT_MODIFIED = 0x02

class Cards(Enum):
    NINE = 0
    TEN = 10
    JACK = 2
    QUEEN = 3
    KING = 4
    ACE = 11

    def order_bias(self):
        val = 0

        if self is Cards.ACE:
            val = 20
        elif self is Cards.TEN:
            val = 16
        elif self is Cards.KING:
            val = 12
        elif self is Cards.QUEEN:
            val = 8
        elif self is Cards.JACK:
            val = 4

        return val
        