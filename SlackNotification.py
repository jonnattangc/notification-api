#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import json
    import requests
    from datetime import datetime

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class SlackNotification() :
    url = os.environ.get('SLACK_NOTIFICATION','None')

    def notifyToChannel(self, data_notify ) : 
        m1 = datetime.now()
        response = None
        request_tx = {}
        errors = []
        count = str(data_notify['pagination']['total'])
        isOk = str(data_notify['stat'])

        if int(count) > 0 and isOk.find('ok') == 0 :
            for monitor in data_notify['monitors'] :
                if int(monitor['status']) != 2 :
                    errors.append(
                        {
                            'pretext'       : str(monitor['friendly_name']),
                            'text'          : 'URL: ' + str(monitor['url']),
                            'color'         : 'danger',
                            'fields'        : [
                                    {
                                        'title': 'Intervalo de consulta',
                                        'value': 'El monitor de consulta cada ' + str(monitor['interval']) + ' seg.',
                                        'short': False
                                    },
                                    {
                                        'title': 'Razón Caída',
                                        'value': str(monitor['reason']),
                                        'short': True
                                    }
                            ]
                        }
                    )

            if len(errors) > 0 :
                request_tx = {
                    'username': 'ALERTA: Notificación de algo funcionando mal',
                    'text': 'Existen ' + str(len(errors)) + ' monitoreos automáticos que se deben analizar',
                    'attachments': errors
                }
                try :
                    logging.info("URL : " + self.url )
                    if self.url != 'None' :
                        headers = {'Content-Type': 'application/json'}
                        response = requests.post(self.url, data = json.dumps(request_tx), headers = headers, timeout = 40)
                        if( response != None and response.status_code == 200 ) :
                            logging.info('Response Slack' + str( response ) )
                        elif( response != None and response.status_code != 200 ) :
                            logging.info("Response NOK" + str( response ) )
                        else :
                            logging.info("No se notifica nada por Slak")
                        
                        diff = datetime.now() - m1
                        logging.info("Notificado en " + str(diff) + " MS")
                except Exception as e:
                    logging.info("Response JSON: " + str( data_notify ) )
                    print("ERROR POST:", e)
