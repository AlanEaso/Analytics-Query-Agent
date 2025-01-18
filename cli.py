from agent.csm_analytics_agent import CSMAnalytsgent

def main():
    agent = CSMAnalytsgent()
    print("CSM Analytics Query Agent")
    print("------------------------")
    print("Enter your analytics report request (or 'quit' to exit):")

    while True:
        query = input("\nQuery: ").strip()
        if query in ['quit', 'exit', 'q']:
            break

        agent.process_query(query, top_k=1)

        user_satisfaction_response = input("\n Are you satisfied with the results? (y/n): ").strip()
        if user_satisfaction_response.lower() == 'n':
            agent.set_probing_state()
    
        agent.process_probing()

        print("\n Enter any of the following commands or enter a new search query: 'quit', 'exit', 'q' to exit")

if __name__ == "__main__":
    main()