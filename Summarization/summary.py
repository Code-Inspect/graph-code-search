import pickle
import os.path as osp

import site
import sys

site.addsitedir('../../lib')  # Always appends to end

print(sys.path)

import timeit
import re
import pathlib
#disable randomization of hash
#former group used randomized hash
import os
import sys
hashseed = os.getenv('PYTHONHASHSEED')
if not hashseed:
  os.environ['PYTHONHASHSEED'] = '0'
  os.execv(sys.executable, [sys.executable] + sys.argv)

import rdflib
import rdflib.parser as rdflib_parser
import rdflib.plugins.parsers.ntriples as triples
import rdflib.plugins.parsers.nquads as quads

#disable randomization of hash
import os
import sys
hashseed = os.getenv('PYTHONHASHSEED')
if not hashseed:
  os.environ['PYTHONHASHSEED'] = '0'
  os.execv(sys.executable, [sys.executable] + sys.argv)



class vertex_graph():
    """
    A class to represent a vertex of the RDF graph that contains information for the sampling and summary
    """

    def __init__(self,name):

        self.name = name
        self.edges = []  # for sampling



class eqcs():
    """
    first all vertices then the eqcs are created for statisitics
    """

    def __init__(self, s, ps,ts):
        self.members = set()
        self.members.add(s)
        self.edgesP = ps
        self.edgesT = ts
        self.degree = len(ps)+len(ts)
        self.type = type


class graph_for_summary():
    """
    A class used to calculate graph summaries
    """

    def __init__(self):

        self.num_vertices = 0  # current number vertices
        self.num_predicates = 0  # self.num_features = 0 #current number of predeciate
        self.count_edge = 0

        # subjects
        self.current_subjects = {}  # Key-Value Store of current subjects with the index of the subject/vertex as key and the subject as value
        self.current_subjects_set = set()  # for testing if seen at this snapshot
        self.unique_subjects = []  # List is used to give a subject its index

        # EQCs
        self.label_dict = {}  # for traininig  # key: hash value: list( subjects )



    def create_graph_information(self, path):
        """
        Calculates the needed data to train the networks


        Args:
            path (str): path to the nq-file
        """

        with open(path) as f:
            number_lines = sum(1 for _ in f)

        print("Files has", number_lines, "lines.")

        # Using readline()
        with open(path) as f:
            count_line = 0
            count_invalid = 0

            parseq = quads.NQuadsParser()
            sink = rdflib.ConjunctiveGraph()
            lines = []
            while True:
                # Get next line from file
                line = f.readline()
                lines.append(line)
                # if line is empty
                # end of file is reached
                if not line:
                    break

                count_line += 1

                if count_line % 10000 == 0:
                    print("Read line", count_line, "of", number_lines, "(", count_line / number_lines * 100.0, "%)")

                sink = rdflib.ConjunctiveGraph()
                # parseq
                strSource = rdflib_parser.StringInputSource(line.encode('utf-8'))

                try:
                    # try parsing the line to a valid N-Quad
                    parseq.parse(strSource, sink)

                    self.count_edge += 1

                    # write the validated N-Quad into the filtered File

                    # print( list(sink.subjects()),list(sink.predicates()),list(sink.objects() ) )
                    s = str(list(sink.subjects())[0])
                    p = str(list(sink.predicates())[0])
                    o = str(list(sink.objects())[0])  # is also a subject. In worst case, it has no edges

                    # for current subject
                    if (s in self.current_subjects_set):
                        self.current_subjects[s].edges.append((p, o))
                    else:
                        self.unique_subjects.append(s)
                        self.current_subjects_set.add(s)
                        self.current_subjects[s] = vertex_graph(s)
                        self.current_subjects[s].edges.append((p, o))
                        self.num_vertices += 1



                except triples.ParseError:
                    # catch ParseErrors and write the invalidated N-Quad into the trashed File
                    count_invalid += 1

                    # print the number of Errors and current trashed line to console
                    print('Wrong Line Number ' + str(f'{count_invalid:,}') + ': ' + line)

            print("lines read:", count_line)
            print("invalid lines read:", count_invalid)
            f.close()
            return lines

    def calculate_graph_summary(self,gs,eqcs):
        """
        Calculate the by the index defined graph summary on the prepared data
        """
        # 2. create graph summary over whole graph
        # go through graph information and calculate labels and features
        if (gs == 1):
            self.attribute_based_collection_impl(eqcs)
        elif (gs == 2):
            self.class_based_collection_impl(eqcs)
        elif (gs == 3):
            self.property_type_collection_impl(eqcs)


    def attribute_based_collection_impl(self,eqcs):
        """
        Implementation to calculate the attribute based collection

        """
        self.based_collection_impl(True, False,eqcs)

    def class_based_collection_impl(self,eqcs):
        """
        Implementation to calculate the class based collection

        """
        self.based_collection_impl(False, True,eqcs)

    def property_type_collection_impl(self,eqcs):
        """
        Implementation to calculate the property type collection


        """
        self.based_collection_impl(True, True,eqcs)

    def add_to_label_dict(self, tmp_hash, s ,tmp_property_list,tmp_type_list,eqcsK):
        """
        Add to label_dict with tmp_hash keys and list of subjects values


        Args:
            tmp_hash (int): Calculated hash for the subject
            s (str): Subject name
        """

        if tmp_hash in eqcsK:
            eqcsK[tmp_hash].members.add(s)
        else:
            eqcsK[tmp_hash] = eqcs(s, tmp_property_list,tmp_type_list)

    def is_rdf_type(self, s):
        """
        Check if the given string contains rdf and therefore is an rdf-type


        Args:
            s (str): Feature used by the graph summary model

        Returns:
            bool: If it is a rdf-type
        """
        return "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in s

    def based_collection_impl(self, prop, typ,eqcs):
        """
        Base implementation for the graph summary calculation


        Args:
            prop (bool): If we want to use the property sets
            typ (bool): If we want to use the type sets
        """
        # iterate through all subjects
        for gi in self.current_subjects.items():
            # calculate hash
            tmp_feature_list = []
            tmp_property_list = []
            tmp_type_list = []
            # go through edges of gi
            for h in gi[1].edges:
                
                # check if we want to use the feature in this config
                if (prop == True and self.is_rdf_type(h[0]) == False and h[0] not in tmp_property_list):
                    	tmp_property_list.append(h[0])
                    	tmp_feature_list.append(h[0])

                if (typ == True and self.is_rdf_type(h[0]) == True and h[1] not in tmp_type_list):
                    	tmp_feature_list.append(h[1])
                    	tmp_type_list.append(h[1])



            tmp_feature_list.sort()
            # if  len(tmp_feature_list) >= 3:
            #    print(gi[1].index)
            #    print(self.unique_subjects[gi[1].index])
            tmp_feature_list_string = "".join(tmp_feature_list)
            tmp_hash = hash(tmp_feature_list_string)


            # print("Tmp _hash: "+str(tmp_hash)+" Forme_hash: "+str(former_hash))


            self.add_to_label_dict(tmp_hash, gi[0], tmp_property_list,tmp_type_list,eqcs)

    def createRDF(self,eqcsK, name,typeS,lines):
        script_dir = os.path.dirname(__file__) 

        
        file = ""
        if typeS == "AC":
            file = '../DB/AC/'+name
        elif typeS == "CC":
            file = '../DB/CC/'+name
        else:
            file = '../DB/ACC/'+name
        path= os.path.join(script_dir, file)
        f = open(path,"w+")
        for k in eqcsK.keys():
            v = eqcsK[k]
            ks = "<hash:"+str(k)+">"
            for e in v.edgesP:
                f.write(ks+" <"+e.replace('\n', '\\n').replace('\r', '\\r').replace('\"', '\\"')+"> "+"\"\" .\n")
            for e in v.edgesT:
                f.write(ks+" <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "+"<"+e.replace('\n', '\\n').replace('\r', '\\r').replace('\"', '\\"')+"> .\n")
           # for m in v.members:
           #     f.write(ks + " <member:s> \"" + m.replace('\n', '\\n').replace('\r', '\\r').replace('\"', '\\"')+"\" .\n")
            f.write(ks + " <number_of_members:s> \"" + str(len(v.members))+"\"  .\n")
         
        self.toStore(name.split(".")[-2],typeS,lines)   
            
            
            
            
            
    def toStore(self,name,typeS,lines):
        g = rdflib.ConjunctiveGraph('BerkeleyDB', identifier='quad1')
        storeList = {}
        if os.path.isfile("../DB/lists.pickle"):
            storeList = pickle.load( open( "../DB/lists.pickle", "rb" ) )
        else:
            storeList["triplets"] = []
            storeList["quads"] = []
            storeList["AC"] = []
            storeList["CC"] = []
            storeList["ACC"] = []


        store_file = "../DB/"+typeS+"/"+name
        if name in storeList["triplets"] or name in storeList["quads"] or name in storeList["AC"] or name in storeList["CC"] or name in storeList["ACC"]:
            print("Name already taken!")
        else:
            script_dir = os.path.dirname(__file__) 
            pathFile = os.path.join(script_dir, store_file)
            g.open(pathFile, create=True)
            print(lines)
            size = 0
            i= 0
            errNo = 0

            for line in lines:
                i +=1
                if line.isspace() or not line:
                    break
                else:
                    size += 1
      
                    insert = "INSERT DATA  {"+line+"} "
                    
                g.update(insert)


            storeList[typeS].append(name)

        pickle.dump( storeList, open( "../DB/lists.pickle", "wb" ) )

def main():
    graph = graph_for_summary()
    arg = sys.argv
    file = arg[1]
    split = file.split(".")
    split = str(split[-2])
    split = split.split("/")
    lines = graph.create_graph_information(file)
    eqcs1 = {}  # attribute based collection"
    eqcs2 = {}  # class based collection
    eqcs3 = {}  # property type collection
    graph.calculate_graph_summary(1,eqcs1)
    graph.calculate_graph_summary(2, eqcs2)
    graph.calculate_graph_summary(3, eqcs3)
    
    graph.createRDF(eqcs1, split[-1]+"_AC.rdf","AC",lines)
    graph.createRDF(eqcs2, split[-1]+"_CC.rdf","CC",lines)
    graph.createRDF(eqcs3, split[-1]+"_ACC.rdf","ACC",lines)


if __name__ == '__main__':
    main()
