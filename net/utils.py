from . import QAbstractSocket, QNetworkInterface, QHostAddress

def first_or_none(iterable: list):
    return (iterable or [None])[0]

def get_interfaces_that_are_up():
    localhost = QHostAddress(QHostAddress.LocalHost)
    return [first_or_none([entry.ip().toString()
                      for entry in interface.addressEntries() 
                          if entry.ip().protocol() == QAbstractSocket.IPv4Protocol and entry.ip() != localhost])
                      for interface in QNetworkInterface.allInterfaces()
                          if interface.flags() & QNetworkInterface.IsUp and not interface.flags() & QNetworkInterface.IsLoopBack]
               