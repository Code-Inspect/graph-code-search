import rdflib.plugins.parsers.nquads as quads
from rdflib.plugin import Plugin
import rdflib.plugins.stores.berkeleydb
from rdflib import Graph
import berkeleydb
import rdflib.parser as rdfParser
import rdflib.plugins.parsers.ntriples as triples
import sys
import re
import pickle
import os

print(berkeleydb.db)
print(rdflib.plugins.stores.berkeleydb.has_bsddb)

 #1 attribute based collection"
 #2 class based collection
 #3 property type collection


g = rdflib.ConjunctiveGraph('BerkeleyDB', identifier='quad1')
parseq = quads.NQuadsParser()

arg = sys.argv
file = arg[1]
name = arg[2]
store = arg[3]

storeList = {}
if os.path.isfile("DB/lists.pickle"):
            storeList = pickle.load( open( "DB/lists.pickle", "rb" ) )
else:
    storeList["triplets"] = []
    storeList["quads"] = []
    storeList["AC"] = []
    storeList["CC"] = []
    storeList["ACC"] = []

try:
    store_dir = ""
    if store == "4":
        print("Quads")
        store_file = "DB/quads/"+name
    elif store == "3":
        print("Triplets")
        store_file = "DB/triplets/"+name
    else:
        raise Exception
    if name in storeList["triplets"] or name in storeList["quads"] or name in storeList["AC"] or name in storeList["CC"] or name in storeList["ACC"]:
        print("Name already taken!")
    else:
        script_dir = os.path.dirname(__file__) 
        path = os.path.join(script_dir, file)
        pathFile = os.path.join(script_dir, store_file)
        readFile = open(path, 'rt' )
        g.open(pathFile, create=True)

        size = 0
        i= 0
        errNo = 0
        for line in readFile.readlines():
            i +=1
            if line.isspace() or not line:
                break
            else:
                size += 1
            insert = ""
            tri = ""
            graph = ""
            if store == "3":
            	tri = line
            else:	
            	tri =  re.split(r"<[^<>]+>\s+\.",line)[0]
            	graph = re.search(r"<[^<>]+>\s+\.", line).group()[:-1]
            
            if store == "4":
                insert = "INSERT DATA { GRAPH "+graph+" {"+tri+"} } "
            else:
                insert = "INSERT DATA  {"+tri+"} "
            g.update(insert)

      

    if store == "4":
        storeList["quads"].append(name)
    else:
        storeList["triplets"].append(name)
              
    pickle.dump( storeList, open( "DB/lists.pickle", "wb" ) )
except Exception:
    print(( "Triplets(3) or Quads(4)! Or another error!"))

