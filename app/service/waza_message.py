#!/usr/bin/python
try:
    import logging
    import sys
    import os
    import json
    import requests
    import threading
    from service.anotification import ANotification

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class WazaMessage(ANotification):
    ws_api_version: str = None

    def __init__(self):
        try:
            self.api_version = str(os.environ.get('WAZA_API_VERSION', 'None'))
        except Exception as e:
            print("Error: __INIT__:", e)

    def send_message(self, json_data: dict, client : dict) -> bool:

        name_thread = '[' + threading.current_thread().name + '-' + str(threading.get_native_id()) + '] '

        ws_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(client['bearer_token'])
        }

        from_str : str = ''
        meta_info : dict = {}
        body : str = ''
        name : str = ''

        if 'title_from' in json_data :
            from_str = str(json_data['title_from'])
        if 'meta_filter' in client :
            meta_info : dict = json.loads(client['meta_filter'])
        if 'body' in json_data :
            body = str(json_data['body'])
        if 'name' in json_data :
            name = str(json_data['name'])
        if 'phone' in json_data :
            if json_data['phone'] != None and json_data['phone'] != '' :
                phone : str = str(json_data['phone'])
                meta_info['to'].append(str(phone))

        success : bool = False
        data_tx = self.buildJsonMessage(str(meta_info['path']), from_str, body, name)

        if data_tx == None :
            logging.error(name_thread + "ERROR Response : " + str( data_response ) )
            success = False
        
        url = 'https://graph.facebook.com/' + str(self.api_version) + '/' + str(client['phone_origin']) + '/messages'
        for to in meta_info['to'] :
            data_tx['to'] = to
            logging.info(f"{name_thread} Sending to {to} data: {data_tx}")
            try :
                response = requests.post(url, data = json.dumps(data_tx), headers = ws_headers, timeout = 30 )
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

    def buildJsonMessage(self, path : str, fromm: str, body : str, name : str) -> dict :
        data_json = None
        if path != None and fromm != None and body != None and name != None :
            data_json = {
                'messaging_product' : 'whatsapp',
                'recipient_type'    : 'individual',
                'to'                : '-por-llenar-',
                'type'              : 'template',
                'template': {
                    'name': "aviso_curso",
                    'language': {
                        'code': 'es_CL',
                        'policy': 'deterministic'
                    }, 
                    'components': [
                            {
                            'type': 'HEADER',
                            'parameters': [
                                {
                                'type': 'text',
                                'text': fromm
                                }
                            ]
                            },
                            {
                            'type': 'BODY',
                            'parameters': [
                                {
                                'type': 'text',
                                'text': name
                                },
                                {
                                'type': 'text',
                                'text': body
                                }
                            ]
                            },
                            {
                            'type': 'button',
                            'sub_type': 'url',
                            'index': 0,
                            'parameters': [
                                {
                                'type': 'text',
                                'text': path
                                }
                            ]
                            },
                    ]
                }
            }
        return data_json