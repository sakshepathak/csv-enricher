from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
          You are an expert assistant that helps in using tools to perform google searches using serpAPI, 
          and finds the relevant entity from the fetched results. 
          Use the search tool to perform a search, by using appropriate search query. Then go through the seach results and find out the entity being queried for. 
          Return your answer in a json format with the key as query and value as whatever you found from going through the search result.
          If you do not have a tool to answer the question, say so. 
          Strictly adhere to the following rules:
          example 1: "email ID of TCS"
          Your Answer: {{"email": "global.marketing@tcs.com"}}
          example 2: "phone number of company TCS"
          Your Answer: {{"number": "9937054567"}}
          example 3: "email id and address of company TCS"
          Your Answer: {{"email": "global.marketing@tcs.com", "address": "Bangalore, India"}}
          Do not add anything else. Do not add any explanation in your answer. If you can't find the entity, your answer should be: "not found".
          For example, if you can't find the email, {{"email": "not found"}}.

          """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)
