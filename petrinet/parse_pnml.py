#-------------------------------Parsing PNML ---------------------------------------------------- 

from xml.etree.ElementTree import fromstring, ElementTree # XML parser
from petrinet import petrinet as pt

def parse_pnml(tree):
    root = tree.getroot()
   
    
    for node in root.iter("net"):
        # petri net object
        net = pt.PetriNet()

        # getting places
        for place_node in node.iter("place"):
            place = pt.Place()
            place.id = place_node.get("id")

            if place_node.find("./name/text")==None:
                place.name = place.id
                         
            else:
                place.name= place_node.find("./name/text").text
                
            net.places[place.id] = place
    
        # getting transitions
        for t in node.iter("transition"):
            #create transition 
            transition = pt.Transition()
            transition.id = t.get("id")

            if t.find("./name/text")==None:
                transition.name= transition.id
            else:transition.name=t.find("./name/text").text 
                

            net.transitions[transition.id] = transition
           
        # getting edges 
        for arc in node.iter("arc"):
            edge = pt.Edge()
            net.edges.append(edge)

            edge.id = arc.get("id")
            edge.input = arc.get("source")
            edge.output = arc.get("target")
            

    #Give the transitions and places new ids starting with 1 and change the edges inputs and outputs accordingly
    #If transition name=id then change name to the new id as well 
    pi=1
    right_ids_places={}
    changed_elem={}#{edgeobject: [False,False] } 
    for e in net.edges:
        changed_elem[e]=[False,False] 

    for elem in net.places:

        if net.places[elem].id==net.places[elem].name:
            net.places[elem].name="p"+str(pi)
        net.places[elem].id="p"+str(pi)
        
        right_ids_places["p"+str(pi)]=net.places[elem]

        for e in net.edges:

            if e.input==elem and not changed_elem[e][0] : 
                e.input="p"+str(pi)
                changed_elem[e][0]=True
            if e.output==elem and not changed_elem[e][1] :
                e.output="p"+str(pi)
                changed_elem[e][1]=True

        pi+=1

    net.places=right_ids_places

    ti=1
    right_ids_transitions={}
    changed_elem={}#{edgeobject: [False,False] } 
    for e in net.edges:
        changed_elem[e]=[False,False]

    for elem in net.transitions:

        if net.transitions[elem].id==net.transitions[elem].name:
            net.transitions[elem].name="t"+str(ti)
        net.transitions[elem].id="t"+str(ti)

        right_ids_transitions["t"+str(ti)]=net.transitions[elem]

        for e in net.edges:

            if e.input==elem and not changed_elem[e][0]:
                e.input="t"+str(ti)
                changed_elem[e][0]=True

            if e.output==elem and not changed_elem[e][1] :
                e.output="t"+str(ti)
                changed_elem[e][1]=True

            
        ti+=1
    
    net.transitions=right_ids_transitions
    return net

def parse_pnml_file(file):
 tree = ElementTree.parse(file)
 return parse_pnml(tree)

def parse_pnml_string(xmlstring):
 tree = ElementTree(fromstring(xmlstring))
 return parse_pnml(tree)