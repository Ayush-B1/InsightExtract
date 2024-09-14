import streamlit as st
from streamlit_chat import message
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
def summarize_text(text):
    # Summarize the input text
    summary = summarizer(text, max_length=100, min_length=60, do_sample=False)
    return summary[0]['summary_text']

st.title("Insight Extract")
pdfs = st.sidebar.file_uploader("Add PDF file", type='pdf')
st.sidebar.write("-------")


text = st.chat_input(placeholder="Say give me Extract some Insights")
text = str(text)
data = summarize_text(text)
message(f"User: {text}")
message(f"Machine: {data}", is_user=True)

