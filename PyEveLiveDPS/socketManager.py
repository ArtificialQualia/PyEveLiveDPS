import logging
import tkinter as tk
import multiprocessing
import logging
import threading
import uuid
import webbrowser
import time
import sys
from socketIO_client import SocketIO, BaseNamespace
import socketIO_client.exceptions
import ssl
import urllib3
urllib3.disable_warnings()

class SocketManager(multiprocessing.Process):
    def __init__(self, server, characterName, loginArgs, loginNotificationQueue):
        multiprocessing.Process.__init__(self)
        if server.startswith("http://") or server.startswith("https://"):
            self.server = server
        else:
            self.server = "https://" + server
        self.characterName = characterName
        self.loginArgs = loginArgs
        self.loginArgs += "&character_name=" + self.characterName
        self.guid = str(uuid.uuid4())
        self.loginArgs += "&socket_guid=" + self.guid
        self.loginNotificationQueue = loginNotificationQueue
        self.dataQueue = multiprocessing.Queue()
        self.daemon = True
        self.running = True
        self.registered = False
        
        logger = logging.getLogger()
        self.loggerLevel = logger.getEffectiveLevel()
        self.logging_queue = multiprocessing.Queue()
        lt = threading.Thread(target=LoggerThread, args=(self.logging_queue,), daemon=True)
        lt.start()

    def run(self):
        qh = logging.handlers.QueueHandler(self.logging_queue)
        logger = logging.getLogger()
        logger.setLevel(self.loggerLevel)
        logger.addHandler(qh)
        global _sockMgr
        _sockMgr = self

        class Namespace(BaseNamespace):
            def on_connect(self):
                logger.info('Connected websocket to ' + _sockMgr.server)

            def on_disconnect(self):
                logger.info('Websocket disconnected from ' + _sockMgr.server)

            def on_reconnect(self):
                logger.info('Websocket reconnected to ' + _sockMgr.server)
                _sockMgr.registered = False
                try:
                    while not _sockMgr.registered:
                        self.emit('register_client')
                        _sockMgr.socket.wait(2)
                except Exception as e:
                    logger.exception(e)

            def on_client_registered(self, *args):
                logger.info('Websocket client registered with server')
                _sockMgr.loginNotificationQueue.put(True)
                _sockMgr.registered = True

        webbrowser.open(self.server + self.loginArgs)
        while self.running:
            try:
                self.socket = SocketIO(self.server, verify=False, wait_for_connection=False,
                                      cookies={'socket_guid': self.guid, 'name': self.characterName})
                self.socket.wait(1)
                self.namespace = self.socket.define(Namespace, '/client')
                while not self.registered:
                    self.namespace.emit('register_client')
                    self.socket.wait(1)
                timeWaiting = 30.0
                while self.running:
                    while not self.dataQueue.empty():
                        self.namespace.emit('peld_data', self.dataQueue.get())
                    time.sleep(0.1)
                    timeWaiting += 0.1
                    if timeWaiting >= 30:
                        self.namespace.emit('peld_check')
                        timeWaiting = 0.0
            except socketIO_client.exceptions.ConnectionError as e:
                logger.exception(e)
            except Exception as e:
                logger.exception(e)
            except:
                logger.critical('baseException')

def LoggerThread(q):
    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger()
        logger.handle(record)