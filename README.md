**How to Use**

1. Download and install Ollama from https://ollama.com/
2. Once Ollama is installed and running on your machine, run ```ollama pull phi``` and ```ollama pull mxbai-embed-large``` (these may take a while to download)
3. Create a ```.env``` file at root level with variables for your ```LABSTEP_USERNAME```, ```LABSTEP_APIKEY``` and ```WORKSPACE_ID``` (this is used to fetch your Collections and Experiments)
4. Create a virtualenv and run ```pip install -r requirements.txt``` within
5. Run ```python app.py```
