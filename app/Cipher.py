try:
    import logging
    import sys
    import os
    from Crypto.Cipher import AES
    import base64

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[Cipher] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

ROOT_DIR = os.path.dirname(__file__)

class Cipher() :
    cipher = None
    aes_key = None
    iv = None
    def __init__(self, ) :
        key = os.environ.get('AES_KEY','None')
        self.aes_key = key.encode('utf-8')[:32]
        self.iv = b'1234567890123456'

    def __del__(self):
        self.aes_key = None
        
    def complete( self, data_str : str ) :
        response : str = data_str
        if data_str != None :
            length = len(data_str)
            resto = 16 - (length % 16)
            i = 0
            while i < resto :
                response += " "
                i += 1
        return response.encode()

    def aes_encrypt(self, payload : str ) :  
        data_cipher_str = None
        try :
            data_clear = self.complete(payload) # se lleva a bytes el texto
            cipher = AES.new(self.aes_key, AES.MODE_CBC, self.iv)
            data_cipher = cipher.encrypt(data_clear) # se encriptan los bytes
            if data_cipher != None :
                b64 = base64.b64encode(data_cipher) # se convierten en base64
                data_cipher_str = b64.decode() # pasan a string la cadena de bytes
        except Exception as e:
            print("ERROR Cipher:", e)
            data_cipher_str = None
        return data_cipher_str

    def aes_decrypt(self, data_cipher_str: str ) :        
        data_clear_str = None
        try :
            b64 = data_cipher_str.encode() # string se pasan a bytes
            data_cipher = base64.b64decode(b64) # bytes en base64 se pasan a los bytes para decifrar
            cipher = AES.new(self.aes_key, AES.MODE_CBC, self.iv)
            data_clear = cipher.decrypt(data_cipher) # se desencriptan los bytes
            if data_clear != None :
                data_clear_str = data_clear.decode() # se llega la cadeba de bytes a texto
                data_clear_str = data_clear_str.strip()
        except Exception as e:
            print("ERROR Decipher:", e)
            data_clear_str = None
        return data_clear_str
    