from agent.csm_analytics_agent import CSMAnalytsgent, AgentState
from agent.memory import ConversationMemory

def main():
    agent = CSMAnalytsgent()
    memory = ConversationMemory()
    print("CSM Analytics Query Agent")
    print("------------------------")
    print("Enter your analytics report request (or 'quit' to exit):")
    try:
        while True:
            query = input("\nQuery: ").strip()
            if query in ['quit', 'exit', 'q']:
                break

            agent.process_query(memory= memory, query=query, top_k=1)

            user_satisfaction_query = input("\n Are you satisfied with the results?: ").strip()
            agent.handle_initial_satisfaction(user_satisfaction_query)

            if agent.agent_status == AgentState.COMPLETE:
                print("\nGreat! Have a nice day!")
                break

            agent.process_probing()

            print("\n Enter any of the following commands or enter a new search query: 'quit', 'exit', 'q' to exit")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()