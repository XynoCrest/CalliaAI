import re
from key_retriever import get_groq_key
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

model = ChatGroq(model = "gemma2-9b-it", groq_api_key = get_groq_key())

# -----------------------------
# Define the Prompt Template
# -----------------------------
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Your name is Callia. "
            "You are a friendly and highly capable virtual receptionist answering phone calls for Callia Veterinary Clinic. "
            "IMPORTANT: You are a voice assistant created by Callia Innovations. Do not mention any LLMs, models, or technical details beyond this. "
            "You were trained by Callia Innovations using a large dataset of publicly available voice conversations. "
            
            "Your role is to assist callers by providing clear information about the clinic, including Hours of operation, location, and services offered. "
            "IMPORTANT: Do not provide any medical advice. Politely inform the caller that you cannot give medical guidance and suggest they contact a qualified veterinarian or visit the clinic for assistance. "
            
            "Clinic Details: "
            "Address: Twenty-five-hundred University Drive North West, Calgary, Alberta, T-Two-N One-N-Four. "
            "Hours: Monday to Friday, 9 AM to 6 PM. Closed on weekends (Saturday and Sunday). "
            "Services: Wide range of services including are offered including wellness exams, vaccinations, dental care, surgery, and emergency care. "
            "The current time in Calgary Alberta (Mountain Daylight Time) is: {current_time}."
            
            "Appointment Scheduling Instructions: "
            "You may schedule appointments. "
            "Always confirm the appointment date, time, caller's name, and pet type. "
            "If you mispronounce a caller's name and they correct you, politely ask them to spell it. Acknowledge the correction and use the correct pronunciation thereafter. "
            
            "Speaking Style: "
            "Speak naturally and conversationally, as if you're talking to a real person on the phone. "
            "Keep responses concise (10 to 50 words), but clear and engaging. "
            "You are processing voice audio and outputting synthesized speech. "
            "You are talking to the user on the phone and your responses are being spoken aloud immediately after you say them. "
            "Always focus on answering the user's question directly. Do not deflect, sidetrack, or avoid the topic. "
            "Respond only with what you'd say out loud — no written formatting, emojis, or special characters. "
            
            "Formatting Rules: "
            "Convert the output text into a format suitable for text-to-speech. "
            "Ensure that numbers, symbols, and abbreviations are expanded for clarity when read aloud. Expand all abbreviations to their full spoken forms. "
            
            "Example input and output: "
            "\"$42.50\" → \"forty-two dollars and fifty cents\"; "
            "\"1234\" → \"one thousand two hundred thirty-four\"; "
            "\"3.14\" → \"three point one four\"; "
            "\"555-555-5555\" → \"five five five, five five five, five five five five\"; "
            "\"2nd\" → \"second\"; "
            "\"3.5\" → \"three point five\"; "
            "\"Dr.\" → \"Doctor\"; "
            "\"Ave.\" → \"Avenue\"; "
            "\"St.\" → \"Street\" (but saints like \"St. Patrick\" should remain); "
            "\"Ctrl + Z\" → \"control z\"; "
            "\"100km\" → \"one hundred kilometers\"; "
            "\"100%\" → \"one hundred percent\"; "
            "\"callia.com/docs\" → \"callia dot com slash docs\"; "
            "\"2024-01-01\" → \"January first, two-thousand twenty-four\"; "
            "\"123 Main St, Anytown, USA\" → \"one two three Main Street, Anytown, United States of America\"; "
            "\"14:30\" → \"two thirty PM\"; "
            "\"8:00 AM\" -> \"eight AM\"; "
            "\"01/02/2023\" → \"January second, two-thousand twenty-five\"; "
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
    # Get current time as a spoken string
    # e.g., "2:45 PM on Wednesday, April 30, 2025"
    now = datetime.now()
    current_time_str = now.strftime("%#I:%M %p on %A, %B %#d, %Y")

    # Inject variable into the prompt
    prompt = prompt_template.invoke(
        {
            "current_time": current_time_str,
            "messages": state["messages"]
        }
    )

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
    # Checks mentions of Ambigious time period within the input, and replaces them with absolute reference
    if re.search(
            r'\b(this|next)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend)\b'
            r'|\bin\s+\d+\s+days?\b'
            r'|\b\d+\s+days?\s+from\s+now\b'
            r'|\btoday\b'
            r'|\btomorrow\b',
            input,
            re.IGNORECASE
        ):
        input = resolve_relative_day(input)

    # Replaces Name Spelled out like S-A-H-A to SAHA
    input = re.sub(r'\b((?:[A-Z]-)+[A-Z])\b', lambda m: m.group(0).replace('-', ''), input)

    config = {"configurable": {"thread_id": {phone}}}
    input_messages = [HumanMessage(input)]
    response = app.invoke({"messages": input_messages}, config)
    output = clean_output(response["messages"][-1].content)
    return output


# ------------------------------------------
# Helper Functions to Manage Word Structures
# ------------------------------------------
def clean_output(output):
    clean_output = re.sub(r'[^\w\s,\.!?\'"-]', '', output)  # This removes anything that's not a word, space, or punctuation
    return clean_output.replace('\n', '').replace('\r', '').replace('  ', ' ')


# Resolves ambigious date references to absolute references
# e.g. - "Can I book an appointment for this Saturday?" 
# to - "Can I book an appointment for Saturday, May 3, 2025?"
# Required to make sure the AI doesn't get these dates wrong
def resolve_relative_day(input_text):
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    now = datetime.now(ZoneInfo("America/Edmonton"))
    today_weekday = now.weekday()

    def get_weekday_offset(keyword, weekday_str):
        target = weekdays[weekday_str]
        if keyword == "this":
            days_ahead = (target - today_weekday + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
        elif keyword == "next":
            days_ahead = (target - today_weekday + 7) % 7 + 7
        else:
            days_ahead = 0
        return now + timedelta(days=days_ahead)

    def get_weekend_offset(keyword):
        base = now + timedelta(days=((5 - today_weekday + 7) % 7))  # Saturday
        if keyword == "next":
            base += timedelta(days=7)
        return base

    def get_sunday_offset(weekend_date):
        return weekend_date + timedelta(days=1)

    def format_date(dt):
        return dt.strftime("%A, %B %#d, %Y") if hasattr(dt, 'strftime') else str(dt)

    def replace_weekday(match):
        keyword = match.group(1).lower()
        weekday = match.group(2).lower()
        date = get_weekday_offset(keyword, weekday)
        return f"{match.group(0)} ({format_date(date)})"

    def replace_weekend(match):
        keyword = match.group(1).lower()
        saturday = get_weekend_offset(keyword)
        sunday = get_sunday_offset(saturday)
        return f"{match.group(0)} ({format_date(saturday)} or {format_date(sunday)})"

    def replace_days(match):
        days = int(match.group(1))
        date = now + timedelta(days=days)
        return f"{match.group(0)} ({format_date(date)})"

    def replace_today(match):
        return f"{match.group(0)} ({format_date(now)})"

    def replace_tomorrow(match):
        tomorrow = now + timedelta(days=1)
        return f"{match.group(0)} ({format_date(tomorrow)})"

    updated_text = input_text

    # Replace "today"
    updated_text = re.sub(r'\btoday\b', replace_today, updated_text, flags=re.IGNORECASE)

    # Replace "tomorrow"
    updated_text = re.sub(r'\btomorrow\b', replace_tomorrow, updated_text, flags=re.IGNORECASE)

    # Replace "this Monday", "next Friday"
    updated_text = re.sub(
        r'\b(this|next)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        replace_weekday,
        updated_text,
        flags=re.IGNORECASE
    )

    # Replace "this weekend", "next weekend"
    updated_text = re.sub(
        r'\b(this|next)\s+weekend\b',
        replace_weekend,
        updated_text,
        flags=re.IGNORECASE
    )

    # Replace "in 2 days"
    updated_text = re.sub(
        r'\bin\s+(\d+)\s+days?\b',
        replace_days,
        updated_text,
        flags=re.IGNORECASE
    )

    # Replace "2 days from now"
    updated_text = re.sub(
        r'\b(\d+)\s+days?\s+from\s+now\b',
        replace_days,
        updated_text,
        flags=re.IGNORECASE
    )

    return updated_text

