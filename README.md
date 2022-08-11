# WBPN
Web-based Petri net visualizer 

To run the app on your system:

(For detailed information you can refer to the visual studio code tutorial :
https://code.visualstudio.com/docs/python/tutorial-flask )

1) Install a version of Python 3.10 (recommended 3.10.5)
2) Download and install Graphviz on your system 

   Using Graphviz requires 2 steps:
   
   1) Download and install Graphviz from https://www.graphviz.org/
   
   After installing Graphviz, make sure that the directory containing the dot executable (bin/ subdirectory) is on your systems' PATH 
   
   2) Installing the graphviz python package with pip install graphviz (this is done in step 6)
   
   (For detailed information you can refer to https://pypi.org/project/graphviz/)

3) Download the WBPN project
4) Inside the project directory create a virtual environment named .venv :

   #Windows
   
   py -3 -m venv .venv
   
   #Linux,MacOS
   
   python3 -m venv .venv
   
5) Activate the virtual environment .venv:

   #Windows
   
    .venv\scripts\activate
    
   #Linux,MacOS
   
    source .venv/bin/activate
    
6) Upgrade pip and install required packages within the activated environment:

   python -m pip install --upgrade pip
   
   pip install graphviz
   
   python -m pip install flask
   
   pip install Flask-Session
   
   pip install Flask-Assets
   
   pip install jsonpickle
   
7) Run the app within the activated environment:
   
   flask run

  
