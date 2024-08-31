import streamlit as st
import google.generativeai as genai
from langchain_community.utilities import GoogleSerperAPIWrapper

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
    
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "response_mime_type": "text/plain",
}

st.set_page_config(page_title="Chat with Gemini", page_icon=":robot_face:")

# Sidebar
with st.sidebar:
    st.title('Chatbot with Gemini')
    st.markdown('''
    ## About
    This app is an AI chatbot powered by Gemini from Google.
    It maintains chat history and allows for continuous conversation.
    It also uses Serper.dev API for web searches.
    ''')
    st.write('Made with ❤️ by Raven')
    
    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat_session = None

# Main chat interface
st.header("Chat with Gemini")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message:"):
    # Get API keys from secrets
    google_api_key = st.secrets["GOOGLE_API_KEY"]
    serper_api_key = st.secrets["SERPER_API_KEY"]
    
    # Initialize Gemini and Serper
    genai.configure(api_key=google_api_key)
    search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
    
    # Create the model if it doesn't exist
    if not st.session_state.chat_session:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config=generation_config,
            system_instruction="You are a helpful AI assistant. For casual greetings and conversations, respond naturally without searching the web. For other queries, use the provided web search results to give accurate and up-to-date information.",
            tools='code_execution',
            safety_settings={
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
        )
        st.session_state.chat_session = model.start_chat(history=[])
    
    # Handle text input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            with st.spinner("Thinking..."):
                # Check if the prompt is a casual greeting
                casual_greetings = ["hi", "hello", "how are you", "hey", "what's up", "whats up"]
                if prompt.lower() in casual_greetings:
                    # For casual greetings, respond without web search
                    response = st.session_state.chat_session.send_message(prompt)
                else:
                    # For other queries, perform web search
                    search_results = search.run(prompt)
                    combined_prompt = f"{prompt}\n\nUse this relevant information from a web search:\n{search_results}"
                    response = st.session_state.chat_session.send_message(combined_prompt)
                
                full_response = response.text
                if "I do not have access to real time information" in full_response.lower():
                    # If the response indicates lack of real-time info, perform a web search
                    search_results = search.run(prompt)
                    full_response = f"Based on the latest information from the web:\n\n{search_results}"
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"An error occurred: {str(e)}. Please check your API keys in the secrets.toml file and try again.")