import logging
import multiprocessing
import logging
import threading
import json
import uuid
import webbrowser
import socketio
import urllib3

from version import version

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
        self.fleetMetadataQueue = multiprocessing.Queue()
        self.dataRecieveQueue = multiprocessing.Queue()
        self.errorQueue = multiprocessing.Queue()
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
        logging.getLogger("socketio.client").setLevel(30)
        logging.getLogger("engineio.client").setLevel(30)
        _sockMgr = self
        info = {'version': version.split('-')[0], 'socket_guid': self.guid, 'name': self.characterName}
        peld_check_data = {'socket_guid': self.guid, 'name': self.characterName}

        class Namespace(socketio.ClientNamespace):
            def on_connect(self):
                logger.info('Connected websocket to ' + _sockMgr.server)

            def on_disconnect(self):
                logger.info('Websocket disconnected from ' + _sockMgr.server)

            def on_client_registered(self, *args):
                logger.info('Websocket client registered with server')
                _sockMgr.loginNotificationQueue.put(True)
                _sockMgr.registered = True
            
            def on_peld_check(self, data):
                data = json.loads(data)
                _sockMgr.fleetMetadataQueue.put(data)
            
            def on_peld_data(self, data):
                data = json.loads(data)
                if data['category'] in ['dpsOut', 'dpsIn', 'logiOut']:
                    _sockMgr.dataRecieveQueue.put(data)
            
            def on_peld_error(self, data):
                _sockMgr.errorQueue.put(data)

        webbrowser.open(self.server + self.loginArgs)
        while self.running:
            try:
                self.socket = socketio.Client(ssl_verify=False)
                self.socket.register_namespace(Namespace('/client'))
                self.socket.connect(self.server, namespaces=['/client'])
                while not self.registered:
                    self.socket.emit('register_client', info, namespace='/client')
                    self.socket.sleep(1)
                timeWaiting = 30.0
                while self.running:
                    while not self.dataQueue.empty():
                        peld_data = self.dataQueue.get()
                        peld_data['entry']['owner'] = self.characterName
                        peld_data['socket_guid'] = self.guid
                        self.socket.emit('peld_data', peld_data, namespace='/client')
                    self.socket.sleep(0.1)
                    timeWaiting += 0.1
                    if timeWaiting >= 30:
                        self.socket.emit('peld_check', peld_check_data, namespace='/client')
                        timeWaiting = 1
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