from openai import OpenAI
from groq import Groq
import os

class OpenAiClient:
  def __init__(self) -> None:
    self._client = None


  def client(self):
        if self._client is not None:
            return self._client
        
        if os.getenv('ENV') == 'development':
            self._client = Groq(api_key=os.getenv('OPENAI_API_KEY'))
        else:
            self._client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        return self._client
