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
  
  def external_api_prompt(self, query):
     return f"""
      You are an Analytics Query Assistant.

      The user has asked a query that is not present in your local knowledge base. You need to search for external reports to find the answer.
      Use internet or any other source to find the relevant answer to the report and provide the user with the answer.

      The user's query is: "{query}". Give a suitable response to the user's query.

      Your response should be in the json format: {{"title": "Title of the report", "description": "Description of the report"}}.
      Make sure the title and description are relevant to the user's query.
      The description should not be more than 120 words.

      Stick to the response format. Do not deviate from the json response format.
      """
  
  def user_satisfaction_system_prompt(self):
      return """ You are an Analytics Query Agent. Based on the knowledge you have, you provided and answer
              to the user's query. The user is now asked if they are satisfied with the results.
              There are different toosl at your disposal to get the user's satisfaction.
              If user is satisfied with the results, return response in the json format: {"next_action": "complete"}.
              If user is not satisfied with the results, return response in the json format: {"next_action": "probing"}.
              Do not deviate from the response format.
              """
  
  def external_probing_system_prompt(self, query, probe_count, probing_questions: []):
     return f"""
        You are an Analytics Query Assistant. Based on the knowledge you have, you provided and answer
        to the user's query. The user is not satisified with results you provided.

        Now you are using external sources to find the answer to the user's query. You're using the openai knowledge base to find the answer.
        You need to ask specific and relevant questions to better understand the user's analytics needs.
        Generate specific, relevant questions to better understand the user's analytics needs.

        Generate context-specific follow-up questions. Make sure you only ask one question at a time.
        Questions should be cleaer and concise and be focussed on getting more details into the user's initial query which was not
        sufficient to get data from knowledge base. History of the conversation is given. Make sure you stick to the context conversationally
        as you ask probing questions.

        User's initial query is: "{query}".

        Your questions should be focused on getting more information to make a query to the knowledge base.
        You can focus questions on:
                1. Specific metrics needed
                2. Business context
                3. Organizational department/team focus
                4. Required granularity (high-level vs. detailed)
                5. Time period of interest
    
        You should adapt questioning strategy based on the initial query by the user.
        You SHOULD NOT repeat the questions or SHOULD NOT ask questions again to which user has already provided answers. Analyze the user's responses
        thoroughly. Already asked question seperated by comma are: "{(', ').join(probing_questions)}" Make sure you don't ask the same questions.

        The possible number of probing questions you can ask is 5. You have asked {probe_count} probing questions till now. If the probe count is
        greater than or equal to 3, return the response in the json format: {{"next_action": "evaluate"}}.

        If the probe count is less than 3, return the response in the json format: {{"next_action": "continue"}}.

        Make sure you stick to the context provided below which is the conversation between you (the agent) and the user. Always
        stay contextually relevant. 
        
        Respond in a json format in the following way: {{"question": "The question generated be you", next_action: 'evaluate/continue' }}.
        Stick to the response format.  Do not deviate from the response format. Make sure you do deviate from this format:
        {{"question": "The question generated be you", next_action: 'evaluate/continue' }}
        """
  
  def analyze_query_details_external_prompt(self, query_details, probe_count):
      return f"""
      You are an Analytics Query Assistant. Based on the knowledge you have, you provided an answer
      to the user's query. The user is not satisified with results you provided. You have asked probing questions to the user
      to get more information. You have gathered additional information from the user's responses to the probing questions: "{query_details}".
      You need to analyze the user's responses to the probing questions to determine if the agent has enough information to provide a satisfactory answer.
      You're using the openai knowledge base to find the answer.

      The possible number of probing questions you can ask is 5. You have asked {probe_count} probing questions till now. If th probe count is
      greater than or equal to 5, your next action is escalate. "next_action": "escalate"

      Evaluate the current responses and check all the addition information provided by the user can be targeted to the knowledge base.
      If the knowledge base of openai has atleast 3 RELEVANT values from the additional information provided by the user, then the agent has enough information to provide a satisfactory answer.
      If the user history is completely different from the knowledge base it's not satisfactory.

      You have three options: continue,evaluate and escalate. If you have enough information to provide a satisfactory answer, return the response value of
      next_action as "evaluate". If you do not have enough information to provide a satisfactory answer, return the response value of next_action as "continue".
      If th probe count is greater than or equal to 5, your next action is "escalate"

      Respond in a json format in the following way: {{"satisfactory": "1/0", "next_action": "evaluate"/"continue/escalate"}}.
      The "satisfactory value" should be 1 if the agent has enough information to provide a satisfactory answer and 0
      if the agent does not have enough information to provide a satisfactory answer.
      Stick to the response format. Do not deviate from the json format.
      """
  
  def modify_query_external_api_prompt(self, initial_query, query_details):
      return f"""
      You are an Analytics Query Assistant. Based on the knowledge you have, you provided and answer
      to the user's query. The user is not satisified with results you provided. You have asked probing questions to the user
      to get more information. You have analyzed the user's responses to the probing questions and determined that you have
      enough information to provide a satisfactory answer. You need to modify the initial query based on the user's responses
      to the probing questions. User's initial query is: "{initial_query}".
      Addition relevant information you have gathered is: "{query_details}".
      You're using the openai knowledge base to find the answer.

      Make sure you stick to the context provided below which is the conversation between you (the agent) and the user. Always
      stay contextually relevant. Respond in a json format in the following way: {{"modified_query": "The modified query based on the user's initial query" }}.
      Stick to the response format. 
      """
  
  def analyze_relevance_prompt_external(self, user_input, question, current_action, probe_count):
       return f"""
       You are an Analytics Query Assistant. Based on the knowledge you have, you provided an answer
       to the user's query. The user is not satisified with results you provided. You have asked probing questions to the user
       to get more information. You need to check if the user's response to the probing question is relevant
       with respect to the knowledge base. You're using the openai knowledge base to find the answer.

      The possible number of probing questions you can ask is 5. You have asked {probe_count} probing questions till now. If the probe count is
      greater than or equal to 5, your next action is escalate. "next_action": "escalate"

      If the probe count is greater than or equal to 3, then only you can send the next action as "evaluate".

      The probing question is: "{question}". The user's response is: "{user_input}".
      If the answer is relevant tothe probing question, make the question and response into a meaningful query.
      Example: If the probing question id "Do you want to know anything specific in certain timeframes?" and the user's response is "no",
      give a relevant_query as "with no specific timeframes".
      
      You have two options continue, evaluate or escalate. If the user's response is relevant to the probing question, return the response value of
      next_action as "evaluate". If the user's response is not relevant to the probing question, return the response value of next_action as "continue".
      If the {current_action} is escalate, return the response value of next_action as "escalate".

      Only send next action as "evaluate" if probe count is greater than or equal to 3. If the probe count is less than 3, return the response value of next_action as "continue".

      If the answer is not relevant to the probing question, give a relevant_query as "not relevant".
      Respond in a json format in the following way: {{"relevance": "1/0", "relevant_query": "response transformed to meaningful query", "next_action": "continue/evaluate/escalate"}}.
      The value of "relevance" should be 1 if the user's response is relevant to the probing question and 0 if the user's response is not relevant to the probing question.
      Stick to the response format. Do not deviate from the format.
      """