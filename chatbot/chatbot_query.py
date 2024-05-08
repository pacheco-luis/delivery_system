
import os
import openai
import dotenv

dotenv.load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")

client = openai.AzureOpenAI( azure_endpoint = endpoint, api_key=api_key, api_version="2024-02-15-preview" )

completion = client.chat.completions.create(
                                                model=deployment,
                                                messages=[
                                                                {
                                                                    "role": "system", "content": "Your name is Nova. Your purpose is to help users by answering their questions. Your tone should be energetic and should always be maintained professionally.",
                                                                    # "role": "user", "content": "Introduce yourself please. Say your name too.",
                                                                    "role": "user", "content": "What is swift courier?",
                                                                },
                                                            ],
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

print(completion.model_dump_json(indent=4))