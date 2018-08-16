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
import ssl
import urllib3
urllib3.disable_warnings()

class SocketNotificationWindow(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        
        self.configure(pady=10, padx=20)
        
        self.wm_attributes("-topmost", True)
        self.wm_title("PyEveLiveDPS Awaiting Login")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        self.geometry("200x50")
        self.update_idletasks()
            
        tk.Label(self, text='Waiting for you to login...').grid(row=1, column=1)

class SocketManager(multiprocessing.Process):
    def __init__(self, server, characterName, loginArgs):
        multiprocessing.Process.__init__(self)
        self.server = "https://" + server
        self.characterName = characterName
        self.loginArgs = loginArgs
        self.loginArgs += "&character_name=" + self.characterName
        self.guid = str(uuid.uuid4())
        self.loginArgs += "&socket_guid=" + self.guid
        self.queue = multiprocessing.Queue()
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
                #_sockMgr.loginWindow.destroy()
                _sockMgr.registered = True

        try:
            #self.loginWindow = SocketNotificationWindow()
            webbrowser.open(self.server + self.loginArgs)
            while self.running:
                try:
                    self.socket = SocketIO(self.server, verify=False,
                                          cookies={'socket_guid': self.guid, 'name': self.characterName})
                    self.namespace = self.socket.define(Namespace, '/client')
                    while not self.registered:
                        try:
                            self.namespace.emit('register_client')
                            self.socket.wait(2)
                        except Exception as e:
                            logger.exception(e)
                    timeWaiting = 30.0
                    while self.running:
                        try:
                            while not self.queue.empty():
                                self.namespace.emit('peld_data', self.queue.get())
                            time.sleep(0.1)
                            timeWaiting += 0.1
                            if timeWaiting >= 30:
                                self.namespace.emit('peld_check')
                                timeWaiting = 0.0
                        except Exception as e:
                            logger.exception(e)
                except Exception as e:
                    logger.exception(e)
        except Exception as e:
            logger.exception(e)

def LoggerThread(q):
    while True:
        record = q.get()
        if record is None:
            break
        logger = logging.getLogger()
        logger.handle(record)