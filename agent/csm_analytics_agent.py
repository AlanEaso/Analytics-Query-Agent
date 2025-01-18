import os
import sys
from agent.probing_agent import ProbingAgent
from agent.memory import ConversationMemory
import openai
from llm.openai_client import OpenAiClient
import json

parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)

from knowledge_base.reports import Report
from enum import Enum

class AgentState(Enum):
    INITIALIZING = "initializing"
    SEARCHING = "searching"
    PROBING = "probing"
    ANALYZING = "analyzing"
    ESCALATING = "escalating"
    COMPLETE = "complete"

class CSMAnalytsgent:
    def __init__(self):
        self.agent_status = AgentState.INITIALIZING
        self.knowledge_base = Report()
        self.query = None
        self.openai_client = OpenAiClient().client()

    def process_query(self, memory: ConversationMemory, query: str, top_k: int = 3):
        self.agent_status = AgentState.SEARCHING
        self.query = query
        memory.add_content(role='user', query=query)
        return self.search_reports(top_k=top_k)

    def set_probing_state(self):
        self.agent_status = AgentState.PROBING

    def search_reports(self, top_k: int = 3):
        results = self.knowledge_base.search_reports(self.query, top_k)
        for report, score in results:
            print(f"Title: {report.title}")
            print(f"Description: {report.description}")
            print(f"Metrics: {report.metrics}")
            print(f"Dimensions: {report.dimensions}")
            print(f"Score: {score}")
            print()

        return results

    def process_probing(self):
        if not self.agent_status == AgentState.PROBING:
            return
        
        print("Probing...")
        # probing_agent = ProbingAgent()
        # probing_agent.probe_user("")

    def handle_initial_satisfaction(self, user_satisfaction_query: str):
        messages = [{
            "role": "system",
            "content": """ You are an Analytics Query Agent. Based on the knowledge you have, you provided and anwer
             to the user's query. The user is now asked if they are satisfied with the results. If the user is satisfied,
             return the response in the format: {user_satisfaction_response: "yes"}. If the user is not satisfied, return
             the response in the following json format: {user_satisfaction_response: "no"} . Do not deviate from the response format.
             The values should always be "yes" or "no" """
        },
        {
            "role": "user",
            "content": user_satisfaction_query
        }]

        response = self.openai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_completion_tokens=1024,
            temperature=0.5,
            response_format={"type": "json_object"} 
        )

        json_response = json.loads(response.choices[0].message.content)
        if json_response['user_satisfaction_response'] == "no":
            self.agent_status = AgentState.PROBING
        else:
            self.agent_status = AgentState.COMPLETE
        return json_response
        