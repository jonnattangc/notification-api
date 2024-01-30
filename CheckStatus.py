#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import json
    import requests
    import pymysql.cursors
    import time
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

    database = 'security'

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
        logging.info("KEY " + str(self.api_key) )
        logging.info("Reciv " + str(request.method) )
        logging.info("Reciv Data: " + str(request.data) )
        logging.info("Reciv Header : " + str(request.headers) )
        m1 = time.monotonic()

        data_status = { "status":False }
        code = 402

        try :
            data_json = {
                'api_key' : str(self.api_key)
            }
            headers = {'Content-Type': 'application/json'}
            url = 'https://api.uptimerobot.com/v2/getMonitors'
            logging.info("URL : " + url )
            response = requests.post(url, data = json.dumps(data_json), headers = headers, timeout = 40)
            if response.status_code != None :
                code = response.status_code
                if response.status_code == 200 :
                    data_response = response.json()
                    slack = SlackNotification() 
                    slack.notifyToChannel( data_response )
                    del slack
                    data_status = { "status": True }
        except Exception as e:
            print("ERROR Status:", e)
        diff = time.monotonic() - m1
        logging.info("Procesado en " + str(diff) + " Seg")
        return data_status, code