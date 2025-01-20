import os
import sys
from agent.probing_agent import ProbingAgent
from agent.summary_agent import SummaryAgent
from agent.agent_state import AgentState
from agent.memory import ConversationMemory
from llm.openai_client import OpenAiClient
from llm.openai_prompt import OpenAIPrompt
from agent.prompts import Prompt
import json

parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)

from knowledge_base.reports import Report

class ExternalApiAgent:
    def __init__(self, db):
        self.db = db
        self.query = None
        self.knowledge_base = Report()
        self.openai_client = OpenAiClient().client()
        self.agent_status = AgentState.INITIALIZING

    def process_query(self, query: str, memory: ConversationMemory, agent_query: bool = False):
        self.agent_status = AgentState.SEARCHING
        self.query = query
        if agent_query:
            memory.add_content(role='assistant', content=query)
        report = self._search_external_reports(query=query, memory=memory)
        memory.add_suggested_report({"title": report['title'], "description": report['description']})
        self._print_report(report)

    def handle_initial_satisfaction(self, user_satisfaction_input: str, memory: ConversationMemory):
        memory.add_content(role='assistant', content="Are you satisfied with the results?")
        memory.add_content(role='user', content=user_satisfaction_input)
        messages = [
        {
            "role": "user",
            "content": user_satisfaction_input
        }]

        openai_prompt = OpenAIPrompt(system_prompt=Prompt().user_satisfaction_system_prompt(),
                                     messages=messages, openai_model=os.getenv("OPENAI_MODEL"))
        openai_prompt_messages = openai_prompt.to_openai_format()

        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=openai_prompt_messages["messages"],
            max_completion_tokens=openai_prompt_messages["max_tokens"],
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        json_response = json.loads(response.choices[0].message.content)
        if json_response['next_action'] == "complete":
            self.agent_status = AgentState.COMPLETE
        else:
            self.agent_status = AgentState.PROBING

        self.db.log_llm_interaction(conversation_id= memory.conversation_id, prompt=openai_prompt_messages["messages"],
                                    response=json_response, model=os.getenv("OPENAI_MODEL"),
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="external_api_user_satisfaction")
        return json_response


    def process_probing(self, memory: ConversationMemory):
        if not self.agent_status == AgentState.PROBING:
            return

        probing_agent = ProbingAgent(db=self.db, memory=memory, csm_agent=self)
        probing_agent.handle_external_probing()



    def _search_external_reports(self, memory, query: str):
        openai_prompt = OpenAIPrompt(system_prompt=Prompt().external_api_prompt(query=query),
                                     messages=memory.get_contents(), openai_model=os.getenv("OPENAI_MODEL"))
        openai_prompt_messages = openai_prompt.to_openai_format()
        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=openai_prompt_messages["messages"],
            max_completion_tokens=openai_prompt_messages["max_tokens"],
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        report = json.loads(response.choices[0].message.content)
        self.db.log_llm_interaction(conversation_id= memory.conversation_id, prompt=openai_prompt_messages["messages"],
                                    response=report, model=os.getenv("OPENAI_MODEL"),
                                    tokens_used=openai_prompt_messages["num_prompt_tokens"], conversation_type="external_api")
        return report
    
    def _print_report(self, report):
        if len(report) == 0:
            print("No reports found.")
        else:
            print(f"Title: {report['title']}")
            print(f"Description: {report['description']}")
            print("\n")
        