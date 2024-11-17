from langchain.agents import AgentExecutor, create_openai_tools_agent

def csv_enricher_agent(llm, tools, prompt):
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True, verbose=True)
    return agent_executor