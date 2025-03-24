import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")  # Ensure .env contains HF_API_KEY=your_api_key

# Check API Key
if not HF_API_KEY:
    st.error("API key not found. Please set HF_API_KEY in your .env file.")
    st.stop()

# Hugging Face API URL
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"  # Change if needed

# Headers for authentication
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def query_huggingface(prompt):
    """Fetches response from Hugging Face model with proper error handling."""
    payload = {"inputs": prompt}
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        # If no response or invalid JSON, raise an error
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"
        
        # Try to parse JSON response
        data = response.json()
        
        # Ensure there's valid generated text
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"]
        else:
            return "Error: No valid response received from the model."
    
    except json.JSONDecodeError:
        return "Error: Unable to decode response. API might be down."
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

# Streamlit UI
st.title("Medicinal Chatbot ")
st.write("Ask me anything about medicines, symptoms, or treatments.")

# User input
user_input = st.text_input("Enter your query:", "What are the side effects of paracetamol?")

if st.button("Get Answer"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            response = query_huggingface(user_input)
            st.success("Response:")
            st.write(response)
    else:
        st.warning("Please enter a query.")
