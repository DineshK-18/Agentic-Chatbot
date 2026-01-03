# app/agents/db_query_agent.py
from langchain_community.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_community.llms import OpenAI
from typing import Any


class DatabaseQueryAgent:
    def __init__(self, database_uri: str):
        self.db = SQLDatabase.from_uri(database_uri)
        self.llm = OpenAI(temperature=0)
        self.chain = create_sql_query_chain(self.llm, self.db)
    
    def natural_language_query(self, question: str) -> str:
        # Convert NL to SQL
        sql_query = self.chain.invoke({"question": question})
        
        # Execute query
        result = self.db.run(sql_query)
        
        # Format response naturally
        return self._format_response(result, question)
    
    def _format_response(self, result: Any, question: str) -> str:
        # Convert SQL results to natural language
        if "tomorrow" in question.lower():
            return f"There are {len(result)} meetings scheduled for tomorrow."
        elif "today" in question.lower():
            return f"You have {len(result)} meetings today."
        return f"Query result: {result}"