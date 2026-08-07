#!/usr/bin/python
try:
    import logging
    import sys
    import os
    from flask import Blueprint, jsonify, redirect, send_from_directory, request
    from service.notification_service import NotificationService

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

notification_blueprint = Blueprint('notification', __name__)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

@notification_blueprint.route('/notification/<path:subpath>', methods=['POST'])
def notification(subpath: str):
    # POST / PUT
    logging.info("Reciv " + str(request.method) + " Contex: /notification/" + str(subpath))
    logging.info("Reciv Data: " + str(request.data))
    logging.info("Reciv Header :\n" + str(request.headers))

    request_data = {
        'method': request.method,
        'x_api_key': request.headers.get('x-api-key'),
        'type': None,
        'data': None
    }

    json_body = request.get_json()
    if json_body:
        request_data['type'] = json_body.get('type')
        request_data['data'] = json_body.get('data')

    service = NotificationService()
    data_response, http_code = service.process(request_data, subpath)
    del service
    return jsonify(data_response), http_code
