import os
import re

from configparser import SafeConfigParser
from datetime import datetime


JOB_VERSION = 2
DATE_MIN = datetime(2013, 1, 1)
INCREMENTAL_DATE = os.getenv('ZUORA_INCREMENTAL_DATE_OVERRIDE')


def parse_environment():
    myDir = os.path.dirname(os.path.abspath(__file__))
    myPath = os.path.join(myDir, '../config', 'environment.conf')
    EnvParser = SafeConfigParser()
    EnvParser.read(myPath)

    return {
        'username': EnvParser.get('ZUORA', 'username'),
        'password': EnvParser.get('ZUORA', 'password'),
        'url': EnvParser.get('ZUORA', 'url'),
        'partner_id': EnvParser.get('ZUORA', 'partner_id'),
        'project_id': EnvParser.get('ZUORA', 'project_id'),
    }


def getPGCreds():
    myDir = os.path.dirname(os.path.abspath(__file__))
    myPath = os.path.join(myDir, '../config', 'environment.conf')
    EnvParser = SafeConfigParser()
    EnvParser.read(myPath)
    username = EnvParser.get('POSTGRES', 'user')
    password = EnvParser.get('POSTGRES', 'pass')
    host = EnvParser.get('POSTGRES', 'host')
    database = EnvParser.get('POSTGRES', 'database')
    port = EnvParser.get('POSTGRES', 'port')
    return (username, password, host, database, port)


def getZuoraFields(item):
    myDir = os.path.dirname(os.path.abspath(__file__))
    myPath = os.path.join(myDir, '../config', 'zuoraFields.conf')
    FieldParser = SafeConfigParser()
    FieldParser.read(myPath)
    fields = re.split(r'\s*,\s*', FieldParser.get(item, 'fields'))
    return fields


def getObjectList():
    myDir = os.path.dirname(os.path.abspath(__file__))
    myPath = os.path.join(myDir, '../config', 'zuoraFields.conf')
    ObjectList = SafeConfigParser()
    ObjectList.read(myPath)
    obj = ObjectList.get('Zbackup', 'objects')
    obj = obj.replace(" ", "")
    objList = obj.split(",")
    return objList


environment = parse_environment()
