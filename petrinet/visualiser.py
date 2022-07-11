import graphviz as gv

def viz_pt(net,markingid) :    
 dot= gv.Digraph(format="svg")
 dot.clear()
 for key in net.markings:
    if key.id==markingid:
     for place,mark in key.marking:
      dot.node(place, place+"{"+ str(mark) + "}")

 for key in net.transitions:
     dot.node(key, shape="square")

 for elem in net.edges:
     dot.edge(elem.get_source(net).id,elem.get_target(net).id)
 
 return dot.pipe(encoding='utf-8')