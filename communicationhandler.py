# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:27:21 2020

@author: Kamil Chrustowski
"""
from concurrent.futures import *
from asyncio import *
class CommunicationHandler():
    __reader = None
    __writer = None
    __should_exit = False
    __receiving_service = ThreadPoolExecutor(max_workers = 1)
    __sending_service = ThreadPoolExecutor(max_workers = 1)
    
    def __init__(self, reader, writer):
        self.__reader = reader
        self.__writer = writer
        self.__receive_service.submit(self.get_message)
    def get_message(self):
        while True:
            raw = await self.__reader.read(-1)
            if not raw:
                break;
            message = raw.decode()
            print(f'received: {message}')
    def send_message(self,message):
        async def send():
            await self.__writer.write(message)
        self.__sending_service.submit(send)
                