from agent.memory import ConversationMemory
from llm.openai_client import OpenAiClient
from llm.openai_prompt import OpenAIPrompt
import os
import json
from agent.prompts import Prompt

class AnalyzeAdditionalQueryAgent:
    def __init__(self, memory: ConversationMemory, probing_agent: None):
        self.memory = memory
        self.openai_client = OpenAiClient().client()
        self.probing_agent = probing_agent

    def analyze(self):
        # Analyze all the user's responses to the probing questions to determine if the agent has enough information to provide a satisfactory answer.
        openai_prompt = OpenAIPrompt(system_prompt=self._analyze_system_prompt(), messages=self.memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
        openai_prompt_messages = openai_prompt.to_openai_format()
        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=openai_prompt_messages["messages"],
            max_completion_tokens=openai_prompt_messages["max_tokens"],
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        json_response = json.loads(response.choices[0].message.content)
        return json_response['satisfactory'] == '1'
    
    def modify_query(self):
        openai_prompt = OpenAIPrompt(system_prompt=self._modify_query_prompt(), messages=self.memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
        openai_prompt_messages = openai_prompt.to_openai_format()
        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=openai_prompt_messages["messages"],
            max_completion_tokens=openai_prompt_messages["max_tokens"],
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        json_response = json.loads(response.choices[0].message.content)
        return json_response['modified_query']
        
    
    def _analyze_system_prompt(self):
        return f"""
        You are an Analytics Query Assistant. Based on the knowledge you have, you provided and answer
        to the user's query. The user is not satisified with results you provided. You have asked probing questions to the user
        to get more information. You need to analyze the user's responses to the probing questions to determine if the agent
        has enough information to provide a satisfactory answer. A summary of your knowledge base is:
        {Prompt().kb_summary()}

        Make sure you stick to the context provided below which is the conversation between you (the agent) and the user. Always
        stay contextually relevant. Respond in a json format in the following way: {{"satisfactory": "1/0" , "relevance": "1/0"}}.
        The "satisfactory value" should be 1 if the agent has enough information to provide a satisfactory answer and 0
        if the agent does not have enough information to provide a satisfactory answer. The value of "relevance" should be 1
        if the user's responses are relevant to the probing questions and 0 if the user's responses are not relevant to the probing questions.
        If there is atleast 3 values related to the ones listed in the summary,
        consider it satisfactory.
        Stick to the response format. 
        """
    
    def _modify_query_prompt(self):
        return f"""
        You are an Analytics Query Assistant. Based on the knowledge you have, you provided and answer
        to the user's query. The user is not satisified with results you provided. You have asked probing questions to the user
        to get more information. You have analyzed the user's responses to the probing questions and determined that you have
        enough information to provide a satisfactory answer. You need to modify the initial query based on the user's responses
        to the probing questions. User's initial query is: "{self.probing_agent.csm_agent.query}".
        Addition relevant information you have gathered is: "{self.probing_agent.query_details}".
        A summary of your knowledge base is:
        {Prompt().kb_summary()}

        Make sure you stick to the context provided below which is the conversation between you (the agent) and the user. Always
        stay contextually relevant. Respond in a json format in the following way: {{"modified_query": "The modified query based on the user's initial query" }}.
        Stick to the response format. 
        """
  