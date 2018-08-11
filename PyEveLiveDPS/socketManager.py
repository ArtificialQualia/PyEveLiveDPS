import tkinter as tk
from peld import logger
import threading
import uuid
import webbrowser
import queue
import time
from socketIO_client import SocketIO, BaseNamespace

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

class SocketManager(threading.Thread):
    def __init__(self, server, characterName, loginArgs):
        threading.Thread.__init__(self, name="socket_manager")
        self.server = "http://" + server
        self.characterName = characterName
        self.loginArgs = loginArgs
        self.loginArgs += "&character_name=" + self.characterName
        self.guid = str(uuid.uuid4())
        self.loginArgs += "&socket_guid=" + self.guid
        self.queue = queue.Queue()
        self.daemon = True
        self.running = True
        self.registered = False
        global _sockMgr
        _sockMgr = self

    def run(self):
        self.loginWindow = SocketNotificationWindow()
        webbrowser.open(self.server + self.loginArgs)
        self.socket = SocketIO(self.server, verify=False, 
                               cookies={'socket_guid': self.guid, 'name': self.characterName})
        self.namespace = self.socket.define(Namespace, '/client')
        while not self.registered:
            self.namespace.emit('register_client')
            self.socket.wait(2)
        timeWaiting = 30.0
        while self.running:
            while not self.queue.empty():
                self.namespace.emit('peld_data', self.queue.get())
            time.sleep(0.1)
            timeWaiting += 0.1
            if timeWaiting >= 30:
                self.namespace.emit('peld_check')
                timeWaiting = 0.0
            
        
    def stop(self):
        self.running = False
        self.registered = True
        try:
            self.namespace.disconnect()
            self.socket.disconnect()
        except AttributeError:
            logger.error('Socket manager missing attributes, web page probably never loaded for ' + self.server)

class Namespace(BaseNamespace):
    def on_connect(self):
        logger.info('Connected websocket to ' + _sockMgr.server)

    def on_disconnect(self):
        logger.info('Websocket disconnected from ' + _sockMgr.server)

    def on_reconnect(self):
        logger.info('Websocket reconnected to ' + _sockMgr.server)
        _sockMgr.registered = False
        while not _sockMgr.registered:
            self.emit('register_client')
            _sockMgr.socket.wait(2)

    def on_client_registered(self, *args):
        logger.info('Websocket client registered with server')
        _sockMgr.loginWindow.destroy()
        _sockMgr.registered = True
