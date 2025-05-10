from agent.memory import ConversationMemory
from llm.openai_client import OpenAiClient
from llm.openai_prompt import OpenAIPrompt
import os
import json
from agent.prompts import Prompt

class AnalyzeAdditionalQueryAgent:
    def __init__(self, db: None, memory: ConversationMemory, probing_agent: None):
        self.memory = memory
        self.openai_client = OpenAiClient()
        self.probing_agent = probing_agent
        self.db = db

    def analyze_relevence(self, user_input: str, question: str):
        openai_prompt = OpenAIPrompt(system_prompt=Prompt().analyze_relevance_prompt(user_input, question),
                                     messages=[], openai_model=os.getenv("OPENAI_MODEL"))
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
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_probing (relevance)")

        return json_response['relevance'], json_response['relevant_query']


    def analyze(self):
        # Analyze all the user's responses to the probing questions to determine if the agent has enough information to provide a satisfactory answer.
        openai_prompt = OpenAIPrompt(system_prompt=self._analyze_system_prompt(), messages=self.memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
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
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_probing (user satisafactory response or not)")
        return json_response['satisfactory'] == '1'
    
    def analyze_external(self, probe_count: int):
        openai_prompt = OpenAIPrompt(system_prompt=Prompt().analyze_query_details_external_prompt(query_details=self.probing_agent.query_details,
                                                                                                  probe_count=probe_count),
                                     messages=self.memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
        openai_prompt_messages = openai_prompt.to_openai_format()
        response = self.openai_client.chat_completion(
            model=os.getenv("OPENAI_MODEL"),
            messages=openai_prompt_messages["messages"],
            max_completion_tokens=openai_prompt_messages["max_tokens"],
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        json_response = json.loads(response.choices[0].message.content)
        print(json_response)
        self.db.log_llm_interaction(conversation_id= self.memory.conversation_id, prompt=openai_prompt_messages["messages"],
                                    response=json_response, model=os.getenv("OPENAI_MODEL"),
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_probing (external api flow)")
        return json_response['next_action']
    
    def analyze_relevence_external_api(self, user_input: str, question: str, next_action: str, probe_count: int):
        openai_prompt = OpenAIPrompt(system_prompt=Prompt().analyze_relevance_prompt_external(user_input, question,
                                                                                              next_action, probe_count),
                                     messages=[], openai_model=os.getenv("OPENAI_MODEL"))
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
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_probing (relevance) (external api flow)")

        return json_response['relevance'], json_response['relevant_query'], json_response['next_action']
    
    def modify_query_external_api(self):
        openai_prompt = OpenAIPrompt(system_prompt=Prompt().modify_query_external_api_prompt(initial_query=self.probing_agent.csm_agent.query, query_details=self.probing_agent.query_details),
                                    messages=self.memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
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
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_probing (modify query details) (external api)")

        return json_response['modified_query']
    
    def modify_query(self):
        openai_prompt = OpenAIPrompt(system_prompt=self._modify_query_prompt(), messages=self.memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
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
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_probing (modify query details)")
        return json_response['modified_query']
        
    
    def _analyze_system_prompt(self):
        return f"""
        You are an Analytics Query Assistant. Based on the knowledge you have, you provided an answer
        to the user's query. The user is not satisified with results you provided. You have asked probing questions to the user
        to get more information. You need to analyze the user's responses to the probing questions to determine if the agent
        has enough information to provide a satisfactory answer. A summary of your knowledge base is:
        {Prompt().kb_summary()}. The agent has in depth details of the summary. So far these are the additional information gathered from the user's responses to the probing questions: "{self.probing_agent.query_details}".
        Evaluate the current responses and check all the addition information provided by the user can be targeted to the knowledge base.
        If the summary provided above has atleast 2 RELEVANT values from the additional information provided by the user, then the agent has enough information to provide a satisfactory answer.
        If the user history is completely different from the knowledge base it's not satisfactory.

        Respond in a json format in the following way: {{"satisfactory": "1/0" , "relevance": "1/0"}}.
        The "satisfactory value" should be 1 if the agent has enough information to provide a satisfactory answer and 0
        if the agent does not have enough information to provide a satisfactory answer. The value of "relevance" should be 1
        if the user's responses are relevant to the probing questions and 0 if the user's responses are not relevant to the probing questions.
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
  