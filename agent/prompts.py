class Prompt:
  def __init__(self):
    pass

  def analyze_relevance_prompt(self, user_input, question):
       return f"""
       You are an Analytics Query Assistant. Based on the knowledge you have, you provided an answer
       to the user's query. The user is not satisified with results you provided. You have asked probing questions to the user
       to get more information. You need to check if the user's response to the probing question is relevant
       with respect to the knowledge base: {self.kb_summary()}.

       The probing question is: "{question}". The user's response is: "{user_input}".
       If the answer is relevant tothe probing question, make the question and response into a meaningful query.
       Example: If the probing question id "Do you want to know anything specific in certain timeframes?" and the user's response is "no",
       give a relevant_query as "with no specific timeframes".
       If the answer is not relevant to the probing question, give a relevant_query as "not relevant".
       Respond in a json format in the following way: {{"relevance": "1/0", "relevant_query": "response transformed to meaningful query"}}.
       The value of "relevance" should be 1 if the user's response is relevant to the probing question and 0 if the user's response is not relevant to the probing question.
       Stick to the response format.
       """


  def kb_summary(self):
    return """
        Core Parameters

        Metric Type

        win/loss, sales, conversion, MRR, growth, expansion,CAC, lead cost, acquisition,adoption, engagement, retention


        Business Context

        enterprise, SMB, consumer,global, EMEA, North America, LATAM,direct, partner, digital, tech, finance, healthcare, retail


        Time Context

        historical, current, predictive, specific timeframe, comparative, trend, seasonal, point-in-time

        """