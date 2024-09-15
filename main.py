import streamlit as st
from streamlit_chat import message
from transformers import pipeline
from PyPDF2 import PdfReader

# A pre trained model for summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

#Summarizing the text
def summarize_text(text):
    summary = summarizer(text, max_length=100, min_length=60, do_sample=False)
    return summary[0]['summary_text']


st.sidebar.title("Insight Extract")
st.sidebar.write("--------")
pdfs = st.sidebar.file_uploader("Add PDF file", type='pdf')     # Upload the document in a pdf format
st.sidebar.write("-------")
submit_button = st.sidebar.button("Submit")

text = st.chat_input(placeholder="Say Hello")   # Taking the input from the user
text = str(text)
data = summarize_text(text)     # Summarizing the given input


message(f"{text}",is_user=True)     # User's Message
message(f"{data}")      # Models Response

# Taking the data which is present in our pdf and extracting it in a list
docs_text = []
if pdfs is not None:
    reader = PdfReader(pdfs)
    num_of_pages = len(reader.pages)
    for i in range(num_of_pages):
        page = reader.pages[i]
        docs_text += page.extract_text().strip().split()
    #
    # st.sidebar.text_area("Here is the text", f"{docs_text}", height=200)

my_message = " ".join(docs_text) # converting the list into a string
# st.sidebar.text_area("Here is the text", f"{my_message}", height=200)

# if submit button is pressed summary is provided
if submit_button:
    data = summarize_text(my_message)
    text = my_message
    message(f"{text}", is_user=True)
    message(f"{data}")
