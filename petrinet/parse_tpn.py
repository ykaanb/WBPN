from petrinet import petrinet as pt

#This method is only for getting the id`s (pnumber and tnumber) of the objects out of the dictionaries plas and trans
#because input output dictionaries only contain names not ids, to get the ids` of sourceid & targetid of a single input or an output we need this method. 
def getId(objectdict, name):
    for key in objectdict:
        if name==objectdict[key]:
            return key

def parse_tpn(Line = []):

 #Petri net object
 net=pt.PetriNet()
 #@plas   - place dictionary { pnumber : pname }
 plas={}
 #@trans  - transition dictionary { tnumber : tname }
 trans={}
 #@input  - input dictionary { innumber : { from_p : pname , to_t : tname } } 
 input={}
 #@output - output dictionary { outnumber : { to_p : pname , from_t : tname } }
 output={}
 #@ti - to iterate transition number and also to access the transition to relate to its in and out 
 ti=1
 #@i  - to iterate place number 
 i=1
 #@ni - to iterate input number 
 ni=1
 #@oi - to iterate output number
 oi=1 

 for element in Line:

    if "place" in element:
       #A list that contains a line with place in form of exp: ["\n","\n\nplace","\n\n","\np3"]
        f=element.split(" ")
        j=[]
        #Replace \n with "" and change the list accordingly exp:["","place","","p3"]
        for item in f[:]:
             l=item.replace("\n","")
             j.append(l)    
        f=j   

        #Find the place name in the list  
        ind=0
        #This boolean is required to escape the " init 1" in woflan models 
        found=False

        for x in range(len(f)):
            if f[x] == "place" :
                ind=x+1
        
        for x in range(ind,len(f)):
            if f[x]!="" and not found:
                ind=x
                found=True
                
        #Save place in dictionary
        plas["p"+str(i)]=f[ind]
        i+=1


    elif "trans " in element:
        #A list that contains a line with transition exp:["\n", "\n", "\n", "trans", "#t3", "in", "#p3_p3", "\n", "\n", "#p4_p4", "out", "#p5_p5"]
        f=element.split(" ")
        j=[]
        #Replace \n with "" and change the list accordingly exp:["", "", "", "trans", "#t3", "in", "#p3_p3", "", "", "#p4_p4", "out", "#p5_p5"]
        for item in f[:]:
            if item != "\n":
                l=item.replace("\n" , "" )
                if "," in l:
                 z=l.split(",")
                 for s in z:
                     j.append(s)
            
                else: j.append(l)
        f=j 
        

        find_t=0
        find_in=0
        find_out=0

        for x in range(len(f)):
            if f[x] == "trans":
                find_t=x+1
            elif f[x] == "in":
                find_in=x+1
            elif f[x] == "out":
                find_out=x+1
        
        for x in range(find_t,find_in-1):
            if f[x]!="":
                find_t=x

        trans["t"+str(ti)]=f[find_t]

        for x in range(find_in,find_out-1):
            if f[x]!="":
             input["in"+str(ni)]={ "from_p" : f[x] , "to_t" : trans["t"+str(ti)] }
             ni+=1

        for x in range(find_out,len(f)):
            if f[x]!="":
             output["out"+str(oi)]={ "to_p" : f[x] , "from_t" : trans["t"+str(ti)] } 
             oi+=1        

        ti+=1


 #----------Changing the data collected into the object oriented Petri net format-----------
 for key in plas:
     place=pt.Place()
     place.name=plas[key]
     place.id=key
     net.places[key]=place

 for key in trans:
     transition=pt.Transition()
     transition.name=trans[key]
     transition.id=key
     net.transitions[key]=transition

 for key in input:
     edge=pt.Edge()
     edge.id=key
     edge.name=key
     

     from_to=input[key]
     for elem in from_to:
         if elem=="from_p":
             edge.input=getId(plas, from_to[elem])
         else:
             edge.output=getId(trans, from_to[elem])

     net.edges.append(edge)
 
 for key in output:
     edge=pt.Edge()
     edge.id=key
     edge.name=key
     

     to_from=output[key]
     for elem in to_from:
         if elem=="to_p":
             edge.output=getId(plas, to_from[elem])
         else:
             edge.input=getId(trans, to_from[elem])
    
     net.edges.append(edge)
 return net

    
def parse_tpn_file(file):
 Line=[]
 with open(file, 'r') as file:
    Lines=file.read()
    Line=Lines.split(";")
 return parse_tpn(Line)