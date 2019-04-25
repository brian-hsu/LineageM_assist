import logging
from datetime import datetime


def disabled():
    logging.disable(50)


class MyLOG:
    def __init__(self, version_cycle, logger_name):
        self.logger_name = logger_name
        self.version_cycle = version_cycle
        self.logger = logging.getLogger(logger_name)

        if not self.logger.handlers:
            self.set_log()

    def set_log(self):
        fm = '%(asctime)s -%(levelname)s- [%(module)s.%(funcName)s, line %(lineno)d]: %(message)s'
        formatter = logging.Formatter(fm)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        if self.version_cycle is 'alpha':
            self.logger.setLevel(10)
            self.logger.info('MyLOG:version_cycle is %s now' % self.version_cycle)
        elif self.version_cycle is 'beta':
            self.logger.setLevel(20)
            date = datetime.now().strftime('%Y-%m-%d_%H.%M.%S.%f')[:-3]
            logfile = 'exec_' + date + '.log'
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.info('MyLOG:version_cycle is "%s" now' % self.version_cycle)
        elif self.version_cycle is 'rc':
            disabled()
        else:
            print('version_cycle Must be [alpha=console,beta=logfile,rc=disabled]')
