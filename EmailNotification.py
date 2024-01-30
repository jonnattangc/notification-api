#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import time
    import smtplib
    from email.message import EmailMessage

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class EmailNotification():

    user = os.environ.get('USER_MAIL','None')
    password = os.environ.get('PASS_MAIL','None')
    api_key = os.environ.get('API_KEY_MAIL','None')
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    def processSendEmail(self, request):
        m1 = time.monotonic()
        success = True

        response = { 
            "success": success, 
            "msg": "Mensaje enviado exitosamente" 
        }
        code = 200

        try :
            if request.headers['x-api-key'] == self.api_key :
                request_data = request.get_json()
                success, msg = self.sendMailMessage(request_data['to'], request_data['type'], request_data['msg'])
                if success == False :
                    code = 500
            else :
                success = False
                msg = "No Autorizado"
                code = 401
        except Exception as e:
            print("ERROR Mail:", e)
            success = False
            msg = str(e) 
            code = 500

        response = {
            "success": success, 
            "msg": str(msg) 
        }            

        logging.info("Procesado en " + str(time.monotonic() - m1) + " Seg")
        return response, code 
    

    def sendMailMessage(self, to, type, text):
        success = True
        response = 'Mensaje Enviado Exitosamente'
        try :
            msg = EmailMessage()
            msg['Subject'] = f'Mensaje de {str(type)}'
            msg['From'] = str(self.user)
            msg['To'] = str(to)
            msg.set_content(str(text))
            logging.info("Connect Server Mail..." )
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.connect(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            logging.info("Login on Server Mail..." )
            server.login(self.user, self.password)
            server.send_message(msg)
            logging.info("Message sent..." )
            server.quit()
        except Exception as e:
            print("ERROR Mail:", e)
            success = False
            response = str(e)
        return success, response
        