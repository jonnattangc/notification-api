#!/usr/bin/python
try:
    import logging
    import sys
    import os
    import time
    import json
    import requests
    import pymysql.cursors
    from datetime import datetime
    import threading
    import psutil
    import gc

    from EmailNotification import EmailNotification
    from WazaMessage import WazaMessage 
    from Cipher import Cipher

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


def message_process( json_data, path : str ) :
        process = psutil.Process(threading.get_native_id())
        mem_info = process.memory_info() 
        logging.info("after start thread memory: " + str(mem_info.rss))

        name_thread = '[' + threading.current_thread().name + '-' + str(threading.get_native_id()) + '] '
        success: bool = False
        try :
            if path.find('mail') >= 0 :    
                mail = EmailNotification()
                success = mail.sendMailMessage(json_data['to'], json_data['subject'], json_data['body'])
                del mail
            elif path.find('waza') >= 0 :
                waza = WazaMessage()     
                success = waza.sendWazaMessage(json_data['name'], json_data['system'], json_data['to'])
                del waza
            else :
                success = False
        except Exception as e :
            logging.error(name_thread + 'Error: ' + str(e))
            success = False
        
        gc.collect()

        mem_info = process.memory_info() 
        logging.info("before stop thread memory: " + str(mem_info.rss))

        if success :
            logging.info(name_thread + 'ha terminado con exito...')
        else :
            logging.error(name_thread + 'ha terminado con falla...')

        return success

class Notification():
    api_key : str = None
    th = None

    def __init__(self):
        self.api_key = str(os.environ.get('API_KEY_MONITORING','None'))

    #def __del__(self):
        #try :
            # if self.th != None and self.th.is_alive() :
                # self.th.join()
        #except Exception as e :
        #    logging.error( e )
        #del self.th


    def process(self, request, subpath: str ) :
        data_response = {"message" : "Servicio ejecutado exitosamente", "data": None}
        http_code  = 200
        logging.info("Reciv " + str(request.method) + " Contex: /notification/" + str(subpath) )
        logging.info("Reciv Data: " + str(request.data) )
        logging.info("Reciv Header :\n" + str(request.headers) )
        # evlua pai key inmediatamente
        rx_api_key = request.headers.get('x-api-key')
        if rx_api_key == None :
            logging.error('x-api-key no found')
            data_response = {"message" : "No autorizado", "data": None}
            http_code  = 409
            return  data_response, http_code
        if str(rx_api_key) != str(self.api_key) :
            data_response = {"message" : "No autorizado", "data": None}
            http_code  = 401
            logging.error('x-api-key is not valid')
            return  data_response, http_code
        
        path : str = None 
        if subpath != None : 
            path = subpath.lower().strip()

        if request.method == 'POST' :
            request_data = request.get_json()
            json_data = None
            request_type = None
            data_rx = None
            try :
                request_type = request_data['type']
            except Exception as e :
                request_type = None
            try :
                data_rx = request_data['data']
            except Exception as e :
                data_rx = None
            if request_type != None :
                # encrypted or inclear
                if data_rx != None and str(request_type) == 'encrypted' :
                    cipher = Cipher()
                    data_cipher = str(data_rx)
                    logging.info('Data Encrypt: ' + str(data_cipher) )
                    data_clear = cipher.aes_decrypt(data_cipher)
                    logging.info('Data EnClaro: ' + str(data_clear) )
                    json_data = json.dumps(data_clear)
                    del cipher
                else: 
                    json_data = data_rx
            else: 
                    json_data = data_rx
            
            self.th = threading.Thread(target=message_process, args=( json_data, path ), name='th')
            self.th.start()
            
        else :
            data_response, http_code = None, 404
        return  data_response, http_code