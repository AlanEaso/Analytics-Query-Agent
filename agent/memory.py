from typing import List

class ConversationMemory:
    def __init__(self):
        self.query_history = []

    def add_content(self, role: str, query: str):
        self.query_history.append({
            "role": role,
            "query": query
        })

    def get_contents(self) -> List[str]:
        return self.query_history