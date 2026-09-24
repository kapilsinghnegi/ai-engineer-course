I want to make a multi agent system
First I want to make a single agent system
It will have one LLM (Groq)
It will have two tools
One: Web Search using Tavily
You'll find all the API keys in .env file 
Second: a python calculator

there will be one ask llm function
llm will decide which tools to use and how many times
there will be a max attempts of 5

then we will convert to multi agent system without LangGraph

In the multi agent system, there will be three ask llm functions:
first will be of manger llm, its only job is to decide which helper llm to use
second will be ask_search_llm which has access to only the search tool
third will be ask_calculate_llm which only has access to calculate tool

The role of each ask llm can be given by a system prompt
manager llm will also have a notes file to keep track of the responses by the helper llm

Finally, we will have token usage in this also 
In the end, we will compare both the systems and see which used more tokens
For test, prepare a little complex query which involves search and calculator (maybe more than once)

If you have any doubts then ask