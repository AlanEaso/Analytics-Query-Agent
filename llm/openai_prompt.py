import tiktoken
import os

class OpenAIPrompt:
    
    MAX_TOKENS= 3000

    def __init__(self, system_prompt, messages, openai_model) -> None:
        self.system_prompt = system_prompt
        self.messages = messages
        self.openai_model = openai_model
        self._messages_for_openai = None
        self._num_prompt_tokens = None

    def messages_for_open_ai(self):
        result = []
        if self._messages_for_openai is not None:
            return self._messages_for_openai, self._num_prompt_tokens
        
        max_tokens = self.MAX_TOKENS
        max_tokens -= self._count_tokens(self.system_prompt)
        result.append({'role': 'system', 'content': self.system_prompt})

        history = []
        if max_tokens > 0:
            history_messages = [message for message in self.messages[-6:]]
            history_messages.reverse()
            addable_history_messages, token_count = self._filter_messages(history_messages, max_tokens)
            history.extend(addable_history_messages)
            max_tokens -= token_count
        
        history.reverse()
        result += history
        self._messages_for_openai = result
        self._num_prompt_tokens = self.MAX_TOKENS - max_tokens
        print(f"TOKENS LEFT: {max_tokens}")

        return self._messages_for_openai, self._num_prompt_tokens


    def _count_tokens(self, text):
        if os.getenv('ENV') == 'development':
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        encoding = tiktoken.encoding_for_model(self.openai_model)
        return len(encoding.encode(text))
    
    def _filter_messages(self, messages, max_tokens):
        output = []
        total_tokens = 0
        for message in messages:
            message_content = message['content']
            message_tokens = self._count_tokens(message_content)
            if total_tokens + message_tokens < max_tokens:
                output.append(message)
                total_tokens += message_tokens
            else:
                break
        return output, total_tokens
    
    def to_openai_format(self):
        messages, num_prompt_token = self.messages_for_open_ai()
        return {
            "messages": messages,
            "max_tokens": self.MAX_TOKENS,
        }
