We want to make a coding agent which can solve simple bugs.
We will use Groq LLM for this. In past other files, we used the same.

The LLM will have some tools which help in solving the bug.
One tool can be search files which lists path of files related to the bug as per the LLM.
We need a search in file tool which can give line numbers related to the bug.
We need a replace which allows replacing a line with another line.

To test this, I want to test this myself. Prepare a simple .cpp file and write boilerplate code in it. Do not introduce any bugs now. I'll introduce the bug and test it myself.

I want to give the bug in simple english in cli and the LLM and the tools should solve it.
Make the system without LangGraph and keep it simple. 
Also there will be a max retry of three times. If the LLM can't solve the bug inside this limit, it should print the message saying that it cannot solve the bug. 

Also there should be clear print statements saying which tool was called at which step. We want to understand the flow completely.
As soon as I change the cpp file and run the agent it should ask me my bug. After I give my bug, it should begin solving it.

Do not write any testcases for now.
If anything is unclear, ask me.