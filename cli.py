from agent.csm_analytics_agent import CSMAnalytsgent
from agent.agent_state import AgentState
from agent.memory import ConversationMemory

def main():
    print("CSM Analytics Query Agent")
    print("------------------------")
    print("Enter your analytics report request (or 'quit' to exit):")
    try:
        while True:
            agent = CSMAnalytsgent()
            memory = ConversationMemory()
            query = input("\nQuery: ").strip()
            if query in ['quit', 'exit', 'q']:
                break

            agent.process_query(memory= memory, query=query, top_k=1)

            user_satisfaction_input = input("\n Are you satisfied with the results? ").strip()
            agent.handle_initial_satisfaction(memory= memory,user_satisfaction_input=user_satisfaction_input)

            if agent.agent_status == AgentState.COMPLETE:
                print("\nGreat! Have a nice day!")
                break

            agent.process_probing(memory=memory)

            print("\n Enter any of the following commands or enter a new search query: 'quit', 'exit', 'q' to exit")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

if __name__ == "__main__":
    main()