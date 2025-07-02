#!/usr/bin/python

try:
    import logging
    import sys
    import os
    from flask import Flask, jsonify, redirect, send_from_directory, request, render_template
    from flask_cors import CORS
    from Notification import Notification
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

# ===============================================================================
# Configuraci'on de Registro de Log
# ===============================================================================
FORMAT = '%(asctime)s %(levelname)s : %(message)s'
root = logging.getLogger()
root.setLevel(logging.INFO)
formatter = logging.Formatter(FORMAT)
# Log en pantalla
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
root.addHandler(handler)

logger = logging.getLogger('HTTP')

# ===============================================================================
# Inicia App
# ===============================================================================
CONTEXT_PATH : str = '/notification'

app = Flask(__name__)
cors = CORS(app, resources={r"/notification/*": {"origins": ["dev.jonnattan.com", "api.jonnattan.cl"]},})

# ===============================================================================
# Variables de entorno
# ===============================================================================
ROOT_DIR = os.path.dirname(__file__)

#===============================================================================
# Redirige
#===============================================================================
@app.route( CONTEXT_PATH + '/<path:subpath>', methods=['GET', 'POST', 'PUT'])
def notification( subpath: str  ) : 
    notification : Notification = Notification() 
    data_response, http_code = notification.process( request, subpath )
    del notification
    return jsonify( data_response ), http_code

#===============================================================================
# Redirige
#===============================================================================
@app.route( CONTEXT_PATH + '/info/<path:subpath>', methods=('GET', 'POST','PUT'))
def proccess_api( subpath ) :
    logging.info("Reciv solicitude endpoint: " + subpath )
    return redirect('/info'), 302

#===============================================================================
# Llamada API
#===============================================================================
@app.route( CONTEXT_PATH + '/info', methods=['GET', 'POST', 'PUT'])
def api() :
    logger.info("ROOT_DIR: " + str(ROOT_DIR) )
    logger.info("ROOT_DIR: " + app.root_path)
    return jsonify({
        "API": "API de notificación",
        "Nombre": "Jonnattan G"
    })
#===============================================================================
# Cualquier pagina que ocupe JS desde este servidor para por ac'a
#===============================================================================
@app.route( CONTEXT_PATH + '/page/js/<path:namejs>')
def process_jsfile( namejs ):
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'js')
    return send_from_directory(file_path, str(namejs) )

#===============================================================================
# Redirige
#===============================================================================
@app.route( CONTEXT_PATH + '/web', methods=['GET'])
def web():
    return render_template( 'page.html' )


# ===============================================================================
# Metodo Principal que levanta el servidor
# ===============================================================================
if __name__ == "__main__":
    listenPort = 8085
    if(len(sys.argv) == 1):
        logger.error("Se requiere el puerto como parametro")
        exit(0)
    try:
        logger.info("Server listen at: " + sys.argv[1])
        listenPort = int(sys.argv[1])
        app.run( host='0.0.0.0', port=listenPort, debug=True)
    except Exception as e:
        print("ERROR MAIN:", e)

    logging.info("PROGRAM FINISH")
