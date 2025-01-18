import os
import sys

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

    def process_query(self, query: str, top_k: int = 3):
        self.agent_status = AgentState.SEARCHING
        return self.search_reports(query=query, top_k=top_k)

    def set_probing_state(self):
        self.agent_status = AgentState.PROBING

    def search_reports(self, query: str, top_k: int = 3):
        results = self.knowledge_base.search_reports(query, top_k)
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
        # Code to probe the user for more information
        