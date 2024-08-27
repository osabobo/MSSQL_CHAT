import streamlit as st
from pandasai import SmartDataframe
import mysql.connector
from pandasai.connectors import MySQLConnector
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

# Function to fetch table names from MySQL database
def fetch_table_names():
    conn = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="1234",
        database="parch"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'parch';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    cursor.close()
    conn.close()
    return table_names

# Streamlit app
st.title("MySQL with Llama-3")

# Fetch table names once and store in session state to avoid re-fetching
if "table_names" not in st.session_state:
    st.session_state.table_names = fetch_table_names()

# Select box for table names
selected_table = st.selectbox("Select a table", st.session_state.table_names)

# Initialize connector only if a table is selected
my_connector = None
if selected_table:
    my_connector = MySQLConnector(config={
        "host": "localhost",
        "port": 3306,
        "database": "parch",
        "username": "root",
        "password": "1234",
        "table": selected_table
    })

# Create a prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You're a very knowledgeable data scientist who provides accurate and eloquent answers to historical questions."),
    ("human", "{question}")
])

# Initialize the ChatGroq model
model = ChatGroq(temperature=0.9, model="llama-3.1-70b-versatile")

# Create a SmartDataframe with the selected table
df_connector = None
if my_connector:
    df_connector = SmartDataframe(my_connector, config={"llm": model}, description=prompt_template)

# Input prompt
prompt = st.text_input("Enter your prompt:")

# Generate response on button click
if st.button("Generate"):
    if prompt and df_connector is not None:  # Ensure df_connector is initialized
        with st.spinner("Generating response..."):
            try:
                response = df_connector.chat(prompt)
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
    else:
        st.error("Connector is not initialized or no data is loaded.")
