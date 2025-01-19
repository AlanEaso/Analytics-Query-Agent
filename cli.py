from agent.csm_analytics_agent import CSMAnalytsgent
from agent.agent_state import AgentState
from agent.memory import ConversationMemory
from db.database import MongoDB
from loguru import logger
import uuid

logger.add("logs/csm_analytics_{time}.log", rotation="500 MB")
def main():
    db = MongoDB()
    conversation_id = str(uuid.uuid4())
    print("Conversation ID: ", conversation_id)
    print("CSM Analytics Query Agent")
    print("------------------------")
    print("Enter your analytics report request (or 'quit' to exit):")
    try:
        while True:
            agent = CSMAnalytsgent(db=db)
            memory = ConversationMemory(conversation_id=conversation_id)
            query = input("\nQuery: ").strip()
            if query in ['quit', 'exit', 'q']:
                break

            reports = agent.process_query(memory= memory, query=query, top_k=1)

            if len(reports) == 0:
                print("No reports found. This feature is under development. Please try again.")
                # Execute external api flow
                continue

            user_satisfaction_input = input("\n Are you satisfied with the results? ").strip()
            agent.handle_initial_satisfaction(memory= memory,user_satisfaction_input=user_satisfaction_input)

            if agent.agent_status == AgentState.COMPLETE:
                print("\nGreat! Have a nice day!")
                continue

            agent.process_probing(memory=memory)

            print("\n Enter any of the following commands or enter a new search query: 'quit', 'exit', 'q' to exit")
    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        raise e
    finally:
        db.close()
        print("Closed MongoDB connection")

if __name__ == "__main__":
    main()