from petrinet import petrinet as pt
def convert(bpmnelemlist, seqflow):
    net=pt.PetriNet()
    place_counter=1
    transition_counter=1
    edge_counter=1
     #create places for seqflows except for eventbasedGW
    for seq in seqflow:
        #find source of seq 
        # for elem in bpmnelemlist:
        #      if elem.id == seq.sourceRef:
        #          source=elem
        # if source.type != "evntbGW":
            p=pt.Place()
            p.id=seq.id
            if seq.name=="":
                p.name="seq_flow:..." + seq.id[-11:] 
            else:p.name=seq.name
            net.places[p.id]=p
            place_counter+=1

    for element in bpmnelemlist:
          match element.type:
                case "s":
                    # create start place (if multiple targets and_split, bind silent t to outgoings)
                    place = pt.Place()
                    place.id = "p" + str(place_counter)
                    place.name = element.name
                    net.places[place.id] = place
                    place_counter+=1
                    # create silent transition for that place
                    transition = pt.Transition()
                    transition.id = "t" + str(transition_counter)
                    transition.name = "silent transition"
                    net.transitions[transition.id] = transition
                    transition_counter+=1

                    #create the edge between the start place and the silent transition
                    edge = pt.Edge()
                    edge.id = edge_counter
                    edge.name = place.id + "-to-" + transition.id
                    edge.input = place.id
                    edge.output = transition.id
                    
                    net.edges.append(edge)
                    edge_counter+=1

                    #create the edge to the seqflows 
                    for target in element.outgoing:
                        edge=pt.Edge()
                        edge.id=edge_counter
                        edge.name= transition.id + "-to-" + target
                        edge.input= transition.id
                        edge.output= target  
                        
                        net.edges.append(edge)
                        edge_counter+=1
                case "e":
                    # create end place (if multiple sources xor_join, bind incomings to silent t )
                    endplace = pt.Place()
                    endplace.id = "p" + str(place_counter)
                    endplace.name = element.name
                    net.places[endplace.id] = endplace
                    place_counter+=1
                    # create end transition 
                    endtransition = pt.Transition()
                    endtransition.id = "t" + str(transition_counter)
                    endtransition.name = "silent transition"
                    net.transitions[endtransition.id] = endtransition
                    transition_counter+=1
                    #xor_join behaviour , create for each incoming a silent transition then create a single silent place and bind them 
                    silent_t=[]
                    for source in element.incoming:
                        #create silent transitions for incomings 
                        silt = pt.Transition()
                        silt.id = "t" + str(transition_counter)
                        silt.name = "silent transition"
                        net.transitions[silt.id] = silt
                        silent_t.append(silt)
                        transition_counter+=1
                        #bind incomings to the respective silent t
                        
                        edge=pt.Edge()
                        edge.id=edge_counter
                        edge.name= source + "-to-" + silt.id
                        edge.input= source
                        edge.output= silt.id  
                        
                        net.edges.append(edge)
                        edge_counter+=1

                    #create a silent place to connect silent transitions to 
                    place=pt.Place()
                    place.id="p"+ str(place_counter)
                    place.name="silent place" 
                    net.places[place.id]=place
                    place_counter+=1

                    #bind the silent transitions to the above silent place
                    for s_t in silent_t:
                        edge=pt.Edge()
                        edge.id=edge_counter
                        edge.name= s_t.id + "-to-" + place.id
                        edge.input= s_t.id
                        edge.output= place.id  
                        
                        net.edges.append(edge)
                        edge_counter+=1
                    #bind the silent place to the end transition
                    edge=pt.Edge()
                    edge.id=edge_counter
                    edge.name=place.id + "-to-" + endtransition.id
                    edge.input=place.id
                    edge.output=endtransition.id
                    
                    net.edges.append(edge)
                    edge_counter+=1
                    #bind the endtransition to the endplace
                    edge=pt.Edge()
                    edge.id=edge_counter
                    edge.name= endtransition.id + "-to-" + endplace.id
                    edge.input=endtransition.id
                    edge.output=endplace.id
                    
                    net.edges.append(edge)
                    edge_counter+=1

                #intermediate events and tasks
                case ("interCatch"|"interThrow"|"t"|"sendT"|"receiveT"|"userT"|
                     "manualT"|"serviceT"|"scriptT"):
                    # create transition 
                    transition = pt.Transition()
                    transition.id = "t" + str(transition_counter)
                    transition.name = element.name
                    net.transitions[transition.id] = transition
                    transition_counter+=1
                    #create edges to seq flows (if multiple incoming or outgoing xor_join, and_split behaviour)
                    #xor_join behaviour , create for each incoming a silent transition then create a single silent place and bind them 
                    silent_t=[]
                    for source in element.incoming:
                        #create silent transitions for incomings 
                        silt = pt.Transition()
                        silt.id = "t" + str(transition_counter)
                        silt.name = "silent transition"
                        net.transitions[silt.id] = silt
                        silent_t.append(silt)
                        transition_counter+=1
                        #bind incomings to the respective silent t
                        
                        edge=pt.Edge()
                        edge.id=edge_counter
                        edge.name= source + "-to-" + silt.id
                        edge.input= source
                        edge.output= silt.id  
                        
                        net.edges.append(edge)
                        edge_counter+=1

                    #create a silent place to connect silent transitions to 
                    place=pt.Place()
                    place.id="p"+ str(place_counter)
                    place.name="silent place" 
                    net.places[place.id]=place
                    place_counter+=1

                    #bind the silent transitions to the above silent place
                    for s_t in silent_t:
                        edge=pt.Edge()
                        edge.id=edge_counter
                        edge.name= s_t.id + "-to-" + place.id
                        edge.input= s_t.id
                        edge.output= place.id  
                        
                        net.edges.append(edge)
                        edge_counter+=1

                    #bind the silent place to the actual activity,event transition
                    edge=pt.Edge()
                    edge.id=edge_counter
                    edge.name=place.id + "-to-" + transition.id
                    edge.input=place.id
                    edge.output=transition.id
                    
                    net.edges.append(edge)
                    edge_counter+=1

                    #and_split behaviour, bind the transition to all the outgoing flows
                    for target in element.outgoing:
                        edge=pt.Edge()
                        edge.id=edge_counter
                        edge.name= transition.id + "-to-" + target
                        edge.input= transition.id
                        edge.output= target  
                        
                        net.edges.append(edge)
                        edge_counter+=1
                #parallel gateways
                case "parGW":
                        #If multiple incomings and outgoings then create and_join + and_split
                        if len(element.incoming)>=1 and len(element.outgoing) >=1:
                            #t1 for and_join, t2 for and_split, p for inbetween
                            t1=pt.Transition()
                            t1.id = "t" + str(transition_counter)
                            t1.name = "silent transition"
                            net.transitions[t1.id] = t1
                            transition_counter+=1

                            t2=pt.Transition()
                            t2.id = "t" + str(transition_counter)
                            t2.name = "silent transition"
                            net.transitions[t2.id] = t2
                            transition_counter+=1

                            p=pt.Place()
                            p.id="p"+ str(place_counter)
                            p.name="silent place"
                            net.places[p.id]=p
                            place_counter+=1
                            #and_join
                            for source in element.incoming:
                                edge=pt.Edge()
                                edge.id=edge_counter
                                edge.name= source + "-to-" + t1.id
                                edge.input= source
                                edge.output= t1.id  
                                
                                net.edges.append(edge)
                                edge_counter+=1
                            #bind t1 to p
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= t1.id + "-to-" + p.id
                            edge.input= t1.id
                            edge.output= p.id  
                            
                            net.edges.append(edge)
                            edge_counter+=1
                            #bind p to t2 
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= p.id + "-to-" + t2.id
                            edge.input= p.id
                            edge.output= t2.id  
                            
                            net.edges.append(edge)
                            edge_counter+=1
                            #and_split t2 to all outgoing
                            for target in element.outgoing:
                                edge=pt.Edge()
                                edge.id=edge_counter
                                edge.name= t2.id + "-to-" + target
                                edge.input= t2.id
                                edge.output= target
                                
                                net.edges.append(edge)
                                edge_counter+=1
                        
                        else: 
                            #for multiple incoming(converging) OR (diverging)multiple outgoing 
                            t=pt.Transition()
                            t.id = "t" + str(transition_counter)
                            t.name = "silent transition"
                            net.transitions[t.id] = t
                            transition_counter+=1
                            for source in element.incoming:
                                edge=pt.Edge()
                                edge.id=edge_counter
                                edge.name= source + "-to-" + t.id
                                edge.input= source
                                edge.output= t.id
                                
                                net.edges.append(edge)
                                edge_counter+=1  
                            for target in element.outgoing:
                                edge=pt.Edge()
                                edge.id=edge_counter
                                edge.name=t.id + "-to-" + target
                                edge.input= t.id
                                edge.output= target  
                                
                                net.edges.append(edge)
                                edge_counter+=1  
                #exclusive gateways
                case "exGW":
                    #If multiple incomings and outgoings then create xor_join + xor_split
                    
                    if len(element.incoming)>1 and len(element.outgoing)>1:
                        silent_t=[]
                        #xor_join
                        #create a silent place to connect xor_join and xor_split
                        place=pt.Place()
                        place.id="p"+ str(place_counter)
                        place.name="silent place xor" 
                        net.places[place.id]=place
                        place_counter+=1

                        for source in element.incoming:
                            #create silent transitions for incomings 
                            silt = pt.Transition()
                            silt.id = "t" + str(transition_counter)
                            silt.name = "silent transition xor in"
                            net.transitions[silt.id] = silt
                            silent_t.append(silt)
                            transition_counter+=1

                            #bind incomings to the respective silent t
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= source + "-to-" + silt.id
                            edge.input= source
                            edge.output= silt.id  
                            
                            net.edges.append(edge)
                            edge_counter+=1

                        

                        #bind the silent transitions to the above silent place
                        for s_t in silent_t:
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= s_t.id + "-to-" + place.id
                            edge.input= s_t.id
                            edge.output= place.id  
                            
                            net.edges.append(edge)
                            edge_counter+=1
                        
                        #xor_split
                        for target in element.outgoing:
                            #create silent transitions for outgoings
                            t = pt.Transition()
                            t.id = "t" + str(transition_counter)
                            t.name = "silent transition xor out"
                            net.transitions[t.id] = t
                            
                            transition_counter+=1

                            #bind transitions to the respective places(targets)
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= t.id + "-to-" + target
                            edge.input= t.id
                            edge.output= target 
                            
                            net.edges.append(edge)
                            edge_counter+=1

                            #bind the silent place to the silent transitions
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= place.id + "-to-" + t.id
                            edge.input= place.id
                            edge.output= t.id  
                            
                            net.edges.append(edge)
                            edge_counter+=1
                    elif len(element.incoming)>1 and len(element.outgoing) ==1:
                        #xor_join
                        
                        
                        for source in element.incoming:
                            #create silent transitions for incomings 
                            silt = pt.Transition()
                            silt.id = "t" + str(transition_counter)
                            silt.name = "silent transition"
                            net.transitions[silt.id] = silt
                            
                            transition_counter+=1

                            #bind incomings to the respective silent t
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= source + "-to-" + silt.id
                            edge.input= source
                            edge.output= silt.id  
                            
                            net.edges.append(edge)
                            edge_counter+=1

                            #bind the silent transitions to the outgoing place
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= silt.id + "-to-" + element.outgoing[0]
                            edge.input= silt.id
                            edge.output= element.outgoing[0]  
                            
                            net.edges.append(edge)
                            edge_counter+=1

                    elif len(element.incoming)==1 and len(element.outgoing) >1:
                        #xor_split
                        for target in element.outgoing:
                            #create silent transitions for outgoings
                            silt = pt.Transition()
                            silt.id = "t" + str(transition_counter)
                            silt.name = "silent transition"
                            net.transitions[silt.id] = silt
                            
                            transition_counter+=1

                            #bind silent transitions to the respective outgoing places
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= silt.id + "-to-" + target
                            edge.input= silt.id  
                            edge.output= target
                            
                            net.edges.append(edge)
                            edge_counter+=1

                           #bind the incoming to the silent transitions
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= element.incoming[0] + "-to-" + silt.id
                            edge.input= element.incoming[0]
                            edge.output= silt.id 
                            
                            net.edges.append(edge)
                            edge_counter+=1
                    else:
                        #create silent transition  
                            t = pt.Transition()
                            t.id = "t" + str(transition_counter)
                            t.name = "silent transition"
                            net.transitions[t.id] = t
                            
                            transition_counter+=1
                            for source in element.incoming:
                                #bind the incoming to the silent transition 
                                edge=pt.Edge()
                                edge.id=edge_counter
                                edge.name= source + "-to-" + t.id
                                edge.input= source
                                edge.output= t.id 
                                
                                net.edges.append(edge)
                                edge_counter+=1

                            for target in element.outgoing:
                                #bind the transition to the outgoing
                                edge=pt.Edge()
                                edge.id=edge_counter
                                edge.name= t.id + "-to-" + target
                                edge.input= t.id
                                edge.output= target
                                
                                net.edges.append(edge)
                                edge_counter+=1
                #eventbased gateways
                case "evntbGW":
                    #Very similar to XOR bind the incomings to outgoings, 1 place evntbGW for race condition
                    #If multiple incoming xor behaviour 
                    silent_t=[]
                    for source in element.incoming:
                        #create silent transitions for incomings 
                        silt = pt.Transition()
                        silt.id = "t" + str(transition_counter)
                        silt.name = "silent transition"
                        net.transitions[silt.id] = silt
                        silent_t.append(silt)
                        transition_counter+=1
                        #bind incomings to the respective silent t
                        
                        edge=pt.Edge()
                        edge.id=edge_counter
                        edge.name= source + "-to-" + silt.id
                        edge.input= source
                        edge.output= silt.id  
                        
                        net.edges.append(edge)
                        edge_counter+=1

                    #create a silent place to connect silent transitions to 
                    place=pt.Place()
                    place.id="p"+ str(place_counter)
                    place.name="silent place evntbGW" 
                    net.places[place.id]=place
                    place_counter+=1

                    #bind the silent transitions to the above silent place
                    for s_t in silent_t:
                        edge=pt.Edge()
                        edge.id=edge_counter
                        edge.name= s_t.id + "-to-" + place.id
                        edge.input= s_t.id
                        edge.output= place.id  
                        
                        net.edges.append(edge)
                        edge_counter+=1
                    
                    #bind the silent place to the outgoing sequence flows, since seq flows are places we need silent transition for each one
                    for target in element.outgoing:
                            #create silent transitions for outgoings
                            t = pt.Transition()
                            t.id = "t" + str(transition_counter)
                            t.name = "silent transition evnt out"
                            net.transitions[t.id] = t
                            
                            transition_counter+=1

                            #bind transitions to the respective places(targets)
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= t.id + "-to-" + target
                            edge.input= t.id
                            edge.output= target 
                            
                            net.edges.append(edge)
                            edge_counter+=1

                            #bind the silent place to the silent transitions
                            edge=pt.Edge()
                            edge.id=edge_counter
                            edge.name= place.id + "-to-" + t.id
                            edge.input= place.id
                            edge.output= t.id  
                            
                            net.edges.append(edge)
                            edge_counter+=1
    
    #Change place sequenceflow ids to regular place id`s 
    pi=1
    right_ids_places={}
    changed_elem={}#{edgeobject: [False,False] } 
    for e in net.edges:
        changed_elem[e]=[False,False] 

    for elem in net.places:

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
    return net  

                 



