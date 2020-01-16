# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:02:26 2020

@author: Kamil Chrustowski
"""
from concurrent.futures import *
from asyncio import *
from communicationhandler import CommunicationHandler
class Server():
    __server = None
    __ip = ""
    __port = 0
    __serverService = ThreadPoolExecutor(max_workers = 1)
    __clients = []
    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port
    def clientCallback(self, reader, writer):
        handler = CommunicationHandler(reader, writer)
        self.__clients.append(handler)
    def startListen(self):
        def __start():
            self.__server = await start_server(clientCallback, self.__ip, self.__port)
            self.__server.serve_forever()
        self.__serverService.submit(__start)