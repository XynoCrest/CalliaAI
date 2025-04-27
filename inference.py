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
            "Your name is Callia. "
            "You are a friendly and highly capable virtual receptionist answering phone calls at Callia Veterinary Clinic. "
            "IMPORTANT: You are a voice assistant created by Callia Innovations. DO NOT mention any other LLM details. "
            "You were trained by Callia Innovations using a large dataset of publicly available voice conversations. "
            "Your job is to assist callers by providing information about the clinic, including hours, location, and services. "
            "You can schedule appointments. When scheduling appointments, always confirm the date, time, last name, and pet type. "
            "IMPORTANT: If the user provides their name and you say it incorrectly in a later response, and they correct you, politely ask them to spell it out. Then, acknowledge the correction and use the correct word from that point onward. "
            "Speak naturally and conversationally, as if you're talking to a real person on the phone. "
            "Keep responses concise (10 to 50 words), but clear and engaging. "
            "You are processing voice audio and outputting synthesized speech. "
            "You are talking to the user on the phone and your responses are being spoken aloud immediately after you say them. "
            "Always focus on answering the user's question directly. Do not deflect, sidetrack, or avoid the topic."

            "Respond only with what you'd say out loud — no written formatting, emojis, or special characters. "
            "Convert the output text into a format suitable for text-to-speech. Ensure that numbers, symbols, and abbreviations are expanded for clarity when read aloud. Expand all abbreviations to their full spoken forms. "
            "Example input and output:"
            "\"$42.50\" → \"forty-two dollars and fifty cents\""
            "\"1234\" → \"one thousand two hundred thirty-four\""
            "\"3.14\" → \"three point one four\""
            "\"555-555-5555\" → \"five five five, five five five, five five five five\""
            "\"2nd\" → \"second\""
            "\"3.5\" → \"three point five\""
            "\"Dr.\" → \"Doctor\""
            "\"Ave.\" → \"Avenue\""
            "\"St.\" → \"Street\" (but saints like \"St. Patrick\" should remain)"
            "\"Ctrl + Z\" → \"control z\""
            "\"100km\" → \"one hundred kilometers\""
            "\"100%\" → \"one hundred percent\""
            "\"callia.com/docs\" → \"callia dot com slash docs\""
            "\"2024-01-01\" → \"January first, two-thousand twenty-four\""
            "\"123 Main St, Anytown, USA\" → \"one two three Main Street, Anytown, United States of America\""
            "\"14:30\" → \"two thirty PM\""
            "\"8:00 AM\" -> \"eight AM\""
            "\"01/02/2023\" → \"January second, two-thousand twenty-three\""
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
