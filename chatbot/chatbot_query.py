
import json
import os
import openai
import dotenv
import re

dotenv.load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")


class CHAT():
    client = openai.AzureOpenAI( azure_endpoint = endpoint, api_key=api_key, api_version="2024-02-15-preview" )
    messages = []
    
    def __init__(self) -> None:
            self.messages = [
                                {
                                    "role":"system",
                                    "content":"Your name is Nova. Your purpose is to help users by answering their questions. Your tone should be energetic and should always be maintained professionally. Your name is Nova. You are a Shakespearean writing assistant who speaks in a Shakespearean style. You help people come up with creative ideas and content like stories, poems, and songs that use Shakespearean style of writing style, including words like \"thou\" and \"hath”.\nHere are some example of Shakespeare's style:\n - Romeo, Romeo! Wherefore art thou Romeo?\n - Love looks not with the eyes, but with the mind; and therefore is winged Cupid painted blind.\n - Shall I compare thee to a summer’s day? Thou art more lovely and more temperate."
                                },
                                {
                                    "role":"user",
                                    "content":"Hello there! What is your name?"
                                },
                                {
                                    "role":"assistant",
                                    "content":"I am Nova, a humble AI assistant. How may I assist thee on this fine day?"
                                },
                                {
                                    "role":"user",
                                    "content":"who are you?"
                                },
                                {
                                    "role":"assistant",
                                    "content":"Hi there! I'm Nova your AI assistant. I'll help you with any questions or inquiries you may have about Swift Courier."
                                },
                                {
                                    "role":"user",
                                    "content":"What is your role?"
                                },
                                {
                                    "role":"assistant",
                                    "content":"Your role/purpose is to help users by answering their questions. Your tone should be energetic and should always be maintained professionally."
                                }
                            ]
        
    def get_response(self, content):
        message =   { "role": "user", "content": content }
        self.messages.append( message )
        
        completion = self.client.chat.completions.create(
                                                            model=deployment,
                                                            messages=self.messages,
                                                            extra_body={
                                                                "data_sources":[
                                                                    {
                                                                        "type": "azure_search",
                                                                        "parameters": {
                                                                            "endpoint": os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
                                                                            "index_name": os.getenv("AZURE_AI_SEARCH_INDEX"),
                                                                            "authentication": {
                                                                                "type": "api_key",
                                                                                "key": os.getenv("AZURE_AI_SEARCH_API_KEY"),
                                                                            }
                                                                        }
                                                                    }
                                                                ],
                                                            }
                                                        )

        # print(completion.model_dump_json(indent=4))
        response = json.loads( completion.model_dump_json(indent=4) )
        
        return response
    
    def get_mssg(response: dict) -> str:
        return response["choices"][0]["message"]["content"]

    def get_response_mssg(self, message: str) -> str:
        rexs = [r" \[.*?\] ", r" \[.*?\]", r"\[.*?\] ", r"\[.*?\]"]
        raw_message = self.get_response( content=message )["choices"][0]["message"]["content"]
        
        [ raw_message := re.sub(rex, "", raw_message) for rex in rexs ]

        return raw_message

