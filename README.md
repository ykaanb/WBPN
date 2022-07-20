# WBPN
Web-based Petri net visualizer 

To run the app on your system:
(For more detailed information you can refer to the visual studio code tutorial :
https://code.visualstudio.com/docs/python/tutorial-flask )

1) Install a version of Python 3.10 (recommended 3.10.5)
2) Download the WBPN project
3) Inside the project directory create a virtual environment named .venv :

   #Windows
   
   py -3 -m venv .venv
   
   #Linux,MacOS
   
   python3 -m venv .venv
   
4) Activate the virtual environment .venv:

   #Windows
   
    .venv\scripts\activate
    
   #Linux,MacOS
   
    source .venv/bin/activate
    
5) Upgrade pip and install required packages within the activated environment:

   python -m pip install --upgrade pip
   
   pip install graphviz
   
   python -m pip install flask
   
   pip install Flask-Session
   
   pip install Flask-Assets
   
   pip install -U jsonpickle
   
6) Run the app within the activated environment:
   
   flask run

  
