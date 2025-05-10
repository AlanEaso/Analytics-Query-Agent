from typing import List

class ConversationMemory:
    def __init__(self, conversation_id: str):
        self.query_history = []
        self.suggested_reports = []
        self.conversation_id = conversation_id

    def add_suggested_report(self, report):
        self.suggested_reports.append(report)

    def get_suggested_reports(self) -> List[str]:
        return self.suggested_reports

    def add_content(self, role: str, content: str):
        self.query_history.append({
            "role": role,
            "content": content
        })

    def get_contents(self) -> List[str]:
        return self.query_history