#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import json
    import requests
    import time

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class SlackNotification() :
    url = os.environ.get('SLACK_NOTIFICATION','None')


    def getTypeMonitor(self, type) : 
        if str(type) == '1' :
            return 'HTTPS'
        elif str(type) == '2' :
            return 'KEYWORD'
        elif str(type) == '3' :
            return 'PING'
        elif str(type) == '4' :
            return 'PORT'
        elif str(type) == '5' :
            return 'HEARTBEAT'
        else :
            return 'DESCONOCIDO: ' + str(type)
        
    def getStateMonitor(self, state) : 
        if str(state) == '0' :
            return 'EN PAUSA'
        elif str(state) == '1' :
            return 'NO COMPROBADO'
        elif str(state) == '8' :
            return 'DEGRADADO'
        elif str(state) == '9' :
            return 'EN FALLA'
        elif str(state) == '2' :
            return 'FUNCIONANDO CORRECTAMENTE'
        else :
            return 'VALOR: ' + str(state)

    def getMonitorColor(self, state) : 
        if str(state) == '0' :
            return 'warning'
        elif str(state) == '1' :
            return 'warning'
        elif str(state) == '8' :
            return 'warning'
        elif str(state) == '9' :
            return 'danger'
        elif str(state) == '2' :
            return 'good'
        else :
            return 'warning'

    def notifyToChannel(self, data_notify ) : 
        ret = True
        m1 = time.monotonic()
        response = None
        request_tx = {}
        monitors = []
        count = str(data_notify['pagination']['total'])
        isOk = str(data_notify['stat'])
        count_errors = 0
        if int(count) > 0 and isOk.find('ok') == 0 :
            for monitor in data_notify['monitors'] :
                if int(monitor['status']) != 0 :
                    logging.info("MONITOR : " + str(monitor) )
                    if int(monitor['status']) != 2 :
                        count_errors = count_errors + 1
                    monitors.append(
                        {
                            'pretext'       : str(monitor['friendly_name']),
                            'text'          : 'URL: ' + str(monitor['url']),
                            'color'         : self.getMonitorColor(str(monitor['status'])),
                            'fields'        : [
                                    {
                                        'title': 'Tipo Monitor',
                                        'value': self.getTypeMonitor(str(monitor['type'])),
                                        'short': True
                                    },
                                    {
                                        'title': 'Estado de Monitor',
                                        'value': self.getStateMonitor(str(monitor['status'])),
                                        'short': True
                                    },
                                    {
                                        'title': 'Intervalo de consulta',
                                        'value': 'El monitor de consulta cada ' + str(monitor['interval']) + ' seg.',
                                        'short': False
                                    },
                            ]
                        }
                    )

            if len(monitors) > 0 :
                request_tx = {
                    'username': 'ALERTA: Cambio de Estado en monitores',
                    'text': 'Hay ' + str(count_errors) + ' monitores que se deben analizar',
                    'attachments': monitors
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
                        
                        diff = time.monotonic() - m1
                        logging.info("Notificado en " + str(diff) + " Seg")
                except Exception as e:
                    logging.info("Response JSON: " + str( data_notify ) )
                    print("ERROR POST:", e)
                    ret = False

        return ret
