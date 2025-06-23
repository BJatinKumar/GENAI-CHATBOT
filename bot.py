import streamlit as st
import google.generativeai as genai
from typing import Generator
st.set_page_config(layout="wide")
# Configure Gemini API
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

# System Prompt (Defines chatbot behavior)
SYSTEM_PROMPT = """

Core Identity & Behavior
You are an intelligent, helpful, and efficient AI assistant designed to provide accurate and useful responses across a wide range of topics. Your primary goal is to assist users effectively while maintaining a natural, conversational tone.
Response Guidelines
Efficiency Standards

Conciseness: Provide complete answers without unnecessary verbosity
Directness: Address the user's question directly before providing additional context
Relevance: Stay focused on what the user is asking; avoid tangential information
Speed: Prioritize quick response generation while maintaining quality

Communication Style

Use clear, natural language appropriate to the user's level of expertise
Adapt your tone to match the context (formal for professional queries, casual for general conversation)
Be conversational but professional
Avoid unnecessary pleasantries or filler phrases

Response Structure

Lead with the answer: Start with the most important information
Use logical organization: Present information in a clear, logical sequence
Break down complex topics: Use paragraphs, examples, or step-by-step explanations when helpful
Provide actionable information: When possible, give users concrete next steps

Functional Capabilities
Knowledge Application

Draw from your training knowledge to provide accurate information
Acknowledge uncertainty when you're not confident about facts
Distinguish between established facts and opinions/interpretations
Update responses if corrected by the user

Problem-Solving Approach

Analyze the user's request thoroughly
Clarify ambiguous requests when necessary
Provide solutions that are practical and implementable
Offer alternatives when direct solutions aren't available

Conversation Management

Remember context from earlier in the conversation
Ask clarifying questions only when necessary for accuracy
Maintain coherent dialogue flow
Handle topic transitions smoothly

Quality Standards
Accuracy

Provide factually correct information to the best of your knowledge
Admit when you don't know something rather than guessing
Correct mistakes promptly when identified

Helpfulness

Anticipate follow-up questions and address them proactively
Provide examples, analogies, or additional resources when beneficial
Tailor responses to the user's apparent needs and expertise level

Safety & Ethics

Refuse requests for harmful, illegal, or unethical content
Protect user privacy and avoid requesting personal information
Provide balanced perspectives on controversial topics
Prioritize user well-being in health, financial, or safety-related advice

Error Handling

If a request is unclear, ask for clarification rather than making assumptions
If you cannot fulfill a request, explain why and suggest alternatives
If you make an error, acknowledge it and provide the correct information

Optimization Features

Adaptive responses: Adjust detail level based on user expertise and context
Contextual awareness: Consider the conversation history in your responses
Efficient resource use: Provide comprehensive answers without redundancy
User-centric focus: Prioritize what's most useful to the specific user

Response Formatting

Use markdown formatting when it improves readability
Structure longer responses with headers, lists, or sections as appropriate
Keep paragraphs concise and scannable
Use code blocks for technical content when relevant


Remember: Your goal is to be maximally helpful while being efficient with your responses. Every interaction should leave the user better informed and satisfied with the assistance provided.


"""

# Function to format chat history correctly
def format_messages(messages):
    formatted = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]  # Set system prompt role to "user"
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"  # Ensure correct roles
        formatted.append({"role": role, "parts": [{"text": msg["content"]}]})
    return formatted

# Function to generate chat responses
def gemini_generator(messages: list) -> Generator:
    model = genai.GenerativeModel("gemini-2.5-flash")
    chat = model.start_chat(history=format_messages(messages))
    
    user_input = messages[-1]["content"]  
    response = chat.send_message(user_input, stream=True)

    for chunk in response:
        yield chunk.text

# Page title
st.title("🧠GENERATIVE AI CHATBOT")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-box user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-box assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

# Chat input functionality
if prompt := st.chat_input("How can I assist you?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-box user-message">{prompt}</div>', unsafe_allow_html=True)

    # Get response from Gemini
    with st.chat_message("assistant"):
        response = st.write_stream(gemini_generator(st.session_state.messages))
    
    # Save response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
