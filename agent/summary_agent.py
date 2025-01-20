from llm.openai_client import OpenAiClient
from llm.openai_prompt import OpenAIPrompt
from agent.memory import ConversationMemory

import os
import json

class SummaryAgent:
    def __init__(self, db: None, memory: ConversationMemory):
        self.memory = memory
        self.openai_client = OpenAiClient()
        self.db = db
      

    def summarize(self):
        openai_prompt = OpenAIPrompt(system_prompt=self._summarize_system_prompt(), messages=self.memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
        openai_prompt_messages = openai_prompt.to_openai_format()
        response = self.openai_client.chat_completion(
            model=os.getenv("OPENAI_MODEL"),
            messages=openai_prompt_messages["messages"],
            max_completion_tokens=openai_prompt_messages["max_tokens"],
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        json_response = json.loads(response.choices[0].message.content)
        self.db.log_llm_interaction(conversation_id= self.memory.conversation_id, prompt=openai_prompt_messages["messages"],
                                    response=json_response, model=os.getenv("OPENAI_MODEL"),
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="summary")

        return json_response['summary'], json_response['apology message']
    
    def _summarize_system_prompt(self):
        return """
        You are an Analytics Query Assistant. Based on the knowledge you have, you provided an answer and the user is not satisified with the results you provided.
        Based on the conversation given below, summarize the conversation and provide a preliminary analysis of the conversation.
        Also add an apology message to the user for the inconvenience caused.

        This data will be subsjected to human intervention for further analysis. Make sure you give a clear and concise summary of the conversation.
        Return the response in json format.
        The format should be as follows:
        {"summary": "The summary of the conversation", "apology message": "The apology message to the user"}

        Do not deviate from the format.
        """