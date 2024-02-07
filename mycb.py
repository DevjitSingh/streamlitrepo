import streamlit as st
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from googlesearch import search
from PyPDF2 import PdfReader
import io
import time
from docx import Document
import requests
from datetime import datetime

# Pass your key here
OPENAI_API_KEY = "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"

# Check if internet connection is available
def check_internet():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Set up sidebar
st.sidebar.title("Welcome to Chatbot with Question Answering!")
user_name = st.sidebar.text_input("Enter Your Name", "Your Name")
st.sidebar.markdown(f"Hello Sir : , {user_name}! Please select below search criteria ")

internet_available = check_internet()
search_option = st.sidebar.radio("Choose Search Option",
                                 ["File Upload", "Internet Search"] if internet_available else ["File Upload"])

# Disable all buttons in the sidebar if internet connection is not available
if not internet_available:
    st.sidebar.warning("Internet connection is required for searching.")
    st.sidebar.warning("Please check your internet connection and try again.")

def extract_file_content(file):
    content = ""
    if file.type == 'application/pdf':
        pdf_content = file.read()
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        max_pages = 5
        content = " ".join([pdf_reader.pages[page].extract_text() for page in range(min(max_pages, len(pdf_reader.pages)))])
    elif file.type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        doc_content = io.BytesIO(file.read())
        doc_reader = Document(doc_content)
        content = " ".join([paragraph.text for paragraph in doc_reader.paragraphs])
    return content

def get_response(embeddings, text, user_question_upper):
    vector_store = FAISS.from_texts([text], embeddings)
    match = vector_store.similarity_search(user_question_upper)
    with st.spinner("Searching for the response..."):
        time.sleep(3)  # Simulating a delay for demonstration purposes
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            temperature=0,
            max_tokens=1000,
            model_name="gpt-3.5-turbo"
        )
        chain = load_qa_chain(llm, chain_type="stuff")
        response = chain.run(input_documents=match, question=user_question_upper)
        return response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def display_result(user_question_upper, response, datetime_str, user_name):
    st.write(f"**{user_name} asked :** {user_question_upper} ?", unsafe_allow_html=True)
    st.write(f"**Date and Time:** {datetime_str}")
    st.markdown(f"**Chatbot Response:**\n\n{response}")

# Get user question based on the selected search option
if search_option == "File Upload":
    file = st.sidebar.file_uploader("Choose a File", type=['pdf', 'doc', 'docx'])
    user_question_upper = st.sidebar.text_input("Type Your Question Here")
    st.markdown("<span style='font-size:30px; text-transform: uppercase; color: yellow;'>Response will be based on the content</span>", unsafe_allow_html=True)

elif search_option == "Internet Search" and internet_available:
    user_question_upper = st.sidebar.text_input("Type Your Question Here")
    st.markdown("<span style='font-size:30px; text-transform: uppercase; color: yellow;'>Response will be based on internet search results</span>", unsafe_allow_html=True)

# Ask button to submit the user's question
if st.sidebar.button("Ask") and internet_available:
    if user_question_upper:
        if search_option == "File Upload" and file is not None:
            try:
                text = extract_file_content(file)
                embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
                response, datetime_str = get_response(embeddings, text, user_question_upper)
                display_result(user_question_upper, response, datetime_str, user_name)
            except Exception as e:
                st.error(f"An error occurred during file processing: {str(e)}")

        elif search_option == "Internet Search":
            try:
                with st.spinner("Searching for the response on the internet..."):
                    time.sleep(3)  # Simulating a delay for demonstration purposes
                    search_results = search(user_question_upper, num=1, stop=5, pause=2, user_agent="Mozilla/5.0")
                    top_result = next(search_results, None)

                    if top_result:
                        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        display_result(user_question_upper, top_result, datetime_str, user_name)
            except Exception as e:
                st.error(f"An error occurred during internet search: {str(e)}")

# Display uploaded message if file is uploaded
if 'file' in locals() and file is not None and search_option == "File Upload":
    st.markdown("<span style='color: blue;'>File successfully uploaded!</span>", unsafe_allow_html=True)

# Refresh button
if st.sidebar.button("Refresh"):
    with st.spinner("Refreshing..."):
        # Simulate a delay for demonstration purposes
        time.sleep(2)
        url = "http://localhost:8501/?cache-buster=123"
        st.sidebar.markdown(f'<a href="{url}">Refresh</a>', unsafe_allow_html=True)
        st.success("Page successfully refreshed")
    # Add text message next to the Refresh button
    st.sidebar.markdown("<span style='color:yellow;'>You may click the Refresh blue link to reload the page</span>", unsafe_allow_html=True)
