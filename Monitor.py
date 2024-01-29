#!/usr/bin/python

try:
    import logging
    import sys
    import os
    from flask import Flask, jsonify, redirect, send_from_directory, request, render_template
    from flask_cors import CORS
    from CheckStatus import CheckStatus
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
filehandle = logging.FileHandler('Monitor.log')
filehandle.setLevel(logging.INFO)
filehandle.setFormatter(formatter)
# se meten ambas configuraciones
root.addHandler(handler)
root.addHandler(filehandle)
logger = logging.getLogger('HTTP')

# ===============================================================================
# Inicia App
# ===============================================================================
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": ["dev.jonnattan.com"]}})

# ===============================================================================
# Variables de entorno
# ===============================================================================
ROOT_DIR = os.path.dirname(__file__)
#===============================================================================
# Redirige
#===============================================================================
@app.route('/', methods=['GET', 'POST', 'PUT'])
def index():
    return redirect('/info'), 302

#===============================================================================
# Redirige
#===============================================================================
@app.route('/info/<path:subpath>', methods=('GET', 'POST','PUT'))
def proccess_api( subpath ) :
    logging.info("Reciv solicitude endpoint: " + subpath )
    return redirect('/info'), 302

#===============================================================================
# Llamada API
#===============================================================================
@app.route('/info', methods=['GET', 'POST', 'PUT'])
def api() :
    logger.info("ROOT_DIR: " + str(ROOT_DIR) )
    logger.info("ROOT_DIR: " + app.root_path)
    return jsonify({
        "Servidor": "Oracle Cloud",
        "Nombre": "Jonnattan G",
        "Linkedin":"https://www.linkedin.com/in/jonnattan/"
    })
#===============================================================================
# Cualquier pagina que ocupe JS desde este servidor para por ac'a
#===============================================================================
@app.route('/page/js/<path:namejs>')
def process_jsfile( namejs ):
    file_path = os.path.join(ROOT_DIR, 'static')
    file_path = os.path.join(file_path, 'js')
    return send_from_directory(file_path, str(namejs) )

#===============================================================================
# Redirige
#===============================================================================
@app.route('/web', methods=['GET'])
def web():
    return render_template( 'page.html' )

#===============================================================================
# Llamada API
#===============================================================================
@app.route('/status', methods=['POST'])
def status() :
    check = CheckStatus()
    data, code = check.getStatusPages( request )
    del check
    return jsonify( data ), code

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
