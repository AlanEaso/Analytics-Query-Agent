from typing import List

class ConversationMemory:
    def __init__(self, conversation_id: str):
        self.query_history = []
        self.conversation_id = conversation_id

    def add_content(self, role: str, content: str):
        self.query_history.append({
            "role": role,
            "content": content
        })

    def get_contents(self) -> List[str]:
        return self.query_history