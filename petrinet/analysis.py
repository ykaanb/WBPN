#Check whether the net is a workflow net:
    # 1)there's a clear start:
        # the unique dedicated input place i s.t.
        # ∙i=∅
        # i.e. no transition can put a token to i
    # 2)there's a clear end:
        # the unique dedicated output place o s.t.
        # o∙=∅
        # i.e. no transitions should consume tokens from o
    # 3)every other transition and place are on the path from i to o 
        #the short-circuited P/T net (P, T ∪ {t}, F ∪ {(o, t), (t,i)}), denoted N, is strongly connected


def check_WFnet(net):
    #Check if there exists a clear Start and a clear End
    
    set_start_nodes(net)
    set_end_nodes(net)
    if net.start_nodes==[] or len(net.start_nodes)>1:
        net.clear_start=False
    if net.end_nodes==[] or len(net.end_nodes)>1:
        net.clear_end=False
    
    #Get all nodes
    nodes=[]
    for p in net.places:
        nodes.append(p)
    for t in net.transitions:
        nodes.append(t)
    
    #Get edges [ (sourcenodeid,targetnodeid) ]
    Edges=[]
    for e in net.edges:
        Edges.append((e.input,e.output))

    #If the net indeed has clear start and clear end then add a short-circuit
    if net.clear_end and net.clear_start:
        #Add short-circuit to the nodes
        nodes.append("short-circuit")
        #Add the short-circuit edges
        Edges.append((net.end_nodes[0],"short-circuit"))
        Edges.append(("short-circuit",net.start_nodes[0]))
        
        #Check whether the net is strongly connected
        net.isStronglyConnected=strongly_connected(nodes,Edges,net)

    #Set whether the net is a WFnet 
    if net.clear_start and net.clear_end and net.isStronglyConnected:
        net.WFnet=True

#Check if the net is strongly connected
def strongly_connected(nodes,edges,net):
    #Each node should be able to visit every node 
    for node in nodes:
        #Create for each node a connected dictionary to track which nodes they visit True for visited false for not visited
        connected={}.fromkeys(nodes,False)
        DFS(node,connected,edges)
        
        #Save the current node and to which nodes it can`t visit
        not_con_nodes=[] 
        for finalcheck in connected:
            if not connected[finalcheck]:
                not_con_nodes.append(finalcheck)
        if not_con_nodes:
            net.not_strongly_connected[node]=not_con_nodes

    if net.not_strongly_connected:
        return False   
    #For double checking with the reverse directions
    #If all the nodes are strongly connected reverse the direction and check again
    # else:
        
    #     r_edges=[]
    #     for source_target_tuple in edges:
    #         r_edges.append((source_target_tuple[1],source_target_tuple[0]))
    #     for node in nodes:
    #         connected2={}.fromkeys(nodes,False)
    #         DFS(node,connected2,r_edges)
    #         not_con_nodes=[]
    #         for finalcheck in connected2:
    #             if not connected2[finalcheck]:
    #                 not_con_nodes.append(finalcheck)
    #         if not_con_nodes:
    #             net.not_strongly_connected[node]=not_con_nodes
    
    #     if not net.not_strongly_connected:
    #           return True  
    #     else:
    #         return False 
    else: return True
        

#A help function which is a depth first search to find visited nodes
#This method changes visited dict such that all the reachable(visited) nodes have True as value 
def DFS(currentnode,connected,edges):
    #Current node tag visited,purpose: each visited dict contains the node itself as well  
    connected[currentnode]=True
    #Check for every edge with input as current node and go to the output if not visited already
    for source_target_tuple in edges:
        if source_target_tuple[0] == currentnode and not connected[ source_target_tuple[1] ]:
            DFS(source_target_tuple[1],connected,edges)

#Help function to set the start nodes, i.e. places with no inputs        
def set_start_nodes(net):
    
    for id in net.places:
        check_startplace=True
        for edge in net.edges:
            if net.places[id] == edge.get_target(net):
                check_startplace=False
        if check_startplace:
            net.start_nodes.append(id)

#Help function to set the start nodes, i.e. places with no outputs 
def set_end_nodes(net):

    for id in net.places:
        check_endplace=True
        for edge in net.edges:
            if net.places[id] == edge.get_source(net):
                check_endplace=False
        if check_endplace:
            net.end_nodes.append(id)

#Check whether the net is sound with the given initial marking:
    # i. ∀M ∈ B(P), [i] −→ M : ∃M1 ∈ B(P), M −→M1 : M1 ≥ [o] (option to complete)
    # ii. ∀M ∈ B(P), [i] −→ M : M ≥ [o] ⇒ M = [o](proper completion)
    # iii. no transition t ∈ T is dead in (N, [i]) (no deadtasks).
#Let W = (S, T, F, i, o) be a workflow net. 
    #For every k ≥ 1, let i k (o k ) denote the marking that puts k tokens on i (on o), and no tokens elsewhere. 
    #W is k-sound if o k is reachable from every marking reachable from i k 

def check_soundness(net,i_tokens):
    
    #Create the desired end_state marking with k tokens on the sink place 
    end_state=[]
    for key in net.places:
        if key==net.end_nodes[0]:
            end_state.append((key,i_tokens))
        else :
            end_state.append((key,0))

    #Find every marking M' >= end_state , save to the greateq_markings list 
    for m in net.markings:
        if great_eq_marking(m.marking,end_state):
            
            net.greateq_markings.append(m)
            net.geq_ids.append("m"+str(m.id))
    #Check option to complete
    net.otc=otc(net)

    #Check proper completion
    if len(net.greateq_markings)==1:
        check_pc=True
        placecounter=1
        for place, mark in net.greateq_markings[0].marking:
            if mark!=end_state[placecounter-1][1]:
                check_pc=False
            placecounter+=1
        net.pc=check_pc

   
    #Dead transitions are set in the check_dead_transitions function below
    #Set whether the net is sound 
    if net.otc and net.pc and not net.dead_t:
            net.sound=True

    
#Option to complete
def otc(net):
    #An OTC(option to complete) dictionary that holds every marking and whether they can reach a greater equal Marking
    # { marking object : True|False }
    markings_otc={}.fromkeys(net.markings,False)

    #Check markings_otc, set True if a marking can reach a greater equal Marking
    for greateq_m in net.greateq_markings:
        #I is the list of Markings that can reach the given greater equal Marking
        I=find_incoming_paths(net,greateq_m,[])
        #Include the greater or equal Marking itself 
        I.append(greateq_m)
        for marking in markings_otc:
            if marking in I:
                markings_otc[marking]=True

    #Append the markings id's, that has no option to complete, to the no_otc list in net
    for m in markings_otc:
        if not markings_otc[m]:
            net.no_otc.append("m"+str(m.id))
    #If the no option to complete list is empty then return True
        #=>all the markings can reach a greater equal Marking 
    #Else return False
    if not net.no_otc:
        return True
    else:
        return False




#Help method to decide whether a Marking is greater equal than another marking        
def great_eq_marking(list1,list2):
    placecounter=1
    for place,mark in list1:
        if list2[placecounter-1][1]>mark:
            return False
        else :
            placecounter+=1
    return True






# Let S = (N, M0) be a system

#BOUNDEDNESS
# S is bounded if an integer k exists such that: ∀M ∈ [M0i, for each place p, M(p) ≤ k . N is
# structurally bounded if (N, M) is bounded for each M.

#Boundness: maximum number of tokens that a place holds of the whole markings list


def set_boundness(net):
    for e in net.markings:
        for (k,v) in e.marking:
            if net.boundness!=-1 :
                if v==-1:
                    net.boundness=-1

                else:
                 if net.boundness<v:
                        net.boundness=v 



#DEADLOCK
# A transition t is dead in S if no marking of [M0i enables t. A deadlock, or dead marking, is
# a marking enabling no transition. S is deadlock-free if no deadlock belongs to [M0i; otherwise
# it is deadlockable. 

#Deadlockfree: every reachable marking should enable some t€T 
#For a sound net the end state is the only deadlock
#return the dead markings
def set_deadlocks(net):
    
    for e in net.markings:
        if  e.r_t_list==[]:
                 
                net.deadlocks.append("m"+str(e.id))
    
    
    

#LIVENESS


# A transition t is L4-live in S if for every marking M in [M0i, there is a marking M'
# in [Mi enabling t. 
# S is live if every transition is live in S.

# A Petri net (PN ; M0) is (L4-)live iff for every reachable state M'
# and every transition t, there is a state M'' reachable from M'
# which enables t
# !! The net is live if all transitions are L4 live

#L4 liveness
def check_L4_live(net):
    #A boolean List that contains every transitions liveness
    P=[]
    
    for key in net.transitions:

        
        #A list that contains the markings in which this transition is enabled
        M=[]
        #A list that contains the markings that are on the path to the markings of M 
        #(This means that only these markings in the list can reach the markings in M)
        #Every marking that can reach the markings in M 
        L=[]

        #Find in which markings this transition is enabled
        for k in net.markings:
             if net.transitions[key] in k.r_t_list:
                 M.append(k)
        #Find which markings can reach the markings in M
        for o in M:
           find_incoming_paths(net,o,L)
        
        #Check the transition`s liveness:(M+L needs to be equal to all markings)
        l=True 
        # M+L
        for k in M:
            if not(k in L):
                L.append(k)

        for v in net.markings:
            if not(v in L):
                l=False
        #Append L4_live transitions to the corresponding list in the net
        if l:
            net.L4_live.append(key)

        P.append(l)
    
    #If all transitions are L4 Live 
    if not (False in P):
        net.live="Strong Live"
    #Else if at least 1 transition is L4 Live
    elif True in P:
        net.live="Weak Live"


#Check L0 live transitions
def check_dead_transitions(net):
     #Check dead transitions

    # A dead transitions dictionary that holds every transition and whether they are dead 
        # { transition object : True|False }
    not_dead_transitions={}.fromkeys(net.transitions,False)
    
    #Set non dead transitions True
    for marking in net.markings:
        for ready_t in marking.r_t_list:
            if not not_dead_transitions[ready_t.id]:
                not_dead_transitions[ready_t.id]=True
    
    #Save dead Transitions ids
    for transition in not_dead_transitions:
        if not not_dead_transitions[transition]:
            net.dead_t.append(transition)

    #Set whether there exists dead transitions 
    if net.dead_t:
        net.d_transitions=True

#Check L3 Live transitions
def check_L3_live(net):
    
    #Check L3 live if t is not dead and not L4 Live
    for t in net.transitions:
     if not (t in net.L4_live) and not (t in net.dead_t):
        #A list that contains the markings in which this transition is enabled
        M=[]
        #A list that contains the markings that can reach a given Marking M
        L=[]
        #Find in which markings this transition is enabled
        for k in net.markings:
             if net.transitions[t] in k.r_t_list:
                 M.append(k)
        
        #1)Find which markings can reach a Marking in M, in which t is enabled, 
        #2)If the t enabled Marking can reach itself AFTER FIRING t !!!!!, then the transition t is L3-Live  
        for o in M:
            find_incoming_paths(net,o,L)
            #Find the resulting Marking M2 after firing t and check whether M2 is on some path to M : M -(t)-> M2 -...-> M
            M2=o.t_paths[t]
           
            if M2 in L:
                net.L3_live.append(t)
                #Save an example marking from which the transition can fire infinitely 
                net.L3_live_wm.append((t,"m"+str(o.id)))
                break
            #Empty L for the next o 
            L=[]

#Check L2_L1 Live transitions
def check_L2_L1_live(net):
    #L2 and L1 live if t is not dead and not L4 Live and not L3 Live
    for t in net.transitions:
        if not (t in net.L4_live) and not (t in net.dead_t) and not (t in net.L3_live):
    
    
    #After firing t M-(t)-> M2 check t-paths, if t is enabled in any reachable marking from M2, t is L2-live; if not L1-live 
            #A list that contains the markings in which this transition is enabled
            M=[]
            #Find in which markings this transition is enabled
            for k in net.markings:
                if net.transitions[t] in k.r_t_list:
                    M.append(k)

            for marking in M:
                #boolean to decide L2 or L1
                L2=False
                #Reachable markings list from M2
                reachable=[]
                #Find the resulting marking object (M2) after firing t
                M2=marking.t_paths[t]
                
                #Find the first reachable Markings from M2, this is required to iterate the search
                for next in M2.t_paths:
                    reachable.append(M2.t_paths[next])

                #Find all the reachable Markings from M2
                for M2_next in reachable:
                    for next_t in M2_next.t_paths:
                         if not (M2_next.t_paths[next_t] in reachable):
                             reachable.append(M2_next.t_paths[next_t])
                
                #Check if in any of the reachable markings t is enabled, if yes L2-live
                for M2_next in reachable:
                    if net.transitions[t] in M2_next.r_t_list:
                        L2=True
                        net.L2_live.append(t)
                        net.L2_live_wm.append((t,"m"+str(marking.id)+"-("+t+")->...->"+"m"+str(M2_next.id)+"-("+t+")->..."))
                        break
                #If even 1 sequence is found and t is already in L2 
                if t in net.L2_live:
                    break
            
            #If not L2 then L1
            if not L2:
                net.L1_live.append(t)
                net.L1_live_wm.append((t,"m"+str(M[0].id)))
            
            

        
        



#A help method to find the which markings can reach a given marking 
#returns markings list

#This method basically collects the incoming markings of incoming markings and so on.. 
# exp:m5<-m2,m3 (I=[m2]) , m2<-m1 (I=[m2,m1]), m1<-m0 (I=[m2,m1,m0]),
# m0<-None (I=[m2,m1,m0]), (I=[m2,m1,m0,m3]), m3<-m4 (I=[m2,m1,m0,m3,m4])
# m4<-m3 (I=[m2,m1,m0,m3,m4])

def find_incoming_paths(net,marking,I):
    
    for k in marking.incoming:
       for i in net.markings:
        #Find and save the incoming marking and recurse it 
        # TO AVOID LOOPS AND DUPLICATES: SAVE AND RECURSE ONLY IF IT IS NOT ALREADY in the I list
        if i.id==k and (not(i in I)):
         I.append(i)
         find_incoming_paths(net,i,I)
    
    return I 


