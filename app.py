import json
import os
from dotenv import load_dotenv

import labstep
from labstep.service.config import configService

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin

from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.readers.json import JSONReader


# Set up Flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = True


# Get .env
folder = os.path.dirname(os.path.abspath(__file__))
load_dotenv(f'{folder}/.env', override=True)


# Set host as staging
configService.setHost('https://api-staging.labstep.com')


## Authenticate user
load_dotenv()
USERNAME = os.getenv('LABSTEP_USERNAME')
APIKEY = os.getenv('LABSTEP_APIKEY')
WORKSPACE_ID = int(os.getenv('WORKSPACE_ID'))
user = labstep.authenticate(USERNAME, APIKEY)
workspace = user.getWorkspace(WORKSPACE_ID)


# Set up embedding model
Settings.embed_model = OllamaEmbedding(model_name="mxbai-embed-large")

# Setand configure Ollama LLM model
Settings.llm = Ollama(model="phi", request_timeout=360.0, temperature=0.1)


# Method to reset JSON file (called on app refresh)
def resetJSON():
    empty_json = [
        "Experiments",
        {

        }
    ]
    with open('./data/experiments.json', 'w', encoding='utf-8') as f:
        json.dump(empty_json, f, ensure_ascii=False, indent=4)
    return "Experiments file reset!"


# Reset JSON and serve index template
@app.route("/", methods=["GET"])
def home():
    resetJSON()
    return render_template("index.html")


# Get list of Collections in Workspace from Labstep
@app.route("/fetch-collections", methods=["GET"])
def fetch_collections():
    collections = workspace.getCollections()
    collection_names = [collection.name for collection in collections]

    return collection_names


# Dump contents of Experiments in selected Collection
@app.route("/learn", methods=["POST"])
@cross_origin()
def learn():
    collection = request.json

    if query is not None:
        experiments_collection = workspace.getCollections(search_query=collection)
        experiments_collection_id = experiments_collection[0].id
        experiments = user.getExperiments(collection_id=experiments_collection_id)
        experiment_entries = []

        for experiment in experiments:
            name = experiment.name
            entry = experiment.getEntry()
            experiment_entries.append(name)
            experiment_entries.append(entry)

        with open('./data/experiments.json', 'w', encoding='utf-8') as f:
            json.dump(experiment_entries, f, ensure_ascii=False, indent=4)
            
        return "Steppy has studied the Experiments in the collection (" + str(collection) + "!"
    else:
        return jsonify({"error": "Collection is missing!"}), 400


# Learn from JSON file of Experiment content and query
@app.route('/query', methods=['POST'])
@cross_origin()
def query():
    query = request.json

    if query is not None:
        # Initialize JSONReader
        reader = JSONReader(levels_back=0, clean_json=True)

        # Load data from JSON file
        documents = reader.load_data(input_file="./data/experiments.json")

        index = VectorStoreIndex.from_documents(
            documents,
        )

        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return str(response)
    else:
        return jsonify({"error": "Query field is missing!"}), 400


# Run Flask app
if __name__ == '__main__':
    app.run()