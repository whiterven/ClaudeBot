import streamlit as st
import anthropic

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Chatbot with Claude", page_icon=":robot_face:")

# Sidebar
with st.sidebar:
    st.title('Chatbot with Claude')
    st.markdown('''
    ## About
    This app is an AI chatbot powered by Claude from Anthropic.
    
    It maintains chat history and allows for continuous conversation.
    ''')
    st.write('Made with ❤️ by Raven')

# Main chat interface
st.header("Chat with Claude")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message:"):
    # Initialize Anthropic client
    client = anthropic.Anthropic()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            with st.spinner("Thinking..."):
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4000,  # Increased from 1000 to 4000
                    temperature=0,
                    messages=st.session_state.messages
                )
            full_response = response.content[0].text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"An error occurred: {str(e)}. Please check your API key and try again.")

# Clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []
