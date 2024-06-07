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
    from flask import Flask, render_template, abort, make_response, request, redirect, jsonify, send_from_directory
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class WazaMessage() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    waza_token = os.environ.get('WAZA_BEARER_TOKEN','None')
    api_key = os.environ.get('API_KEY_MONITORING','None')
    phone_id = os.environ.get('PHONE_ID','None')

    database = 'gral-purpose'
    environment = None
    bearer_token = 'Bearer ' + str(waza_token)
    headers = None

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
            self.headers = {'Content-Type': 'application/json', 'Authorization': str(self.bearer_token) }
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def __del__(self):
        if self.db != None:
            self.db.close()

    def connect( self ) :
        try:
            if self.db == None :
                self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def isConnect(self) :
        return self.db != None

    def saveMsgs( self, msg_rx, msg_tx, user, mobile ) :
        try :
            if self.db != None :
                now = datetime.now()
                cursor = self.db.cursor()
                sql = """INSERT INTO whatsapp_messages (msg_rx, msg_tx, users, mobiles, create_at, update_at) VALUES(%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (str(msg_rx), str(msg_tx), str(user), str(mobile), now.strftime("%Y/%m/%d %H:%M:%S"), now.strftime("%Y/%m/%d %H:%M:%S") ))
                self.db.commit()
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()

    def sendWazaMessage(self, name, system, to = '56992116678' ) :

        #data_json = {
        #    'messaging_product' : 'whatsapp',
        #    'recipient_type'    : 'individual',
        #    'to'                : str(to),
        #    'type'              : 'text',
        #    'text'              : { 'preview_url': False, 'body': str(msgTx), }
        #}

        data_json = {
            'messaging_product' : 'whatsapp',
            'recipient_type'    : 'individual',
            'to'                : str(to),
            'type'              : 'template',
            'template': {
                'name': "alerta_sistema",
                'language': {
                    'code': 'es_ES',
                    'policy': 'deterministic'
                }, 
                'components': [
                        {
                        'type': 'HEADER',
                        'parameters': [
                            {
                            'type': 'text',
                            'text': str(name)
                            }
                        ]
                        },
                        {
                        'type': 'BODY',
                        'parameters': [
                            {
                            'type': 'text',
                            'text': str(system)
                            }
                        ]
                        },
                ]
            }
        }

        url = 'https://graph.facebook.com/v18.0/' + str(self.phone_id) + '/messages'
        # logging.info("Request To : " + url )
        try :
            response = requests.post(url, data = json.dumps(data_json), headers = self.headers, timeout = 40)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info("Response : " + str( data_response ) )
            else :
                logging.error("ERROR Response : " + str( data_response ) )
        except Exception as e:
            print("ERROR POST:", e)

        return 'ok', 200


    def requestProcess(self, request ) :
            
            if request.headers['x-api-key'] == self.api_key :
                pass
            else :
                abort(401)

            logging.info('########################## ' + str(request.method) + ' ###################################')
            logging.info("Reciv Header : " + str(request.headers) )
            logging.info("Reciv Data: " + str(request.data) )
            # valores por defecto
            data_response = jsonify({'statusCode': 200, 'statusDescription': 'Servicio exitoso' })
            errorCode = 200
            request_data = request.get_json()
            try :
                m1 = time.monotonic()
                data_response, errorCode = self.sendWazaMessage( request_data['name'], request_data['system'], request_data['to'] )
                diff = time.monotonic() - m1;
                logging.info("Time Response in " + str(diff) + " sec." )
            except Exception as e:
                print("ERROR POST:", e)
            return data_response, errorCode
