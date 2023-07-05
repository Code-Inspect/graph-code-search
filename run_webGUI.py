from flask import Flask, flash, redirect, url_for, render_template, request, session
from datetime import timedelta

import berkeleydb
import rdflib
import re
import pickle
import os

#fuser -n tcp -k 5000 : to free port 5000 in ubuntu

from datetime import datetime
now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

import logging
script_dir = os.path.dirname(__file__) 
log = os.path.join(script_dir, 'Logs/webGUI'+now+'.log')
logging.basicConfig(
    filename= log,
    filemode='w+',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG
)
app = Flask(__name__)

app.secret_key = "test"  # change key for more security


g = rdflib.ConjunctiveGraph('BerkeleyDB', identifier='mygraph')

currentDataset = ""

storeList = pickle.load( open( "DB/lists.pickle", "rb" )) 
           
datasetsQ = []
datasetsT = []
listTri = []
listQuads = []
listAC = []
listCC = []
listACC = []
for i in storeList["triplets"]:
    datasetsT.append(i)   
    listTri.append(i)
for i in storeList["quads"]:
    datasetsT.append(i)  
    datasetsQ.append(i)   
    listQuads.append(i)
for i in storeList["AC"]:
    datasetsT.append(i)   
    listAC.append(i)
for i in storeList["CC"]:
    datasetsT.append(i)   
    listCC.append(i)
for i in storeList["ACC"]:
    datasetsT.append(i)   
    listACC.append(i)


@app.route("/")
def home():
    logging.info("Called Home/GET")
    return render_template("home.html")


@app.route("/quads", methods=["POST", "GET"])
def quads():
    prefix = []
    prefix.append("None")
    prefix.append("<http://www.w3.org/1999/02/22-rdf-syntax-ns#>")
    prefix.append(" <http://www.w3.org/2000/01/rdf-schema#>")
    prefix.append(" <http://xmlns.com/foaf/0.1/>")
    prefix.append(" <http://www.perceive.net/schemas/relationship/> ")

    datasets4 = datasetsQ.copy()

    requested = {}

    requested["subject"] = ""
    requested["subSu"] = ""
    requested["eSu"] = ""
    requested["strSu"] = ""

    requested["predicate"] = ""
    requested["subPre"] = ""
    requested["ePre"] = ""

    requested["object"] = ""
    requested["subOb"] = ""
    requested["strOb"] = ""

    requested["context"] = ""
    requested["subCo"] = ""
    requested["eCo"] = ""

    requested["answers"] = ""

    if request.method == "POST":
        logging.info("Called Quads/POST")
        #print(requested["subject"])
        dataset = request.form["dataset"]
        if dataset != currentDataset:
            #g.close()
            script_dir = os.path.dirname(__file__) 
            file = ""
            if dataset in listQuads: 
                file = "DB/quads/"+dataset         
            else:
                print("ERROR")
            path = os.path.join(script_dir, file)
            g.open(path, create=False)

        datasets4.insert(0, dataset)

        session.permanent = True  # False default and only saved while browser open. True save for time in timedelta
        sub = request.form["subject"]

        subSu = False
        if "subSu" in request.form:
            subSu = True
        if sub == "" and "eSu" not in request.form:
            subSu = True
        sub1 = ""
        s1 = ""
        s2 = ""
        if "strSu" in request.form:
            s2 = "\"" + sub + "\""
        else:
            s2 = "<" + sub + ">"
        if subSu:
            s1 = "?s"
            s2 = "?s"
            sub1 = " filter( regex(str(?s)," + "\"" + sub + "\"" + " ) )"

        requested["subject"] = sub
        if "subSu" in request.form:
            requested["subSu"] = "checked"
        if "eSu" in request.form:
            requested["eSu"] = "checked"
        if "strSu" in request.form:
            requested["strSu"] = "checked"

        pre = request.form["predicate"]
        predicatePre = request.form["predicatePre"]

        prefix1 = ""
        prefix2 = "<"
        prefix3 = ">"

        if predicatePre != "None":
            prefix1 = "PREFIX pre:" + predicatePre
            prefix2 = "pre:"
            prefix3 = ""

        subPre = False
        if "subPre" in request.form:
            subPre = True
        if pre == "" and "ePre" not in request.form:
            subPre = True

        sub2 = ""
        p1 = ""
        p2 = prefix2 + pre + prefix3
        if subPre:
            p1 = "?p"
            p2 = "?p"
            prefix1 = ""
            sub2 = " filter( regex(str(?p)," + "\"" + pre + "\"" + " ) )"



        prefix.insert(0,predicatePre)

        requested["predicate"] = pre
        if "subPre" in request.form:
            requested["subPre"] = "checked"
        if "ePre" in request.form:
            requested["ePre"] = "checked"

        obj = request.form["object"]
        subOb = False
        if "subOb" in request.form:
            subOb = True
        if obj == "" and "eOb" not in request.form:
            subOb = True

        sub3 = ""
        o1 = ""
        o2 = ""

        if "strOb" in request.form:
            o2 = "\"" + obj + "\""
        else:
            o2 = "<" + obj + ">"

        if subOb:
            o1 = "?o"
            o2 = "?o"
            sub3 = " filter( regex(str(?o)," + "\"" + obj + "\"" + " ) )"

        requested["object"] = obj
        if "subOb" in request.form:
            requested["subOb"] = "checked"
        if "eOb" in request.form:
            requested["eOb"] = "checked"
        if "strOb" in request.form:
            requested["strOb"] = "checked"

        gr = request.form["context"]
        sub4 = ""
        g1 = ""
        g2 = "<" + gr + ">"
        g3 = ""
        subCo = False
        if "subCo" in request.form:
            subCo = True
        if gr == "" and "eCo" not in request.form:
            subCo = True

        if subCo:
            g1 = "?g"
            g2 = "?g"
            g3 = "ORDER BY ?g "
            sub4 = " filter( regex(str(?g)," + "\"" + gr + "\"" + " ) )"

        requested["context"] = gr
        if "subCo" in request.form:
            requested["subCo"] = "checked"
        if "eCo" in request.form:
            requested["eCo"] = "checked"





        query = """
        """ + prefix1 + """
        SELECT """ + g1 + " " + s1 + " " + p1 + " " + o1 + """
        WHERE {
        GRAPH """ + g2 + " " + """ { """ + s2 + " " + p2 + " " + o2 + " " + sub1 + " " + sub2 + " " + sub3 + " " + """}  """ + sub4 + " " + """ }
        """ + g3 + " " + """
        """
        qres = ""
        try:
            qres = g.query(query)
        except:
            logging.error("Query:" + query+"\n")
            return render_template("sparql.html", prefix=prefix,datasets = datasets4,
                                   error="Invalid SPARQL query! The following query caused the exception: \n\n " + query,requested=requested)
        logging.info("Query:"+query+"\n")
        i = 0
        data = []
        for row in qres:
            rs = ""
            if subSu:
                rs = row.s
            else:
                rs = s2

            rp = ""
            if subPre:
                rp = row.p
            else:
                rp = p2

            ro = ""
            if subOb:
                ro = row.o
            else:
                ro = o2

            rg = ""
            if subCo:
                rg = row.g
            else:
                rg = g2

            i += 1
            # data.append(f"{row.s}  {row.p} {row.o} {row.g} ")
            data.append({"s": f"{rs}", "p": f"{rp}", "o": f"{ro}", "g": f"{rg}"})
            if i == 100:
                break
        requested["answers"] = len(qres)
        # eturn redirect(url_for("home"))
        return render_template("sparql.html", data=data,datasets = datasets4, prefix=prefix, requested=requested)
    else:
        logging.info("Called Quads/GET")
        return render_template("sparql.html", prefix=prefix,datasets = datasets4,requested=requested)



@app.route("/triples", methods=["POST", "GET"])
def triples():
    prefix = []
    prefix.append("None")
    prefix.append("<http://www.w3.org/1999/02/22-rdf-syntax-ns#>")
    prefix.append(" <http://www.w3.org/2000/01/rdf-schema#>")
    prefix.append(" <http://xmlns.com/foaf/0.1/>")
    prefix.append(" <http://www.perceive.net/schemas/relationship/> ")
    prefix.append("<r-ast:> ")
    prefix.append("<number of members:>")

    datasets3 = datasetsT.copy()

    requested = {}

    requested["subject"] = ""
    requested["subSu"] = ""
    requested["eSu"] = ""
    requested["strSu"] = ""

    requested["predicate"] = ""
    requested["subPre"] = ""
    requested["ePre"] = ""

    requested["object"] = ""
    requested["subOb"] = ""
    requested["strOb"] = ""

    requested["answers"] = ""

    if request.method == "POST":
        logging.info("Called Triples/POST")
        #print(requested["subject"])

        dataset = request.form["dataset"]
        if dataset != currentDataset:
            #g.close()
            script_dir = os.path.dirname(__file__) 
            file = ""
            if dataset in listTri: 
                file = "DB/triplets/"+dataset
            elif dataset in listQuads: 
                file = "DB/quads/"+dataset
            elif dataset in listAC: 
                file = "DB/AC/"+dataset
            elif dataset in listCC: 
                file = "DB/CC/"+dataset
            elif dataset in listACC: 
                file = "DB/ACC/"+dataset
            else:
                print("ERROR")
            path = os.path.join(script_dir, file)
            print(path)
            g.open(path, create=False)
        datasets3.insert(0, dataset)

        session.permanent = True  # False default and only saved while browser open. True save for time in timedelta
        sub = request.form["subject"]

        subSu = False
        if "subSu" in request.form:
            subSu = True
        if sub == "" and "eSu" not in request.form:
            subSu = True
        sub1 = ""
        s1 = ""
        s2 = ""
        if "strSu" in request.form:
            s2 = "\"" + sub + "\""
        else:
            s2 = "<" + sub + ">"
        if subSu:
            s1 = "?s"
            s2 = "?s"
            sub1 = " filter( regex(str(?s)," + "\"" + sub + "\"" + " ) )"

        requested["subject"] = sub
        if "subSu" in request.form:
            requested["subSu"] = "checked"
        if "eSu" in request.form:
            requested["eSu"] = "checked"
        if "strSu" in request.form:
            requested["strSu"] = "checked"

        pre = request.form["predicate"]
        predicatePre = request.form["predicatePre"]

        prefix1 = ""
        prefix2 = "<"
        prefix3 = ">"

        if predicatePre != "None":
            prefix1 = "PREFIX pre:" + predicatePre
            prefix2 = "pre:"
            prefix3 = ""

        subPre = False
        if "subPre" in request.form:
            subPre = True
        if pre == "" and "ePre" not in request.form:
            subPre = True

        sub2 = ""
        p1 = ""
        p2 = prefix2 + pre + prefix3
        if subPre:
            p1 = "?p"
            p2 = "?p"
            prefix1 = ""
            sub2 = " filter( regex(str(?p)," + "\"" + pre + "\"" + " ) )"



        prefix.insert(0,predicatePre)

        requested["predicate"] = pre
        if "subPre" in request.form:
            requested["subPre"] = "checked"
        if "ePre" in request.form:
            requested["ePre"] = "checked"

        obj = request.form["object"]
        subOb = False
        if "subOb" in request.form:
            subOb = True
        if obj == "" and "eOb" not in request.form:
            subOb = True

        sub3 = ""
        o1 = ""
        o2 = ""

        if "strOb" in request.form:
            o2 = "\"" + obj + "\""
        else:
            o2 = "<" + obj + ">"

        if subOb:
            o1 = "?o"
            o2 = "?o"
            sub3 = " filter( regex(str(?o)," + "\"" + obj + "\"" + " ) )"

        requested["object"] = obj
        if "subOb" in request.form:
            requested["subOb"] = "checked"
        if "eOb" in request.form:
            requested["eOb"] = "checked"
        if "strOb" in request.form:
            requested["strOb"] = "checked"





        query = """
        """ + prefix1 + """
        SELECT """ + s1 + " " + p1 + " " + o1 + """
        WHERE {
         """ + s2 + " " + p2 + " " + o2 + " " + sub1 + " " + sub2 + " " + sub3 + " " + """}  """

        qres = ""
        try:
            qres = g.query(query)
        except:
            logging.error("Query:" + query+"\n")
            return render_template("sparql2.html", prefix=prefix,datasets = datasets3,
                                   error="Invalid SPARQL query! The following query caused the exception: \n\n " + query,requested=requested)
        logging.info("Query:" + query+"\n")
        i = 0
        data = []
        for row in qres:
            rs = ""
            if subSu:
                rs = row.s
            else:
                rs = s2

            rp = ""
            if subPre:
                rp = row.p
            else:
                rp = p2

            ro = ""
            if subOb:
                ro = row.o
            else:
                ro = o2



            i += 1
            # data.append(f"{row.s}  {row.p} {row.o} {row.g} ")
            data.append({"s": f"{rs}", "p": f"{rp}", "o": f"{ro}"})
            if i == 100:
                break
        requested["answers"] = len(qres)
        # eturn redirect(url_for("home"))
        return render_template("sparql2.html", data=data,datasets = datasets3, prefix=prefix, requested=requested)
    else:
        logging.info("Called Triples/GET")
        return render_template("sparql2.html", prefix=prefix,datasets = datasets3,requested=requested)


if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
    

