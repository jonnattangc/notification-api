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
    from flask import send_from_directory, render_template
    from EmailNotification import EmailNotification
    from WazaMessage import WazaMessage 
    from Cipher import Cipher

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


def message_process( json_data, path : str, client ) :
        process = psutil.Process(threading.get_native_id())
        mem_info = process.memory_info() 
        name_thread = '[' + threading.current_thread().name + '-' + str(threading.get_native_id()) + '] '
        logging.info(name_thread + "After start thread memory: " + str(mem_info.rss))
        success: bool = False
        try :
            if path.find('mail') >= 0 :    
                mail = EmailNotification()
                success = mail.sendMailMessage(json_data['to'], json_data['subject'], json_data['body'], client)
                del mail
            elif path.find('waza') >= 0 :
                waza = WazaMessage()     
                success = waza.sendWazaMessage(str(json_data['to']), str(json_data['subject']), str(json_data['body']), client)
                del waza
            else :
                success = False
        except Exception as e :
            logging.error(name_thread + 'Error: ' + str(e))
            success = False
        
        gc.collect()

        mem_info = process.memory_info() 
        logging.info(name_thread + "Before stop thread memory: " + str(mem_info.rss))

        if success :
            logging.info(name_thread + 'ha terminado con exito...')
        else :
            logging.error(name_thread + 'ha terminado con falla...')

        return success

class Notification():
    th = None
    db = None
    def __init__(self) :
        try:
            host = os.environ.get('HOST_BD','None')
            user = os.environ.get('USER_BD','None')
            password = os.environ.get('PASS_BD','None')
            port = int(os.environ.get('PORT_BD', 3306))
            eschema = str(os.environ.get('SCHEMA_BD','gral-purpose'))
            self.db = pymysql.connect(host=host, port=port, user=user, password=password, database=eschema, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD __init__() :", e)
            self.db = None

    def __del__(self) :
        if self.db != None :
            self.db.close()
    
    def get_client(self, apikey: str) :
        client = None
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from clients where apikey = %s"""
                cursor.execute(sql, (apikey))
                results = cursor.fetchall()
                for row in results:
                    client = {
                        'phone_origin' : str(row['ws_phone_id']),
                        'bearer_token' : str(row['ws_bearer_token']),
                        'company_name' : str(row['company']),
                        'mail_user' : str(row['mail_user']),
                        'password' : str(row['mail_pass']),
                    }
                    logging.info("Client found: " + str(client['company_name']) )   
        except Exception as e:
            print("ERROR BD get_client():", e)
        return client

    def process(self, request, subpath: str ) :
        data_response = {"message" : "Servicio ejecutado exitosamente", "data": None}
        http_code  = 200
        client = None

        logging.info("Reciv " + str(request.method) + " Contex: /notification/" + str(subpath) )
        logging.info("Reciv Data: " + str(request.data) )
        logging.info("Reciv Header :\n" + str(request.headers) )

        # evalua pai key inmediatamente
        rx_api_key: str = request.headers.get('x-api-key')
        if rx_api_key == None :
            logging.error('x-api-key no found')
            data_response = {"message" : "No autorizado", "data": None}
            http_code  = 409
            return  data_response, http_code
        else :
            logging.info('x-api-key found')
            client = self.get_client(rx_api_key)
            if client == None :
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
            
            self.th = threading.Thread(target=message_process, args=( json_data, path, client ), name='th')
            self.th.start()
        elif request.method == 'GET' :
            #===============================================================================
            # Cualquier pagina que ocupe JS desde este servidor para por ac'a
            #===============================================================================
            if path.find('js') >= 0 :
                file_path = os.path.join(ROOT_DIR, 'static')
                file_path = os.path.join(file_path, 'js')
                return send_from_directory(file_path, str(namejs) ), http_code
            elif path.find('web') >= 0 :
                return render_template( 'page.html' ), http_code
            else :
                data_response, 404
        else :
            data_response, 404

        return  data_response, http_code