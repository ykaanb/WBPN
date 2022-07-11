from flask import Flask, render_template, make_response, request, Markup, session
from flask_assets import Bundle, Environment
from flask_session import Session
from datetime import datetime
from petrinet import analysis as anl
from petrinet import parse_tpn as tpn
from petrinet import parse_pnml as pnml
from petrinet import parse_bpmn as bpmn
from petrinet import visualiser as viz
from petrinet.petrinet import Edge, Marking, PetriNet, Place, Transition 
import os
import re
import jsonpickle

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "sjg1dslk0324üopkfa3"
Session(app)

assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css")
assets.register("css", css)
css.build()

sessionkey_petrinet_base = "sessionkey_petrinet_base"
sessionkey_petrinet = "sessionkey_petrinet_net"
sessionkey_markingid = "sessionkey_petrinet_markingid"

@app.route("/", methods = [ "GET"])
def home():
    session.clear()
    return render_template(
        'index.html',
        year=datetime.now().year
    )

@app.route('/upload', methods = [ 'POST'])
def upload_parse_file():
    f = request.files['file']
    if not f :
        if not session:
             return home()
        else:
            if sessionkey_petrinet in session:
                net=load_net(session[sessionkey_petrinet])
                return create_response(net,int(session[sessionkey_markingid]))
            else:
                net=load_net(session[sessionkey_petrinet_base])
                return create_response(net,0)


    lines = f.read().decode("utf-8")
    lines = re.sub('(\r\n|\r)', '\n', lines)
    extension = os.path.splitext(f.filename)[1]

    if extension == ".tpn":
        net = tpn.parse_tpn(lines.split(";"))
    elif extension == ".pnml":
        net = pnml.parse_pnml_string(lines)
    elif extension ==".bpmn":
        net = bpmn.parse_bpmn_string(lines)
    if net:
        
        # net.places["p1"].marking=1

        initial=Marking()
        initial.id=0
        initial.marking=net.get_pmarkings()
        net.markings.append(initial)
        net.regulate_transitions_readiness()
   
        net.set_cover()
        anl.check_WFnet(net)
        session.permanent=False
        session[sessionkey_petrinet_base]=jsonpickle.encode(net)

        return create_response(net, 0)
    else:
        return home()

@app.route('/marking', methods = [ 'POST'])
def set_markings():
    
    net = load_net(session[sessionkey_petrinet_base])
    current_markingid = 0

    try:

        input = parse_places(request.form['initial_marking'])
        
        for k in input:
            net.places[k].marking = input.get(k)
        
        net.markings=[]
        net.regulate_transitions_readiness()
        initial=Marking()
        
        initial.id=0

        initial.marking=net.get_pmarkings()
        initial.r_t_list=net.get_ready_transitions()
        net.markings.append(initial)
        net.set_cover()

        
        anl.set_boundness(net)
        anl.check_dead_transitions(net)
        anl.set_deadlocks(net)
        if net.boundness!=-1:
            anl.check_L4_live(net)
            anl.check_L3_live(net)
            anl.check_L2_L1_live(net)
        
            if  len(input)==1 and net.WFnet :
                    for key in input:
                        placeid=key
                        i_tokens=input[key]
                    if placeid==net.start_nodes[0]:
                        anl.check_soundness(net,i_tokens)

            
        return create_response(net, current_markingid)

    except:
        
        return create_response(net, current_markingid)
 

@app.route('/next', methods = [ 'POST'])
def increase_marking():
    net = load_net(session[sessionkey_petrinet])
    current_markingid = int(session[sessionkey_markingid])
    return create_response(net, current_markingid + 1)

@app.route('/previous', methods = [ 'POST'])
def decrease_marking():
    net = load_net(session[sessionkey_petrinet])
    current_markingid = int(session[sessionkey_markingid])
    return create_response(net, current_markingid - 1)

def create_response(net, markingid):
    
    resp = make_response(
        render_template('index.html',
          markingid = markingid,
          net = net,
          canforwards = True if markingid + 1 <= net.markingcount else False,
          canbackwards = True if markingid - 1 >= 0 else False,
          markingdict = create_marking_dict(net,markingid),
          #Maybe add width=\"400px\" height=\"800px\" 
          img = Markup(re.sub("<svg width=\"\d+pt\" height=\"\d+pt\"","<svg ",viz.viz_pt(net, markingid))),
          year = datetime.now().year))

    # session.pop(sessionkey_petrinet, None)
    # session.permanent=False
    session[sessionkey_petrinet] = jsonpickle.encode(net)
    session[sessionkey_markingid] = str(markingid)
    return resp

def load_net(json_net):
    return jsonpickle.decode(json_net, classes=[PetriNet,Marking,Edge,Transition,Place])

def parse_places(inputstring):
    output = {}
    inputs = inputstring.split(",")
    for input in inputs:
        result = input.strip().split("=")
        output[result[0].strip()] = int(result[1].strip())
    return output

#A method to create the matrix up to the marking it is supposed to show
def create_marking_dict(net,current_marking_id):
    markings = {}
    markingcount=0
    
    for k in net.markings:
        output = []#a list for ready transitions string , t_paths string and incomings string
        if(markingcount<=current_marking_id):
            #to save ready transitions
            ready_t="ready to fire:["
            for r_t in k.r_t_list:
                ready_t+=r_t.id +","
            ready_t+="]"
            output.append(ready_t)
            #to save t_paths
            output.append("transition paths:"+k.t_pathstring)
            #to save incomings
            temp=""
            for key in k.incoming:
                temp+="M" + str(key) + k.incoming[key].id
            
            output.append("Incomings:" + temp)
            temp=""
            for t_p in k.t_paths:
                temp+="M" + str(k.t_paths[t_p].id)
            output.append("t_paths:" + temp)
            markings["M"+str(k.id) + ":" +str(k.marking)] = output
            markingcount+=1
    return markings