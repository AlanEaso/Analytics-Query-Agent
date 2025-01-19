from agent.memory import ConversationMemory
from agent.agent_state import AgentState
from agent.analyze_additional_query_agent import AnalyzeAdditionalQueryAgent
from agent.prompts import Prompt
from llm.openai_client import OpenAiClient
from llm.openai_prompt import OpenAIPrompt
import os
import json

class ProbingAgent:
    def __init__(self, db, memory: ConversationMemory, csm_agent: None):
        self.csm_agent = csm_agent
        self.memory = memory
        self.query_details = []
        self.modified_query = None
        self.db = db
        self.openai_client = OpenAiClient().client()

    def probe_user(self, probe_count: int):
        # Create a probing question based on the user's query and the agent's response
        probing_question = self._generate_probing_question()
        print(probing_question['question'])
        self.memory.add_content(role='assistant', content=probing_question["question"])

        # Get the user's response to the probing question
        self._get_user_probing_response(probing_question=probing_question['question'])


        # Check if minimum probe count has reached
        if probe_count > 2:
            satisfactory = self._analyze_all_additional_query_inputs()
            if satisfactory:
                user_satisified = self._hanlde_satisfactory_response()
                if user_satisified:
                    return "satisifed"
            else:
                pass
    
    def _analyze_all_additional_query_inputs(self):
        # Analyze all the user's responses to the probing questions to determine if the agent has enough information to provide a satisfactory answer.
        return AnalyzeAdditionalQueryAgent(db=self.db, memory=self.memory, probing_agent=self).analyze()
    
    def _get_user_probing_response(self, probing_question):
        user_input = input("\nKindly Enter your response : \n").strip()
        relevence , relevent_query = AnalyzeAdditionalQueryAgent(db=self.db, memory=self.memory,
                                                                 probing_agent=self).analyze_relevence(user_input=user_input,
                                                                                                       question= probing_question)
        if relevence == '1':
            self.query_details.append(relevent_query)
        
        self.memory.add_content(role='user', content=user_input)
    
    def _generate_probing_question(self):
        # Generate a probing question based on the user's query and the agent's response
        openai_prompt = OpenAIPrompt(system_prompt=self._probing_system_prompt(), messages=self.memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
        openai_prompt_messages = openai_prompt.to_openai_format()
        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=openai_prompt_messages["messages"],
            max_completion_tokens=openai_prompt_messages["max_tokens"],
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        json_response = json.loads(response.choices[0].message.content)
        self.db.log_llm_interaction(conversation_id= self.memory.conversation_id, prompt=openai_prompt_messages["messages"],
                                    response=json_response, model=os.getenv("OPENAI_MODEL"),
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_probing")
        return json_response
    
    def _hanlde_satisfactory_response(self):
        self.modified_query = AnalyzeAdditionalQueryAgent(db=self.db, memory=self.memory, probing_agent=self).modify_query()
        self.csm_agent.process_query(memory=self.memory, query=self.modified_query, top_k=1, agent_query=True)

        user_satisfaction_input = input("\n Are you satisfied with the results? ").strip()
        self.csm_agent.handle_initial_satisfaction(memory= self.memory,user_satisfaction_input=user_satisfaction_input)
        if self.csm_agent.agent_status == AgentState.COMPLETE:
            print("\nGreat! Have a nice day!")
            return True
    
    def _probing_system_prompt(self):
        return f"""
        You are an Analytics Query Assistant. Based on the knowledge you have, you provided and answer
        to the user's query. The user is not satisified with results you provided. You need to ask specific and relevant
        questions to better understand the user's analytics needs.
        Generate specific, relevant questions to better understand the user's analytics needs.
        Generate context-specific follow-up questions. Make sure you only ask one question at a time.
        Questions should be cleaer and concise and be focussed on getting more details into the user's initial query which was not
        sufficient to get data from knowledge base. A summary of your knowledge base is: {Prompt().kb_summary()}
        User's initial query is: "{self.csm_agent.query}".

        Your questions should be focused on getting more information to make a query to the knowledge base.
        You can focus questions on:
                1. Specific metrics needed
                2. Business context
                3. Organizational department/team focus
                4. Required granularity (high-level vs. detailed)
                5. Time period of interest
    
        You should adapt questioning strategy based on the initial query by the user.
        You SHOULD NOT repeat the questions or SHOULD NOT ask questions again to which user has already provided answers. Analyze the user's responses
        thoroughly.

        Make sure you stick to the context provided below which is the conversation between you (the agent) and the user. Always
        stay contextually relevant. Respond in a json format in the following way: {{"question": "The question generated be you" }}.
        Stick to the response format. 
        """
