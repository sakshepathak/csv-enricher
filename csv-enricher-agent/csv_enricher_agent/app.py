import streamlit as st
import pandas as pd
from backend.google_api import authenticate_gspread, load_google_sheet, write_to_google_sheet
from backend.agent.csv_enricher_agent import csv_enricher_agent
from backend.agent.prompts.prompt import prompt
from backend.agent.tools.serp_data_fetcher import search
from langchain_openai import ChatOpenAI
from typing import Any
from string import Template
from dotenv import load_dotenv
import os 
import io

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@st.cache_data
def process_llm_queries(queries, _llm, _agent_executor):
    """
    Process the queries using the LLM and cache the results.

    Args:
        queries (list): List of queries to process.
        _llm (ChatOpenAI): The LLM instance.
        _agent_executor: The agent executor.

    Returns:
        tuple: Results and search_results_list.
    """
    results = []
    search_results_list = []

    for query in queries:
        result = _agent_executor.invoke({"input": f"{query}"})
        results.append(result["output"])

        # Extract only the related_questions and organic_results from the intermediate steps if available
        intermediate_steps = result.get("intermediate_steps", [])
        if intermediate_steps and isinstance(intermediate_steps, list):
            last_step = intermediate_steps[-1]
            if isinstance(last_step, tuple) and len(last_step) > 1:
                tool_output = last_step[1]
                related_questions = tool_output.get("related_questions", [])
                organic_results = tool_output.get("organic_results", [])
                search_result = {
                    "related_questions": related_questions,
                    "organic_results": organic_results,
                }
            else:
                search_result = {}
        else:
            search_result = {}
        search_results_list.append(search_result)

    return results, search_results_list

def main() -> None:
    st.title("Spreadsheet Enricher")

    st.sidebar.header("Upload Options")
    option: str = st.sidebar.radio("Choose an option", ["Upload CSV", "Google Sheets Link"])
    df: pd.DataFrame = pd.DataFrame()
    client = None
    sheet_url = None

    if option == "Upload CSV":
        uploaded_file: Any = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("### Data Preview")
            st.dataframe(df.head(10))

    elif option == "Google Sheets Link":
        sheet_url = st.text_input("Enter Google Sheets URL")
        creds_file: Any = st.file_uploader("Upload Google Sheets credentials JSON", type=["json"])

        if sheet_url and creds_file:
            try:
                client = authenticate_gspread(creds_file)
                df = load_google_sheet(client, sheet_url)
                st.write("### Data Preview")
                st.dataframe(df.head(10))
            except Exception as e:
                st.error(f"Error: {e}")

    if not df.empty:
        selected_columns: list[str] = st.multiselect(
            "Select one or more columns to work with", options=df.columns.tolist()
        )
        if selected_columns:
            st.write("### Selected Columns")
            st.dataframe(df[selected_columns].head(10))

            user_query: str = st.text_input(
                "Ask me to do something with your data",
                placeholder="Example: What is the email ID for {company}",
            )

            if user_query:
                try:
                    main_column = selected_columns[0]
                    tmpl = Template(user_query)
                    queries = [tmpl.substitute({main_column: value}) for value in df[main_column]]
                    queries = queries[:6]
                    tools = [search]
                    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
                    agent_executor = csv_enricher_agent(llm=llm, tools=tools, prompt=prompt)

                    # Process the queries and cache the results
                    results, search_results_list = process_llm_queries(queries, llm, agent_executor)

                    enriched_data = []
                    for res in results:
                        try:
                            enriched_data.append(eval(res))  # Convert string to dict
                        except:
                            enriched_data.append({})  # Handle unexpected formats

                    # Normalize the results into a DataFrame
                    enriched_df = pd.DataFrame(enriched_data)

                    # Add search results as a new column
                    enriched_df["search_results"] = search_results_list

                    # Concatenate with the original DataFrame
                    df = pd.concat([df, enriched_df], axis=1)

                    st.write("### Enriched Data")
                    st.dataframe(df.head(10))

                    # Save changes to Google Sheet
                    if sheet_url and client:
                        if st.button("Save Changes to Google Sheet"):
                            try:
                                write_to_google_sheet(client, sheet_url, df)
                                st.success("Enriched data has been successfully saved to the Google Sheet!")
                                st.markdown(f"[Open Google Sheet]({sheet_url})", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Failed to write to Google Sheet: {e}")

                    # Save changes to CSV file
                    if option == "Upload CSV":
                        csv_buffer = io.StringIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()

                        st.download_button(
                            label="Download Enriched File",
                            data=csv_data,
                            file_name="enriched_data.csv",
                            mime="text/csv",
                        )

                except KeyError as e:
                    st.error(f"Error: Missing placeholder in template. Ensure {e} exists in your prompt.")

if __name__ == "__main__":
    main()
