I am building a restaurant order management ai agent system using LangGraph.

I will explain you very clearly what i want and what is the architecture. I will also explain you the nodes the state and the edges. In the end I will give you test cases to simulate and to tell me whether they pass or not.

The rough plan is: 
There will be a user. When the code runs, the user will give an order. This will be taken as an input which I will type. This order should go to the LLM. The order as of now should contain dish and the required quantity. For simplicity purpose for now, we will limit the order to one particular dish and whatever quantity the user wants. The LLM will have to extract the order name and the quantity from the user input. If the user input is unrelated to food ordering, the LLM should not process that and tell the user that it is an ai agent oof food ordering and not a general purpose llm.

Once the llm has ordered dish and quantity
It will send that to a node called order_confirm. 
The task of this order_confirm node is to look at the menu (I will tell you the menu later in this prompt). 
This node will decide one of the 3 cases: 
the order is available
the order is partially available which means the quantity is not sufficient
the order is not available at all (dish being not in the menu or 0 quantity available). 
It will put this in the status of the state (I will tell u the exact content of the LangGraph state as well)

Once the llm received this 
If the status is confirmed (fully available) it should call another node called cook. 
If the status is partial or not available, it should again prompt the user to decide the user can either place a new order or can confirm if he wants to go ahead with the partial order.

This order retries will be limited to 3 attempts meaning if after 3 attempt the user is not satisfied, the system will come the the END node

Now when the cook node is called there can be 2 cases: 
Either the cook is done then the status will be 'Ready' 
and if the cook fails (we can use a prob function). 
Give 40% chances of fail and 60% chance of success.

If the cook fails there should be 1 more attempt allowed for cook to succeed. If the cook fails even after these then the llm should issue a apology to the user and come to END state

If the cook succeeds, the status will be READY and the next node will be called which is serve 
similar to cook this also has 2 cases serve pass or serve fail. 
This also has 2 retry attempts 
if the serve fails 2 times then the llm should issue a apology to the user and come to END state.

If the serve succeeds the status should become complete the llm should issue a message to the user saying your order is complete 
if serve fails then cook should be called one more time to retry. 
Note that if cook has exhausted its retry attempts then it should not cook again and llm should issue an apology and come to end state.

Now the state of LangGraph.

there should be a annotated message be llm and user.

there should be order details
dish name as str 
required quantity as int 
available quantity as string 
order_conform will write the available quantity by reading the menu 
the llm should get to know the order confirm status by reading the state 
if a dish is not available in the menu then order_confirm should write 0 as available quantity

then there should be status 
each node will update the status as specified in the above rules 
then order retry attempts which are 3 
cook retry attempts which are 2 
serve retry attempts which are 2 
each time a failure happens and a node is retrying it should decrement the counter 
if any retry counter becomes 0 it means it is over. llm should understand whether it has to give a retry or issue apology by reading this counter 
in the end there should be final result whether the order was completed or not.

Write the code and ask if there are any open questions from your side then ask I will give you some test scenarios to test later on

TC1 
a user ask an unrelated question 
then he places a order which is partial then he rejects the partial and wants to order again 
again he orders a dish which is not available expected. END due to order retry

TC2 
user places a order which can be available 
cook makes it fails once 
cooks again success 
serve fails once 
cook retries success 
serve does success 
overall success

TC3 
user orders partial 
does not want partial 
orders again 
fully available cooks makes it fails 
makes again success serve fails 
cook retries success serve fails again 
cook does not retry due to cook retry exhaust 
overall FAIL