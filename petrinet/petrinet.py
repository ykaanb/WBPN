
class PetriNet:
 
 def __init__(self) :
     
     self.edges=[]
     self.transitions = {} # Map of transitions. Key: transition id, Value: transition object
     self.places = {} # Map of places. Key: place id, Value: place object
     self.markings=[] # List of Marking objects
     self.markingcount=0

     self.boundness=0
     self.unbounded_places=[] # id's of unbounded places
    #  self.dlockf=True
     self.deadlocks=[] # id's of dead markings
     
     self.clear_start=True
     self.clear_end=True
     self.start_nodes=[] # ids
     self.end_nodes=[] # ids
     self.isStronglyConnected=False
     self.WFnet=False
     self.not_strongly_connected={} # A Map of nodes that are not strongly connected { nodeid : [nodeid,nodeid,nodeid...] }
     
     self.otc=False # Option to complete
     self.greateq_markings=[] # A list of markings objects that are greater equal than the desired endstate 
     self.geq_ids=[] #A list of markings ids that are greater equal than the desired endstate
     self.no_otc=[] # A list of string markings ids' that have no option to complete
     self.pc=False # Proper completion
     self.d_transitions=False # Dead transitions
     self.sound=False

     self.dead_t=[] # id's of dead transitions L0 live 
     self.live="Not live" # whether the net is live
     self.L4_live=[] # id's of L4 live transitions
     self.L3_live=[] # id's of L3 live transitions [(transition id, Marking String), ...]
     self.L3_live_wm=[] # id's of L3 live transitions with an example corresponding marking that can reach itself[(transition id, Marking String), ...]
     self.L2_live=[] # id's of L2 live transitions
     self.L2_live_wm=[] # id's of L2 live transitions with an example corresponding Markings [(transition id, "Marking id ->...-> Marking id"), ...]
     self.L1_live=[] # id's of L1 live transitions
     self.L1_live_wm=[] # id's of L1 live transitions with an example of a corresponding Marking [(transition id, Markings String), ...] 


 #A method to get a single Marking list of (placeid, marking) tuples , meaning the current Tokens of all places

 def get_pmarkings(self):
     pmlist = []
     for key in self.places:
         pmlist.append((key, self.places[key].marking))
     return pmlist

 #A method to return to a marking state without losing the markings list and count
 def set_pmarkings(self, pmlist):
     for placeid, marking in pmlist:
         self.places[placeid].marking = marking

  #!!!!! With W NOTATION as -1!!!!
 #A method to fire a single Transition
 #if k.get_source().marking!="w" then no change in marking
 #if k.get_target().marking!="w" then no change in marking
 def fire_t(self,trans_obj):
     for k in self.edges:
         if trans_obj == k.get_target(self):
            if k.get_source(self).marking!=-1:
             k.get_source(self).marking-=1
         elif trans_obj == k.get_source(self):
            if k.get_target(self).marking!=-1:
             k.get_target(self).marking+=1

  #A method to make transitions` ready= True or False
 def regulate_transitions_readiness(self):

     for key in self.transitions:
        #this temp is a temporary list for each transition`s input places
        temp=[]

        #find input places for each transition
        for e in self.edges:
            if self.transitions[key] == e.get_target(self):
                temp.append(e.get_source(self))
        
        #Check if transition has input places 
        if temp!=[]:
            rfire=True
            #check if all the input places have more than 0 token
            for k in temp:
                if k.marking==0:
                    rfire=False
            
            self.transitions[key].ready=rfire

 #A method to return ready Transitions
 def get_ready_transitions(self):
     temp = []
     for key in self.transitions:
         if self.transitions[key].ready == True:
             temp.append(self.transitions[key])
     return temp

 
 def set_cover(self):
    
    
    for m in self.markings:
     

        #Iterate through the ready transitions list for the given marking state 
        for k in m.r_t_list : 
        
            #Return to the starting state after the iteration so that before the next transition fires, the state is correct
            self.set_pmarkings(m.marking) 
            self.regulate_transitions_readiness()

            self.fire_t(k)
            
            self.regulate_transitions_readiness()

            n=Marking() 
            n.id=self.markingcount+1
            n.marking=self.get_pmarkings()
            n.incoming[m.id]=k
            
            I=find_inc(self,n,[])
            for prev_marking in I:
            #  if prev_marking.id!=0:
                    greater_place_list=[]
                    greater_check=True
                    prev_mark_list=prev_marking.marking
                    n_mark_list=n.marking
                    place_id_counter=1
                    for place,mark in n_mark_list:
                        if mark!=-1 and prev_mark_list[place_id_counter-1][1]>mark:
                            greater_check=False
                        elif mark==-1 or mark>prev_mark_list[place_id_counter-1][1]:
                            greater_place_list.append(place_id_counter)
                        place_id_counter+=1
                    if greater_check:
                        for index in greater_place_list:
                            self.places["p"+str(index)].marking=-1
                            if not("p"+str(index)) in self.unbounded_places:
                                self.unbounded_places.append("p"+str(index))
                        n.marking=self.get_pmarkings()

            #Check whether newMarking m' after the greater_check -> if greater_check=True then changes occur on m' thats why we need to check newMarking after the changes
            newMarking=True
            for o in self.markings:
                if n.marking == o.marking:
                    newMarking=False
                    existingMarking=o
            #Create new Marking and add to the markings list
            if newMarking:
                    m.t_paths[k.id]=n
                    m.t_pathstring+=k.id + "->m" + str(n.id) + " " 
                    n.r_t_list=self.get_ready_transitions()
                    self.markings.append(n)
                    self.markingcount+=1
                    
            #If Marking already exists, save the marking id and the transition to the already existing marking as incoming, also save the transition path to the current marking 
            else:
                for o in self.markings:
                    if existingMarking==o:
                        o.incoming[m.id]= k 
                        m.t_paths[k.id]=o 
                        m.t_pathstring+=k.id + "->m" + str(o.id) + " "
                
           
            

#Help method to find the Markings on the path from M0 to some marking M         
def find_inc(net,marking,I):
    
    for k in marking.incoming:
       for i in net.markings:
        #Find and save the incoming marking and recurse it 
        # TO AVOID LOOPS AND DUPLICATES: SAVE AND RECURSE ONLY IF IT IS NOT ALREADY in the I list
        if i.id==k and (not(i in I)):
         I.append(i)
         find_inc(net,i,I)
    
    return I 


class Marking:

    def __init__(self):
        self.id=0
        self.marking=[] # A list of Marking list of (placeid, marking) tuples , meaning the current Tokens of all places
        self.incoming={} # A Map for already fired Transitions pointing to this marking and from which Marking they are firing : { Marking id(int) : transition Object}
        self.r_t_list=[] # A list for ready Transitions 
        self.t_paths={}  # A map to track which transition leads to which marking : { Transition id(string) : marking object } 
        self.t_pathstring="" #A string to track which transition leads to which marking


    # def __init__(self, marking=[], incoming={}, r_t_list=[], t_paths={}, id: int = 0, t_pathstring: str = ""):
    #     self.marking = marking # A list of Marking list of (placeid, marking) tuples , meaning the current Tokens of all places
    #     self.incoming = incoming # A Map for already fired Transitions pointing to this marking and from which Marking they are firing : { Marking id(int) : transition Object}
    #     self.r_t_list = r_t_list # A list for ready Transitions
    #     self.t_paths = t_paths # A map to track which transition leads to which marking : { Transition id(string) : marking object }
    #     self.id = id 
    #     self.t_pathstring = t_pathstring #A string to track which transition leads to which marking
        

class Transition:

    def __init__(self):
        # self.isPlace=False
        self.ready=False
        self.id=""
        self.name=""
    
    
    
    # def __init__(self, isPlace: bool = False, ready: bool = False, id: str = "", name: str = ""):
    #     self.isPlace = isPlace
    #     self.ready = ready
    #     self.id = id
    #     self.name = name
        


class Place:

    def __init__(self):
        # self.isPlace=True
        
        self.id=""
        self.name=""
        self.marking=0


#    def __init__(self, isPlace: bool = True, id: str = "", name: str = "", marking: int = 0):
#        self.isPlace = isPlace
#        self.id = id
#        self.name = name
#        self.marking = marking


class Edge:
    
    def __init__(self):
        self.id=""
        self.name=""
        self.input="" #id 
        self.output="" #id
        
    
    
    # def __init__(self, id: str = "", name: str = "", input: str= "", output: str= "", net=None):
    #     self.id = id
    #     self.name = name
    #     self.input = input  # id
    #     self.output = output  # id
    #     self.net = net

    #Get the source node of a transition or a place
    def get_source(self,net):
        if self.input in net.transitions:
            return net.transitions[self.input]
        else:
            return net.places[self.input]
    #Get the target node of a transition or a place
    def get_target(self,net):
        if self.output in net.transitions:
            return net.transitions[self.output]
        else:
            return net.places[self.output]
