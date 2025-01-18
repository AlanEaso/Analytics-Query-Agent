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

        results = agent.search_reports(query, top_k=1)
        for report, score in results:
            print(f"Title: {report.title}")
            print(f"Description: {report.description}")
            print(f"Metrics: {report.metrics}")
            print(f"Dimensions: {report.dimensions}")
            print(f"Score: {score}")
            print()

        print("\n Enter any of the following commands: 'quit', 'exit', 'q' to exit")

if __name__ == "__main__":
    main()