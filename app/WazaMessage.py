#!/usr/bin/python
try:
    import logging
    import sys
    import os
    import json
    import requests

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class WazaMessage() :

    waza_token = os.environ.get('WAZA_BEARER_TOKEN','None')
    phone_id = os.environ.get('PHONE_ID','None')
    ws_api_version = os.environ.get('WAZA_API_VERSION','None')
    bearer_token : str = 'Bearer ' + str(waza_token)
    headers = None

    def __init__(self) :
        try:
            self.headers = {'Content-Type': 'application/json', 'Authorization': str(self.bearer_token) }
        except Exception as e :
            print("ERROR BD:", e)


    def sendWazaMessage(self, name, system, to = '56992116678' ) :
        success : bool = False

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

        url = 'https://graph.facebook.com/' + str(self.ws_api_version) + '/' + str(self.phone_id) + '/messages'
        # logging.info("Request To : " + url )
        try :
            response = requests.post(url, data = json.dumps(data_json), headers = self.headers, timeout = 40)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info("Response : " + str( data_response ) )
                success = True
            else :
                logging.error("ERROR Response : " + str( data_response ) )
                success = False
        except Exception as e:
            print("ERROR POST:", e)
            success = False

        return success
