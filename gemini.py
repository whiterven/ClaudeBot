import streamlit as st
import google.generativeai as genai

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

st.set_page_config(page_title="Chat with Gemini", page_icon=":robot_face:")

# Sidebar
with st.sidebar:
    st.title('Chatbot with Gemini')
    st.markdown('''
    ## About
    This app is an AI chatbot powered by Gemini from Google.
    
    It maintains chat history and allows for continuous conversation.
    ''')
    st.write('Made with ❤️ by Raven')
    
    # API Key input
    st.markdown("### Enter your Google AI API Key")
    api_key_input = st.text_input("API Key", type="password", key="api_key_input")
    if api_key_input:
        st.session_state.api_key = api_key_input
    st.markdown("**Note:** We do not store your API key. It's used only for this session and is completely safe to enter.")

# Main chat interface
st.header("Chat with Gemini")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message:"):
    if not st.session_state.api_key:
        st.error("Please enter your Google AI API key in the sidebar to use the chatbot.")
    else:
        # Initialize Gemini
        genai.configure(api_key=st.session_state.api_key)
        
        # Create the model if it doesn't exist
        if not st.session_state.chat_session:
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
            }
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config,
            )
            st.session_state.chat_session = model.start_chat(history=[])
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                with st.spinner("Thinking..."):
                    response = st.session_state.chat_session.send_message(prompt)
                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}. Please check your API key and try again.")

# Clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.chat_session = None
