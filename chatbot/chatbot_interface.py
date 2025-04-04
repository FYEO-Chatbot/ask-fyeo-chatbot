from .bow_chatbot import BOWChatbot
from .bert_chatbot import BERTChatbot
# from .sbert_chatbot import SBERTChatbot
from .tfidf import TFIDF
import torch
from enums import Mode
import io
from smart_open import open as smart_open

#Uses facade pattern to provide a simple interface to access all functionality of the chatbot and allows for easy switching between different chatbot models
class ChatbotInterface():
    bert_model = "bert"
    bow_model = "bow"
    # sbert_model = "sbert"


    def __init__(self, type, data, mode, **kwargs):
        self.type = type
        self.data = data 
        #files that contain the saved state of our trained models
        if mode == Mode.DEV:
            bert_url = "bertmodel.pth"
            bow_url = "bowmodel.pth"
        else:
            bert_url = "https://fyeochatbotmodels.s3.us-east-2.amazonaws.com/bertmodel.pth"
            bow_url = "https://fyeochatbotmodels.s3.us-east-2.amazonaws.com/bowmodel.pth"

        if type == ChatbotInterface.bert_model:
            self.model = BERTChatbot(**kwargs)
            self.file = self.get_file(bert_url, mode)
        # elif type == ChatbotInterface.sbert_model:
        #     self.model = SBERTChatbot(**kwargs)
        #     self.file = None
        else:
            self.model = BOWChatbot(**kwargs)
            self.file = self.get_file(bow_url, mode)
        
     

    def train(self):
        self.model.train(self.data)
    

    def chat(self):
        self.model.chat(self.data, self.file)
      

    def get_response(self, question):
        try:
            # print(question)
            return self.model.get_response(question, self.data, self.file)
        except Exception as e:
            print(e)
            return e
        
    def find_duplicates(self, tag, patterns):
        return TFIDF.find_duplicates(self.data, tag, patterns)
   

    def get_file(self,url, mode):
        if mode == Mode.DEV:
            try:
                file = torch.load(url)
                return file
            except Exception as e:
                print(e)
                return None
        else:
            with smart_open(url, 'rb') as f:
                buffer = io.BytesIO(f.read())
                file = torch.load(buffer)
                return file


        
