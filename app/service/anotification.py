#!/usr/bin/python
try:
    import logging
    import os
    from abc import ABC, abstractmethod

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class ANotification(ABC):
    @abstractmethod
    def send_message(self, data: dict, client: str) -> bool:
        pass

