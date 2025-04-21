import re
from key_retriever import get_groq_key
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

model = ChatGroq(model = "gemma2-9b-it", groq_api_key = get_groq_key())

# -----------------------------
# Define the Prompt Template
# -----------------------------
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are Callia."
            "You are a friendly and helpful virtual receptionist answering phone calls at Callia Veterinary Clinic."
            "You were created by Callia Innovations. Do not mention any language model details."
            "Your job is to assist callers by providing information about the clinic, including hours, location, and services."
            "You can schedule appointments. Always confirm the date, time, last name, and pet type politely."
            "Speak naturally and conversationally, as if you're talking to a real person on the phone."
            "Keep responses concise (10 to 50 words), but clear and engaging."
            "Respond only with what you'd say out loud — no written formatting, emojis, or special characters."
            "Imagine your responses will be spoken aloud immediately after you say them."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# -----------------------------
# Define the LangGraph 
# -----------------------------
workflow = StateGraph(state_schema=MessagesState)

# Funtion to be executed by Graph Node
def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}

# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Saves graph state after each call
memory = MemorySaver()

# Compile the graph into an app
app = workflow.compile(checkpointer=memory)

# --------------------------------------
# Creating a config and running the app
# --------------------------------------
def brain(input: str, phone="4031234567"):
    config = {"configurable": {"thread_id": {phone}}}

    input_messages = [HumanMessage(input)]
    response = app.invoke({"messages": input_messages}, config)
    output = clean_output(response["messages"][-1].content)
    return output

def clean_output(output):
    clean_output = re.sub(r'[^\w\s,\.!?\'"-]', '', output)  # This removes anything that's not a word, space, or punctuation
    return clean_output.replace('\n', '').replace('\r', '').replace('  ', ' ')
