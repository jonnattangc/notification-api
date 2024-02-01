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
    from WazaMessage import WazaMessage 

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
        data_status = { "Status": "Ok", "Message": "Servicios Operando Correctamente" }
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
                        if self.notifiedHashExist(hash) :
                            logging.info("No hay cambio de estado que notificar")
                            data_status = { "Status": "Ok", "Message": "No hay cambios de estados que notificar" }
                        else :
                            mail = EmailNotification() 
                            waza = WazaMessage()
                            data_status = { "Status": "Ok", "Message": "Se han notificado cambio de estados" }
                            if self.saveNotification(data_response, hash) :
                                slack = SlackNotification() 
                                if not slack.notifyToChannel( data_response ) :
                                    mail.sendMailMessage( 'jonnattan@gmail.com','[Monitor] Error Procesando Datos', 'Data de Slack:\n' + str(data_response))
                                    data_status = { "Status": "Ok", "Message": "No se pudo notificar en Slack cambio de estado" }
                                    waza.sendWazaMessage("Revisa tu correo, hay hay un error reportado" )
                                else:
                                    data_status = { "Status": "Ok", "Message": "Se notifico en Slack cambio de estado" }
                                    waza.sendWazaMessage("Revisa tu slack, hay un cambio de estado reportado !!!" )
                                del slack
                            else:
                                mail.sendMailMessage( 'jonnattan@gmail.com','[Monitor] Error Guardando en Base de Datos', 'No se pudo guardar en BD de Notificaciones')
                                data_status = { "Status": "NOk", "Message": "Error Guardando en Base de Datos" }
                                waza.sendWazaMessage("Revisa tu Monitor, hay un error de BD !!!" )
                            del mail
                            del waza
        except Exception as e:
            print("ERROR Status:", e)
        diff = time.monotonic() - m1
        logging.info("Procesado en " + str(diff) + " Seg")
        return data_status, code
    
    def notifiedHashExist(self, hash) :
        sql = "SELECT * FROM `notifications` WHERE `notification_hash` = %s and `notification_active` = %s"
        cursor = self.db.cursor()
        cursor.execute(sql, (hash, True))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def saveNotification(self, data, hash) :
        saved = False
        try :
            if self.db != None and self.desableAllNotification() :
                sql = """INSERT INTO notifications (destination_name, destination_type, destination_value, notification_type, notification_date, notification_hash, notification_active ) VALUES (%s, %s, %s, %s, %s, %s,%s)"""
                cursor = self.db.cursor()
                now = datetime.now()
                cursor.execute(sql, ('Canal JonnaChannel', 'Slack', str(data), 'Cambio Estado', now.strftime("%Y-%m-%d %H:%M:%S"), str(hash), True ))
                self.db.commit()
                cursor.close()
                saved = True
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
        return saved
    
    def desableAllNotification(self) :
        saved = False
        try :
            if self.db != None :
                sql = """UPDATE notifications SET notification_active = %s WHERE notification_date < %s"""
                cursor = self.db.cursor()
                now = datetime.now()
                cursor.execute(sql, (False, now.strftime("%Y-%m-%d %H:%M:%S") ))
                self.db.commit()
                cursor.close()
                saved = True
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
        return saved