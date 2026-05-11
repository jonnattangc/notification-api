#!/usr/bin/python
try:
    import logging
    import sys
    import os
    import json
    import threading
    import psutil
    import gc

    from service.client_repository import ClientRepository
    from service.cipher import Cipher
    from service.anotification import ANotification
    from service.email_notification import EmailNotification
    from service.waza_message import WazaMessage
    from service.slack_notification import SlackNotification

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

def message_process(json_data, path: str, client):
    process = psutil.Process(threading.get_native_id())
    mem_info = process.memory_info()
    name_thread = '[' + threading.current_thread().name + '-' + str(threading.get_native_id()) + '] '
    logging.info(name_thread + "After start thread memory: " + str(mem_info.rss))
    success: bool = False
    try:
        notification : ANotification = None
        if path.find('mail') >= 0:
            notification = EmailNotification()  
        if path.find('waza') >= 0:
            notification = WazaMessage()
        if path.find('slack') >= 0 :
            notification = SlackNotification()     
        success = notification.send_message(json_data, client)
        del notification
    except Exception as e:
        logging.error(name_thread + 'Error: ' + str(e))
        success = False

    gc.collect()

    mem_info = process.memory_info()
    logging.info(name_thread + "Before stop thread memory: " + str(mem_info.rss))

    if success:
        logging.info(name_thread + 'ha terminado con exito...')
    else:
        logging.error(name_thread + 'ha terminado con falla...')

    return success

class NotificationService():
    th = None
    client_repository = None

    def __init__(self):
        self.client_repository = ClientRepository()

    def __del__(self):
        self.client_repository = None

    def process(self, request_data, subpath: str):
        data_response = {"message": "Servicio ejecutado exitosamente", "data": None}
        http_code = 200
        client = None

        # evalua api key inmediatamente
        rx_api_key: str = request_data.get('x_api_key')
        if rx_api_key is None:
            logging.error('x-api-key no found')
            data_response = {"message": "No autorizado", "data": None}
            http_code = 409
            return data_response, http_code
        else:
            logging.info(f'x-api-key found : {rx_api_key}')
            client = self.client_repository.get_client(rx_api_key)
            if client is None:
                data_response = {"message": "No autorizado", "data": None}
                http_code = 401
                logging.error('x-api-key is not valid')
                return data_response, http_code
            else:
                logging.info(f'Client found: {client}')

        path: str = None
        if subpath is not None:
            path = subpath.lower().strip()

        if request_data.get('method') == 'POST':
            json_data = None
            request_type = None
            data_rx = None
            try:
                request_type = request_data['type']
            except Exception as e:
                request_type = None
            try:
                data_rx = request_data['data']
            except Exception as e:
                data_rx = None
            if request_type is not None:
                # encrypted or inclear
                if data_rx is not None and str(request_type) == 'encrypted':
                    cipher = Cipher()
                    data_cipher = str(data_rx)
                    logging.info('Data Encrypt: ' + str(data_cipher))
                    data_clear = cipher.aes_decrypt(data_cipher)
                    logging.info('Data EnClaro: ' + str(data_clear))
                    json_data = json.dumps(data_clear)
                    del cipher
                else:
                    json_data = data_rx
            else:
                json_data = data_rx

            self.th = threading.Thread(target=message_process, args=(json_data, path, client), name='th')
            self.th.start()

        return data_response, http_code
