from agent.memory import ConversationMemory
from agent.agent_state import AgentState
from agent.analyze_additional_query_agent import AnalyzeAdditionalQueryAgent
from agent.prompts import Prompt
from llm.openai_client import OpenAiClient
from llm.openai_prompt import OpenAIPrompt
from agent.summary_agent import SummaryAgent
import os
import json
import requests

class ProbingAgent:
    def __init__(self, db, memory: ConversationMemory, csm_agent: None):
        self.csm_agent = csm_agent
        self.memory = memory
        self.query_details = []
        self.probing_questions = []
        self.modified_query = None
        self.db = db
        self.openai_client = OpenAiClient()

    def probe_user(self, probe_count: int):
        # Create a probing question based on the user's query and the agent's response
        probing_question = self._generate_probing_question()
        self.probing_questions.append(probing_question['question'])

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

    def handle_external_probing(self):
        max_probe_count = 5
        probe_count = 1
        next_action = 'continue'
        while probe_count <= max_probe_count and next_action == 'continue':
            response  = self._generate_external_probing_question(probe_count=probe_count)
            self.probing_questions.append(response["question"])
            next_action = response['next_action']
            print(response["question"])
            self.memory.add_content(role='assistant', content=response["question"])

            next_action = self._get_user_probing_response_external(probing_question=response['question'],
                                                                   next_action=next_action,
                                                                   probe_count=probe_count)
            probe_count += 1
            if next_action == 'evaluate':
                next_action = self._analyze_all_additional_query_inputs_external(probe_count=probe_count)
                if next_action == 'evaluate':
                    user_satisified = self._hanlde_external_satisfactory_response()
                    if user_satisified:
                        next_action = 'complete'
                    else:
                        next_action = 'continue'
                elif next_action == 'escalate':
                    response = self._escalate()
                    print(response)
                else:
                    pass
        if next_action != 'complete':
            response = self._escalate()
            print(response)


    def _escalate(self):
        self.csm_agent.agent_status = AgentState.ESCALATING
        preliminary_analysis, response = SummaryAgent(db=self.db ,memory=self.memory).summarize()
        self.db.create_escalation_ticket(self.memory.conversation_id, self.csm_agent.query, 
                                            self.memory.get_suggested_reports(),
                                            preliminary_analysis=preliminary_analysis,
                                            probing_details=self.memory.get_contents())

        message_for_team = f"Escalation ticket created for conversation {self.memory.conversation_id}. Summary: of the conversation: {preliminary_analysis}. Please check the conversation and close the ticket."
            
        try:
            requests.post("http://slack_notifier:3000/notify",
                        json={"message": message_for_team},
                        headers={"x-api-key": os.getenv("EXTERNAL_SLACK_NOTIFIER_API_KEY")},
                        timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Error sending notification: {e}")
        
        return response

    def _generate_external_probing_question(self, probe_count: int):
        openai_prompt = OpenAIPrompt(system_prompt=Prompt().external_probing_system_prompt(self.csm_agent.query,
                                                                                           probe_count,
                                                                                           self.probing_questions),
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
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="external_api_probing (genreate question)")
        return json_response
        

    def _analyze_all_additional_query_inputs_external(self, probe_count: int):
        # Analyze all the user's responses to the probing questions to determine if the agent has enough information to provide a satisfactory answer.
        return AnalyzeAdditionalQueryAgent(db=self.db, memory=self.memory, probing_agent=self).analyze_external(probe_count=probe_count)
    
    def _hanlde_external_satisfactory_response(self):
        self.modified_query = AnalyzeAdditionalQueryAgent(db=self.db, memory=self.memory, probing_agent=self).modify_query_external_api()
        self.csm_agent.process_query(memory=self.memory, query=self.modified_query, agent_query=True)

        user_satisfaction_input = input("\n Are you satisfied with the results? ").strip()
        self.csm_agent.handle_initial_satisfaction(memory= self.memory,user_satisfaction_input=user_satisfaction_input)
        if self.csm_agent.agent_status == AgentState.COMPLETE:
            print("\nGreat! Have a nice day!")
            return True
    
    def _analyze_all_additional_query_inputs(self):
        # Analyze all the user's responses to the probing questions to determine if the agent has enough information to provide a satisfactory answer.
        return AnalyzeAdditionalQueryAgent(db=self.db, memory=self.memory, probing_agent=self).analyze()
    
    def _get_user_probing_response_external(self, probing_question, next_action, probe_count):
        user_input = input("\nKindly Enter your response : \n").strip()
        relevence , relevent_query , next_action = AnalyzeAdditionalQueryAgent(db=self.db, memory=self.memory,
                                                                               probing_agent=self).analyze_relevence_external_api(user_input=user_input,
                                                                                                                                  question= probing_question,
                                                                                                                                  next_action=next_action,
                                                                                                                                  probe_count=probe_count)
        if relevence == '1':
            self.query_details.append(relevent_query)
        
        self.memory.add_content(role='user', content=user_input)
        return next_action
    
    def _get_user_probing_response(self, probing_question):
        user_input = input("\nKindly Enter your response : ").strip()
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
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_probing (generate question)")
        return json_response
    
    def _hanlde_satisfactory_response(self):
        self.modified_query = AnalyzeAdditionalQueryAgent(db=self.db, memory=self.memory, probing_agent=self).modify_query()
        results = self.csm_agent.process_query(memory=self.memory, query=self.modified_query, top_k=1, agent_query=True)
        if len(results) == 0:
            return False

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
        thoroughly. Already asked question seperated by comma are: "{(', ').join(self.probing_questions)}" Make sure you don't ask the same questions.

        Make sure you stick to the context provided below which is the conversation between you (the agent) and the user. Always
        stay contextually relevant. Respond in a json format in the following way: {{"question": "The question generated be you" }}.
        Stick to the response format. 
        """
