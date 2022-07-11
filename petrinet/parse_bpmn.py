import xml.dom.minidom as minidom


from petrinet import petrinet as pt 
from petrinet import convertpt
def parse_bpmn_string(input):

     #minidom.parseString()
     parsed=minidom.parseString(input)
     
     #Get processes
     processeslist=parsed.getElementsByTagName("process")
    
     
     #Get bpmn elements flow elements
     #bpmnelements list
     bpmnelements=[]
     sequenceflows=[]
     process=processeslist[0]

     startEventlist = process.getElementsByTagName("startEvent")
     intermediateCatchEventlist = process.getElementsByTagName("intermediateCatchEvent")
     intermediateThrowEventlist = process.getElementsByTagName("intermediateThrowEvent")
     endEventlist = process.getElementsByTagName("endEvent")

     tasklist = process.getElementsByTagName("task")
     sendTasklist = process.getElementsByTagName("sendTask")
     receiveTasklist = process.getElementsByTagName("receiveTask")
     userTasklist = process.getElementsByTagName("userTask")
     manualTasklist = process.getElementsByTagName("manualTask")
     serviceTasklist = process.getElementsByTagName("serviceTask")
     scriptTasklist = process.getElementsByTagName("scriptTask")
     

     exclusiveGatewaylist = process.getElementsByTagName("exclusiveGateway")
     parallelGatewaylist = process.getElementsByTagName("parallelGateway")
     inclusiveGatewaylist = process.getElementsByTagName("inclusiveGateway")
     eventBasedGatewaylist = process.getElementsByTagName("eventBasedGateway")

     sequenceflowlist = process.getElementsByTagName("sequenceFlow")

     #creating the bpmnelements, sequenceflows and saving them in a list bpmnelements and sequenceflows

     #Events---------------
     create_bpmnelements_list(startEventlist,bpmnelements,"s")
     
     create_bpmnelements_list(intermediateCatchEventlist,bpmnelements,"interCatch")
     
     create_bpmnelements_list(intermediateThrowEventlist,bpmnelements,"interThrow")
     
     create_bpmnelements_list(endEventlist,bpmnelements,"e")
     
     #Events-----------------

     #Tasks------------------
     create_bpmnelements_list(tasklist,bpmnelements,"t")
     
     create_bpmnelements_list(sendTasklist,bpmnelements,"sendT")
     
     create_bpmnelements_list(receiveTasklist,bpmnelements,"receiveT")
     
     create_bpmnelements_list(userTasklist,bpmnelements,"userT")
     
     create_bpmnelements_list(manualTasklist,bpmnelements,"manualT")
     
     create_bpmnelements_list(serviceTasklist,bpmnelements,"serviceT")
     
     create_bpmnelements_list(scriptTasklist,bpmnelements,"scriptT")
     
     #Tasks--------------------------
     
     #Gateways-----------------------
     create_bpmnelements_list(exclusiveGatewaylist,bpmnelements,"exGW")
     
     create_bpmnelements_list(parallelGatewaylist,bpmnelements,"parGW")
     
     create_bpmnelements_list(inclusiveGatewaylist,bpmnelements,"inclGW")
          
     create_bpmnelements_list(eventBasedGatewaylist,bpmnelements,"evntbGW")
                    
     #Gateways---------------------------

     #Sequenceflows----------------------
     for seqf in sequenceflowlist:
          sf = sequenceflow()
          sf.id = seqf.getAttribute("id")
          sf.name = seqf.getAttribute("name")
          sf.sourceRef = seqf.getAttribute("sourceRef")
          sf.targetRef = seqf.getAttribute("targetRef")
          sequenceflows.append(sf)
     #Sequenceflows-----------------------


     #Convert BPMN elements into petri net !!! This works for controlled flow bpmns example start events have indgree of 0 and outdgree 1

     
     #FOR CONSOLE---------------------
     # elemcounter=1
     # for elem in bpmnelements:
     #      print("Element"+ str(elemcounter))
     #      print("type->" + elem.type)
     #      print("id->" + elem.id)
     #      print("name->" + elem.name)
     #      print("incoming:")
     #      print(elem.incoming)
     #      print("outgoing:")
     #      print(elem.outgoing)
     #      print("--------------")
     #      elemcounter+=1
     # elemcounter=1
     # for elem in sequenceflows:
     #      print("SeqFlow"+ str(elemcounter))
     #      print("id->" + elem.id)
     #      print("sourceRef:" + elem.sourceRef)
     #      print("targetRef:" + elem.targetRef)
     #      print("--------------")
     #      elemcounter+=1

     return convertpt.convert(bpmnelements,sequenceflows)

def create_bpmnelements_list(list, bpmnlist, type):
     for element in list:
          bpmnelem=bpmnelement(element,type)
          bpmnlist.append(bpmnelem)

def create_or_find_seqplace(seqid,place_counter,net):
     seqid_exists=False
     p=pt.Place()
     for place in net.places:
          if (("sequence_flow:" + seqid) == net.places[place].name):
               seqid_exists=True
               p=place
     if not seqid_exists:
          p.id = "p" + str(place_counter)
          p.name = "sequence_flow:" + seqid

     




class bpmnelement:
     
     def __init__(self,Domelement,type):
          #element type: 
          # "s" for startevent, "e" for endevent, "t" for task, "svt" for serviceTask, "sct" for scriptTask
          # "exGW" for exclusiveGateway, "parGW" for parallelGateway
          self.type=type 
          self.id=Domelement.getAttribute("id")
          self.name="("+ type + ") -" + Domelement.getAttribute("name")
          self.incoming=[]#list of incoming sequenceflow strings
          self.outgoing=[]#list of outgoing sequenceflow strings

          incominglist=Domelement.getElementsByTagName("incoming")
          for incoming in incominglist:
                    self.incoming.append(incoming.firstChild.data)
          outgoinglist=Domelement.getElementsByTagName("outgoing")
          for outgoing in outgoinglist:
                    self.outgoing.append(outgoing.firstChild.data)



class sequenceflow:
     def __init__(self):
         self.id=""
         self.name=""
         self.sourceRef=""#string sourceRef of the sequenceflow
         self.targetRef=""#string targetRef of the sequenceflow

     
   
        
