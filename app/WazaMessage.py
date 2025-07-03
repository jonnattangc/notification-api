#!/usr/bin/python
try:
    import logging
    import sys
    import os
    import json
    import requests
    import threading

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class WazaMessage() :
    ws_api_version : str = None

    def __init__(self) :
        try:
            self.api_version = str(os.environ.get('WAZA_API_VERSION','None'))
        except Exception as e :
            print("Error: __INIT__:", e)

    def sendWazaMessage(self, to: str, subject: str, body: str, client ) :
        name_thread = '[' + threading.current_thread().name + '-' + str(threading.get_native_id()) + '] '

        ws_headers = {
            'Content-Type': 'application/json', 
            'Authorization': 'Bearer ' + str(client['bearer_token']) 
        }

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
                            'text': str(subject)
                            }
                        ]
                        },
                        {
                        'type': 'BODY',
                        'parameters': [
                            {
                            'type': 'text',
                            'text': str(body)
                            }
                        ]
                        },
                ]
            }
        }
        url = 'https://graph.facebook.com/' + str(self.api_version) + '/' + str(client['phone_origin']) + '/messages'
        # logging.info("Request To : " + url )
        try :
            response = requests.post(url, data = json.dumps(data_json), headers = ws_headers, timeout = 10 )
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info(name_thread + "Response : " + str( data_response['messages'][0]['message_status'] ) )
                success = True
            else :
                logging.error(name_thread + "ERROR Response : " + str( data_response ) )
                success = False
        except Exception as e:
            print("ERROR POST:", e)
            success = False

        return success
