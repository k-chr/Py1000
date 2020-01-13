
STATUS_GAME = {"VALUE_DECLARATION": "Choose value to declare. ",
                "STACK_CHOOSING": "Choose number of card stack. ",
                "STACK_CARD_TAKING": "Take cards from stack by choosing unwanted hand's card.",
                "GAME": "Game time!",
                "SCORING": "Scoring time!"}

class StatusGame:
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
            self.__status_name = "GAME"
            StatusGame.__instance = self

    def get_status_name(self):
        return self.__status_name

    def set_status_name(self, name):
        self.__status_name = str(name)