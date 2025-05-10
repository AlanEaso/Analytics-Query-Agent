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

    def chat_completion(self, model, messages, max_completion_tokens, temperature, response_format):
        retry_count = 0
        response_flag = False
        response = None

        while not response_flag and retry_count <= 3:
            try:
                retry_count += 1
                response = self.client().chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=max_completion_tokens,
                    temperature=temperature,
                    response_format=response_format
                )
                response_flag = True
            except Exception as e:
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                if retry_count >= 3:
                    raise e
                continue

        return response
