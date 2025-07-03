#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import time
    import smtplib
    from email.message import EmailMessage
    import threading

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class EmailNotification():

    def sendMailMessage(self, to: str, subject: str, body: str, client):
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587        
        if client is not None :
            name_thread = '[' + threading.current_thread().name + '-' + str(threading.get_native_id()) + '] '
            success = True
            try :
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = str(client['mail_user'])
                msg['To'] = to
                msg.set_content(body)

                logging.info(name_thread + "Connect to Server Mail..." )
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.connect(smtp_server, smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()
                logging.info(name_thread + "Login on Server Mail..." )
                server.login(str(client['mail_user']), str(client['password']))
                server.send_message(msg)
                logging.info(name_thread + "Mail Message sent to " + str(to) + " ..." )
                server.quit()
            except Exception as e:
                print(name_thread + "ERROR Mail:", e)
                success = False
        return success
        