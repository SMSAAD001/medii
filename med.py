import streamlit as st
import requests
import os
import time
import speech_recognition as sr  # Speech-to-Text
from gtts import gTTS  # Text-to-Speech

# Retrieve API key from environment variables
API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Function to query Hugging Face API
def query_huggingface_api(prompt):
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {"inputs": prompt}
    
    with st.spinner("Fetching response..."):
        response = requests.post(API_URL, headers=headers, json=payload)
        time.sleep(1)  # Simulate processing time
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "Sorry, I couldn't understand that.")
                return "Sorry, I couldn't understand that."
            except requests.exceptions.JSONDecodeError:
                return "Invalid API response."
        else:
            return f"API request failed with status code {response.status_code}"

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Streamlit UI
st.set_page_config(page_title="Medicine Chatbot", layout="centered")
st.title("💊 Medicine & Disease Prediction Chatbot")
st.write("👩‍⚕️ Ask about symptoms, medicines, or health advice!")

# Speech-to-Text Feature
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, could not understand your voice."
        except sr.RequestError:
            return "Check your internet connection."

# Short Answer Generator
def generate_short_answer(prompt):
    full_response = query_huggingface_api(prompt)
    return " ".join(full_response.split()[:40])  # Limit to ~3-4 lines

# General Health Query
st.subheader("💬 General Health Query")
user_input = st.text_input("You:", "", key="query_input")
if st.button("🎙️ Speak"):
    user_input = recognize_speech()
    st.text(f"You: {user_input}")

if st.button("Ask"): 
    if user_input:
        detailed_prompt = f"Provide a **short** medical explanation for: {user_input}. Include key symptoms, causes, and treatments."
        response_text = generate_short_answer(detailed_prompt)
        
        st.session_state.chat_history.append((user_input, response_text))
        st.success(f"🤖 **Bot:** {response_text}")

# Chat History
st.subheader("📜 Chat History")
for query, reply in st.session_state.chat_history[-5:]:  # Show last 5 exchanges
    st.write(f"👤 **You:** {query}")
    st.write(f"🤖 **Bot:** {reply}")
    st.write("---")

# Disease Prediction Based on Symptoms
st.subheader("🩺 Disease Prediction")
symptoms = st.text_area("Enter symptoms (comma-separated):", "fever, cough, sore throat")
if st.button("Predict Disease"):
    if symptoms:
        prediction_prompt = f"Predict possible diseases based on: {symptoms}. Provide a brief summary (max 4 lines)."
        disease_text = generate_short_answer(prediction_prompt)
        st.warning(f"🩺 **Possible Disease:** {disease_text}")

# Medicine Information
st.subheader("💊 Medicine Suggestions")
med_query = st.text_input("Ask about a medicine:", "What is Paracetamol used for?")
if st.button("Get Medicine Info"):
    if med_query:
        med_prompt = f"Explain in **4 lines max** the uses, dosage, and side effects of {med_query}."
        med_text = generate_short_answer(med_prompt)
        st.info(f"💊 **Medicine Info:** {med_text}")

