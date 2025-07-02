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
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    def sendMailMessage(self, to, subject, text):
        success = True
        try :
            msg = EmailMessage()
            msg['Subject'] = str(subject)
            msg['From'] = str(self.user)
            msg['To'] = str(to)
            msg.set_content(str(text))
            logging.info("Connect to Server Mail..." )
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.connect(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            logging.info("Login on Server Mail..." )
            server.login(self.user, self.password)
            server.send_message(msg)
            logging.info("Mail Message sent..." )
            server.quit()
        except Exception as e:
            print("ERROR Mail:", e)
            success = False
        return success
        