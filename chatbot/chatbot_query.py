
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
        system_mssg =   { 
                            "role": "system", 
                            "content": "Your name is Nova. Your purpose is to help users by answering their questions. Your tone should be energetic and should always be maintained professionally."
                        }
        
        self.messages.append( system_mssg )
        
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

