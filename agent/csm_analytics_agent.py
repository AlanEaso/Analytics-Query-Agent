import os
import sys
from agent.probing_agent import ProbingAgent
from agent.summary_agent import SummaryAgent
from agent.agent_state import AgentState
from agent.memory import ConversationMemory
from llm.openai_client import OpenAiClient
from llm.openai_prompt import OpenAIPrompt
import json

parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)

from knowledge_base.reports import Report

class CSMAnalytsgent:
    def __init__(self, db):
        self.db = db
        self.agent_status = AgentState.INITIALIZING
        self.knowledge_base = Report()
        self.query = None
        self.openai_client = OpenAiClient().client()

    def process_query(self, memory: ConversationMemory, query: str, top_k: int = 3, agent_query: bool = False):
        self.agent_status = AgentState.SEARCHING
        if agent_query:
            memory.add_content(role='assistant', content=query)
        else:
            memory.add_content(role='user', content=query)
            self.query = query
        reports =  self.search_reports(query=query, top_k=top_k)
        valid_reports = []
        for report, _score in reports:
            if _score > 0.5:
                valid_reports.append(report)
                memory.add_suggested_report({"title": report.title, "description": report.description})
                self._print_report(report)

        return valid_reports

    def set_probing_state(self):
        self.agent_status = AgentState.PROBING

    def _print_report(self, report):
        print(f"Title: {report.title}")
        print(f"Description: {report.description}")
        print("\n")

    def search_reports(self, query: str, top_k: int = 3):
        results = self.knowledge_base.search_reports(query, top_k)

        return results

    def process_probing(self, memory: ConversationMemory):
        if not self.agent_status == AgentState.PROBING:
            return
        
        print("Probing...")
        probing_agent = ProbingAgent(db=self.db, memory=memory, csm_agent=self)
        max_probes = 5
        probe_count = 0
        user_satisfied = False
        # probing_agent.probe_user(probe_count= probe_count+1)
        while probe_count < max_probes:
            probe_user_response = probing_agent.probe_user(probe_count= probe_count+1)
            if probe_user_response == "satisifed":
                user_satisfied = True
                break
            probe_count += 1

        if not user_satisfied:
            self.agent_status = AgentState.ESCALATING
            preliminary_analysis, response = SummaryAgent(db=self.db ,memory=memory).summarize()
            self.db.create_escalation_ticket(memory.conversation_id, self.query, memory.get_suggested_reports(),
                                            preliminary_analysis=preliminary_analysis, probing_details=memory.get_contents())

            print(response)

    def handle_initial_satisfaction(self, user_satisfaction_input: str, memory: ConversationMemory):
        memory.add_content(role='assistant', content="Are you satisfied with the results?")
        memory.add_content(role='user', content=user_satisfaction_input)
        messages = [
        {
            "role": "user",
            "content": user_satisfaction_input
        }]

        openai_prompt = OpenAIPrompt(system_prompt=self._user_satisfaction_system_prompt(), messages=messages, openai_model=os.getenv("OPENAI_MODEL"))
        openai_prompt_messages = openai_prompt.to_openai_format()

        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=openai_prompt_messages["messages"],
            max_completion_tokens=openai_prompt_messages["max_tokens"],
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        json_response = json.loads(response.choices[0].message.content)
        if json_response['user_satisfaction_response'] == "no":
            self.agent_status = AgentState.PROBING
        else:
            self.agent_status = AgentState.COMPLETE

        self.db.log_llm_interaction(conversation_id= memory.conversation_id, prompt=openai_prompt_messages["messages"],
                                    response=json_response, model=os.getenv("OPENAI_MODEL"),
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="user_satisfaction")
        return json_response
    
    def _user_satisfaction_system_prompt(self):
        return """ You are an Analytics Query Agent. Based on the knowledge you have, you provided and answer
                to the user's query. The user is now asked if they are satisfied with the results. If the user is satisfied,
                return the response in the format: {user_satisfaction_response: "yes"}. If the user is not satisfied, return
                the response in the following json format: {user_satisfaction_response: "no"} . Do not deviate from the response format.
                The values should always be "yes" or "no" """
        