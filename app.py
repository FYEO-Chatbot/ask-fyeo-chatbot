from flask import Flask, request, jsonify
import json
import torch
from model import NeuralNet
from chat import chatbot
app = Flask(__name__)


#SETUP
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


with open('intents.json', 'r', encoding="utf8") as f:
    intents = json.load(f)


FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()
context = {}



@app.route('/')
def hello():
    return 'Hello World'



@app.route('/answer', methods=['POST'])
def predict():

    if request.method == 'POST':
        question = request.json['question']
        print(question)
        response = chatbot(question, data, model, intents, context=context)

        print('RESPONSE ', response)
        return jsonify({'response': response})
    return jsonify({'error':'Invalid request type'})