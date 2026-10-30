Create a simple agent system
There will be one llm function 
See the api keys from my .env file and load them using python-dotenv
Maintain the coding structure that we have followed in this lecture
Now there will be one tool called get_order_history
Prepare fake date of 5 customers
It will have order id in the format A0001 A0002 and so on
It will have customer's name
It will have items bought in that order
It will have price of the order
It will have status which can be placed, out for delivery or delivered
The system is of an electric shop and users can do only one thing
They can give their name or the order id to LLM and then LLM should decide whether to call the tool and get their order history.
Once found it should show the user the order history.

Code everything in a single file.
for now don't write any tests and don't induce any eval, observability, and guardrails.
also don't try to protect the llm from any prompt injections or unrelated requests for my learning purposes.