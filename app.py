import json
from google import genai
from google.genai import types
import streamlit as st

from twilio.rest import Client

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]
TWILIO_CONTENT_SID = st.secrets["TWILIO_CONTENT_SID"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


@st.cache_resource
def get_twilio_client():
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)



twilio_client = get_twilio_client()
gemini_client = get_gemini_client()
MODEL_NAME = "gemini-3.6-flash"

def clean_whatsapp_text(text):
    if not text:
        return "No nutrition summary available."
    text = " ".join(text.split())  # collapse whitespace/newlines
    return text[:1500] + "..." if len(text) > 1500 else text


def send_whatsapp_message(to_number, user_name, summary):
    try:
        content_variables = json.dumps(
            {"1": user_name, "2": clean_whatsapp_text(summary)},
            ensure_ascii=False,
        )
        message = twilio_client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
            to=f"whatsapp:{to_number}",
            content_sid=TWILIO_CONTENT_SID,
            content_variables=content_variables,
        )
        return True, message.sid
    except Exception as error:
        return False, str(error)


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])
        elif message["kind"] == "video":
            st.video(message["content"])
        else:
            st.warning(f"Unknown message kind: {message['kind']}")


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])
def ask_gemini(contents):
    response = st.session_state.chat.send_message(contents)
    return response.text


def send_whatsapp(phone_number, name, summary):
    print(f"Sending WhatsApp to {name} ({phone_number}):\n{summary}")
    return True, "Sent successfully"


# step 1: onboarding (username and phone)
if "onboarded" not in st.session_state:
    st.title("MacroSnap 🥗")
    st.caption("Snap it. Track it. Text yourself the result: ")

    with st.form("onboarding_form"):
        name = st.text_input("Name")
        whatsapp_number = st.text_input(
            "whatsapp number (with country code)",
            placeholder="+91XXXXXXXXXX",
            help="This is the number Macroscope will text your summary to.",
        )

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name.strip() or not whatsapp_number.strip():
                st.warning("Please fill in both your name and whatsapp number.")
            else:
                st.session_state.name = name.strip()
                st.session_state.whatsapp_number = whatsapp_number.strip()
                # active my ai
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()

    st.stop()

# create a chat interface
header_col, button_col = st.columns([3, 1], vertical_alignment="center")

with header_col:
    st.title("MacroSnap 🥗")

with button_col:
    send_disabled = len(st.session_state.messages) <= 1
    if st.button(
        "Send to whatsapp", disabled=send_disabled, use_container_width=True
    ):
        with st.spinner("Summarizing your day..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
        success, info = send_whatsapp(
            st.session_state.whatsapp_number, st.session_state.name, summary
        )
        if success:
            st.success(
                f"Summary sent to {st.session_state.whatsapp_number} successfully!"
            )
        else:
            st.error(f"Failed to send summary: {info}")

st.caption(
    f"Logged in as {st.session_state.name} - updates go to {st.session_state.whatsapp_number}"
)

if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )
else:
    for message in st.session_state.messages:
        render_message(message)

# step 2: chat input (line 100 onwards)
prompt = st.chat_input(
    "Tell me what you ate or upload a food photo...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if prompt:
    if prompt.text:
        add_message("user", "text", prompt.text)

    contents = []
    if prompt.files:
        for uploaded_file in prompt.files:
            image_bytes = uploaded_file.read()
            add_message("user", "image", image_bytes)
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes, mime_type=uploaded_file.type
                )
            )

    if prompt.text:
        contents.append(prompt.text)

    if contents:
        with st.spinner("Analyzing your meal..."):
            reply = ask_gemini(contents)
        add_message("assistant", "text", reply)
        st.rerun()