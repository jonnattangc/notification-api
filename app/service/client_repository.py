#!/usr/bin/python
try:
    import logging
    import sys
    import os
    import pymysql.cursors

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class ClientRepository():
    db = None

    def __init__(self):
        try:
            host = os.environ.get('HOST_BD', 'None')
            user = os.environ.get('USER_BD', 'None')
            password = os.environ.get('PASS_BD', 'None')
            port = int(os.environ.get('PORT_BD', 3306))
            eschema = str(os.environ.get('SCHEMA_BD', 'gral-purpose'))
            self.db = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=eschema,
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            print("ERROR BD __init__() :", e)
            self.db = None

    def __del__(self):
        if self.db is not None:
            self.db.close()

    def get_client(self, apikey: str):
        client = None
        try:
            if self.db is not None:
                cursor = self.db.cursor()
                sql = """select * from clients where apikey = %s"""
                cursor.execute(sql, (apikey,))
                results = cursor.fetchall()
                for row in results:
                    client = {
                        'id'            : str(row['id']),
                        'phone_origin'  : str(row['ws_phone_id']),
                        'bearer_token'  : str(row['ws_bearer_token']),
                        'company_name'  : str(row['company']),
                        'mail_user'     : str(row['mail_user']),
                        'mail_pass'     : str(row['mail_pass']),
                        'meta_filter'     : str(row['meta_filter']),
                        'api_key'       : str(row['apikey'])
                    }
                    logging.info("Client found: " + str(client['company_name']))
        except Exception as e:
            print("ERROR BD get_client():", e)
        return client
