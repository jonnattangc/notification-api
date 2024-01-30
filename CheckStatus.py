#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import json
    import requests
    import pymysql.cursors
    import time
    import hashlib
    from datetime import datetime
    from SlackNotification import SlackNotification
    from EmailNotification import EmailNotification

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class CheckStatus() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    api_key = os.environ.get('API_KEY_ROBOT_UPTIME','None')
    database = 'gral-purpose'

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def __del__(self):
        if self.db != None:
            self.db.close()

    def isConnect(self) :
        return self.db != None
    
    def getStatusPages(self, request ) : 
        m1 = time.monotonic()
        data_status = { "status":False }
        code = 402

        try :
            if self.api_key != 'None' :
                data_json = {'api_key' : str(self.api_key)}
                headers = {'Content-Type': 'application/json'}
                url = 'https://api.uptimerobot.com/v2/getMonitors'
                logging.info("URL : " + url )
                response = requests.post(url, data = json.dumps(data_json), headers = headers, timeout = 40)
                if response.status_code != None :
                    code = response.status_code
                    if response.status_code == 200 :
                        data_response = response.json()
                        hash = hashlib.sha512(bytes(json.dumps(data_response), 'utf-8')).hexdigest()
                        exists = self.notifiedHash(hash)
                        # logging.info("Hash : " + str(hash) + " - Exists : " + str(exists))
                        if exists == None :
                            if self.saveNotification(data_response, hash) :
                                slack = SlackNotification() 
                                if not slack.notifyToChannel( data_response ) :
                                    mail = EmailNotification() 
                                    mail.sendMailMessage( 'jonnattan@gmail.com','Error Procesando Datos', 'Data de Slack:\n' + str(data_response))
                                    del mail 
                                del slack
                            else:
                                mail = EmailNotification() 
                                mail.sendMailMessage( 'jonnattan@gmail.com','Error Guardando en Base de Datos', 'No se pudo guardar en BD de Notificaciones')
                                del mail
                        else :
                            logging.info("No hay cambio de estado que notificar")
                        data_status = { "status": True }
        except Exception as e:
            print("ERROR Status:", e)
        diff = time.monotonic() - m1
        logging.info("Procesado en " + str(diff) + " Seg")
        return data_status, code
    
    def notifiedHash(self, hash) :
        sql = "SELECT * FROM `notifications` WHERE `hash_notification` = %s"
        cursor = self.db.cursor()
        cursor.execute(sql, (hash))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def saveNotification(self, data, hash) :
        saved = True
        try :
            if self.db != None :
                sql = """INSERT INTO notifications (destination_name, destination_type, destination_value, notification_type, notification_date, hash_notification ) VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor = self.db.cursor()
                now = datetime.now()
                cursor.execute(sql, ('Canal JonnaChannel', 'Slack', str(data), 'Cambio Estado', now.strftime("%Y-%m-%d %H:%M:%S"), str(hash) ))
                self.db.commit()
                cursor.close()
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
            saved = False
        return saved