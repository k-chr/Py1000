from PyQt5.QtCore import QObject, pyqtSignal

STATUS_GAME = { "VALUE_DECLARATION": "Choose value to declare. ",
                "STACK_CHOOSING": "Choose number of card stack. ",
                "CARDS_HANDIN":"Wait until server gives you cards to play.",
                "WAITING_FOR_OPPONENT" : "Waiting for opponent to connect...",
                "TYPE_IP": "Provide your IP address into text fields and press START button",
                "STACK_CARD_TAKING": "Take cards from stack by choosing unwanted hand's card.",
                "GAME": "Game time!",
                "SCORING": "Scoring time!",
                "APP_START":"Choose game mode or adjust settings or get some help with game rules",
                "OPPONENT_MOVE":"Waiting for opponent move...",
                "YOUR_MOVE":"It\'s your turn...",
                "TRUMP_CHANGE":"Trump suit changed!",
                "CONNECTION_FAILED":"Failed to connect, check if you have connection to LAN"}
class Signals(QObject):
    statusChanged = pyqtSignal()

class StatusGame(QObject):
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if StatusGame.__instance == None:
            StatusGame()
        return StatusGame.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if StatusGame.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.__status_name = "APP_START"
            self.signals = Signals()
            StatusGame.__instance = self

    def get_status_name(self):
        return self.__status_name

    def set_status_name(self, name):
        self.__status_name = str(name)
        self.signals.statusChanged.emit()