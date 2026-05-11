#!/usr/bin/python
try:
    import logging
    import sys
    import os
    from flask import Flask
    from flask_cors import CORS

    from api.routes import notification_blueprint

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
app = Flask(__name__)
cors = CORS(app, resources={r"/notification/*": {"origins": ["dev.jonnattan.com", "api.jonnattan.cl"]},})
app.register_blueprint(notification_blueprint)

# ===============================================================================
# Metodo Principal que levanta el servidor
# ===============================================================================
if __name__ == "__main__":
    listenPort = 8085
    if len(sys.argv) == 1:
        logger.error("Se requiere el puerto como parametro")
        exit(0)
    try:
        logger.info("Server listen at: " + sys.argv[1])
        listenPort = int(sys.argv[1])
        app.run(host='0.0.0.0', port=listenPort, debug=True)
    except Exception as e:
        print("ERROR MAIN:", e)

    logging.info("PROGRAM FINISH")
