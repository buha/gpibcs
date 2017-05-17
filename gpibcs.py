import configparser
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from PyQt5 import QtWidgets
from qplaintexteditlogger import QPlainTextEditLogger
from version import updateVersion

def confparse(filename, cfg):
    '''
    Function that handles configuration file parsing.
    :param filename: the .conf file path
    :param cfg: a dictionary to populate with parsed configuration (typically empty)
    :return: nothing
    '''

    def confparseExHandle(filename, e):
        if type(e) is ValueError:
            sys.exit(filename + ': ' + str(e))

        elif type(e) is configparser.NoOptionError or type(e) is configparser.NoSectionError:
            # We have hardcoded default values for the configuration logging
            # so it's safe to ignore this exception
            pass
        else:
            gpibtester = 'An exception of type {0} occurred. Arguments:\n{1!r}'
            message = gpibtester.format(type(e).__name__, e.args)
            sys.exit(message)

    # Initialize a config
    parser = configparser.RawConfigParser(delimiters=('='),
                                          comment_prefixes=('#'),
                                          inline_comment_prefixes=('#'),
                                          empty_lines_in_values=False)

    # try to open the configuration file
    try:
        parser.read(filename)
    except IOError:
        pass
    except configparser.ParsingError as e:
        sys.exit('{0}, line {1}: file has no sections defined.'.format(e.args[0], e.args[1]))
    except configparser.DuplicateOptionError as e:
        sys.exit('{0}, line {1}: \"{2}\" is defined more than once.'.format(e.args[2], e.args[3], e.args[1]))
    except configparser.DuplicateSectionError as e:
        sys.exit('{0}, line {1}: \"[{2}]\" is defined more than once.'.format(e.args[1], e.args[2], e.args[0]))
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['logFileName'] = parser.get('logging', 'logFileName')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['logFileSize'] = parser.getint('logging', 'logFileSize')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['logFileLevel'] = 10 * parser.getint('logging', 'logFileLevel')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['logConsoleLevel'] = 10 * parser.getint('logging', 'logConsoleLevel')
        if (cfg['logConsoleLevel'] > logging.CRITICAL or
                    cfg['logConsoleLevel'] == logging.NOTSET or
                    cfg['logFileLevel'] > logging.CRITICAL or
                    cfg['logFileLevel'] == logging.NOTSET):
            raise ValueError('logConsoleLevel must be an integer in the range [1...5]')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        if cfg['gpibDevice'] != 'none':
            cfg['gpibDevice'] = parser.get('gpib', 'gpibDevice')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['gpibTimeout'] = parser.get('gpib', 'gpibTimeout')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        cfg['lastUsedDir'] = parser.get('gui', 'lastUsedDir')
    except Exception as e:
        confparseExHandle(filename, e)

    try:
        dirsString = parser.get('gui', 'autoLoadDirs')
        dirsList = [e.strip() for e in dirsString.split(',')]
        cfg['autoLoadDirs'] = dirsList
    except Exception as e:
        confparseExHandle(filename, e)

    return parser

def loggingsetup(cfg, logginghandler):
    '''
    Function that initializes the logging service.
    :param cfg: a pre-populated dictionary
    :return: nothing
    '''
    # create a rotating logger to a file
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(cfg['logFileLevel'])
    fileHandler = RotatingFileHandler(os.path.join(cfg['configDir'], cfg['logFileName']), maxBytes=cfg['logFileSize'], backupCount=5)
    fileHandler.setLevel(cfg['logFileLevel'])
    fileFormatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y/%d/%m %H:%M:%S')
    fileHandler.setFormatter(fileFormatter)

    # define a Handler which writes INFO messages or higher to the sys.stderr
    consoleLogger = QPlainTextEditLogger(logginghandler)
    # set the console logger level
    consoleLogger.setLevel(cfg['logConsoleLevel'])
    # set a simpler format
    consoleFormatter = logging.Formatter('%(asctime)s.%(msecs)03d  %(levelname)-8s %(message)s', datefmt='%H:%M:%S')
    # tell the handler to use this format
    consoleLogger.setFormatter(consoleFormatter)

    # add the handlers to the root logger
    rootLogger.addHandler(fileHandler)
    rootLogger.addHandler(consoleLogger)

def main(debug):
    # make sure we're displaying the correct version before importing ui code
    updateVersion()
    import ui

    # default configuration
    cfg = {}
    cfg['logFileName'] = os.path.basename(__file__).split('.')[0] + '.log'
    cfg['logFileSize'] = 1024000
    cfg['logFileLevel'] = logging.DEBUG
    cfg['logConsoleLevel'] = logging.INFO
    if debug:
        cfg['gpibDevice'] = 'none'
    else:
        cfg['gpibDevice'] = ''
    cfg['gpibTimeout'] = 1
    cfg['installDir'] = os.path.dirname(os.path.realpath(__file__))
    if (os.name == 'posix'):
        cfg['configDir'] = os.path.expanduser('~/.config/gpibcs')
        os.makedirs(cfg['configDir'], exist_ok=True)
    else:
        cfg['configDir'] = os.path.expanduser('~\AppData\Local\gpibcs')
        os.makedirs(cfg['configDir'], exist_ok=True)
    cfg['lastUsedDir'] = cfg['configDir']
    sequenceDir = os.path.join(cfg['installDir'], 'sequence')
    cfg['autoLoadDirs'] = [sequenceDir, cfg['configDir']]

    # find out which .conf file we are using
    filename = os.path.join(cfg['configDir'], 'gpibcs.conf')

    # create config file template if it does not exist
    if not os.path.isfile(filename):
        with open(filename, 'w') as f:
            f.write('[logging]\n\n[gpib]\n\n[gui]\n\n')
        f.close()

    # overwrite configuration with the contents of .conf file
    parser = confparse(filename, cfg)

    # set up graphics
    app = QtWidgets.QApplication(sys.argv)
    form = ui.GPIBCSWindow(cfg, parser)

    # draw
    form.show()
    s = app.exec_()

    # finish properly
    sys.exit(s)

if __name__ == '__main__':
    debug = True if len(sys.argv) > 1 and sys.argv[1] == '--debug' else False
    main(debug)
