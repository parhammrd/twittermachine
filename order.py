#!./venv/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import os
import logging
import importlib

import datetime

commandline = ["--add", "--dailyjob", "--AU", "AT"]

dirs = ["Operation", "sqlite"]

for dirName in dirs:
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    else:
        pass

logging.basicConfig(filename='example.log',level=logging.DEBUG)

def dynamic_import(abs_module_path, class_name):
    module_object = importlib.import_module(abs_module_path)
    target_class = getattr(module_object, class_name)

    return target_class

class wizard:
    '''
    it is a generator of jobs in queues
    the porpose is yield a list of queries 
        or generate a json to element requestes
    '''
    name = "dbtwitterquery"
    ndir = "./{}.json".format(name)
    _jobj = {'dbname': 'dailymaily',
        'expire':False,
        'date': datetime.date.today().isoformat(),
        'user':{'fram':30,
            'number': 0,
            'deactive': False,
            'ext': False},
        'tweet': {'fram':30,
            'number': 0,
            'deactive': False,
            'ext': False},
        'query': [{'qname': datetime.date.today().isoformat(),
        'expire' : False,
        'since': None,
        'until': None,
        'idpoint': None,
        'idsince': None}]}
    _qury = {'qname': datetime.date.today().isoformat(),
        'expire' : False,
        'since': None,
        'until': None,
        'idpoint': None,
        'idsince': None}
    def __init__(self, jsonfile=False):
        self.reloadjson()

        if jsonfile:
            js = self.ldjson(jsonfile)
            if not js['expire']:
                point = datetime.date.fromisoformat(js['date'])
                limitqu = abs(point - datetime.date.today())
                if not limitqu:
                    js['date'] = datetime.date.today().isoformat()
                    if js['dbname'] == 'dailymaily':
                        js['query'].append(self._qury)

                self.range = len( js['query'])
                # self.mkjson(js) 

    def yieldqueries(self):
        return range(self.range)

    def revname(self):
        return self.name

    def revdir(self):
        return self.ndir

    def mkjson(self, js):
        with open(self.ndir, "w") as dbq:
            json.dump(js, dbq)

    def ldjson(self, job):
        with open("./Operation/"+job, "r") as dbtquery:
            jsn = json.load(dbtquery)

        return jsn

    def reloadjson(self):
        if os.path.exists(self.ndir):
            with open(self.ndir, "r") as dbq:
                jsn = json.load(dbq)
            with open("./Operation/"+jsn["dbname"]+".json", "w+") as dbtquery:
                json.dump(jsn, dbtquery)
        else:
            return self.mkjson(self._jobj)

if __name__ == "__main__":

    if not sys.argv[1] in commandline:
        logging.error("Flag Error")
        sys.exit()
    elif sys.argv[1] == "--add":
        wiz = wizard()

        quit()

    elif sys.argv[1] == "--AU":

        wiz = wizard()

        uevent = dynamic_import("sqlTM", "uevent")
        uevent(0)

    elif sys.argv[1] == "--AT":

        uevent = dynamic_import("sqlTM", "uevent")
        uevent(0)

    elif sys.argv[1] == "--dailyjob":
        oper = os.listdir('./Operation/')

        for job in oper:
            if job.endswith('.json'):
                wiz = wizard(job)
                print("{} event start".format(job[:-4]))
                
                uevent = dynamic_import("sqlTM", "uevent")

                for thread in wiz.yieldqueries():
                    uevent(thread)
    
