
# MySQL with Llama-3 Streamlit App

This repository contains a Streamlit application that allows users to interact with a MySQL database using the Llama-3.1 language model through the `ChatGroq` API. The app lets users select a table from a MySQL database and generate responses to prompts based on the table's data using a smart AI-driven approach.

## Prerequisites

Before running the application, ensure you have the following installed on your system:

- Python 3.7 or later
- MySQL Server
- pip (Python package installer)

## Installation

1. **Clone the Repository**

   Clone this repository to your local machine.

   ```bash
   git clone https://github.com/your-username/mysql-llama3-streamlit.git
   cd mysql-llama3-streamlit
   ```

2. **Install Python Dependencies**

   Install the necessary Python packages using pip:

   ```bash
   pip install streamlit mysql-connector-python pandasai langchain_groq python-dotenv
   ```

3. **Set Up Environment Variables**

   Create a `.env` file in the project root directory and add your `GROQ_API_KEY`:

   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Setting Up MySQL Database

Ensure your MySQL server is running, and you have a database named `parch` set up. The MySQL connection details are as follows:

- **Host:** `localhost`
- **Port:** `3306`
- **User:** `root`
- **Password:** `1234`

The app assumes that the `parch` database is already populated with tables. Adjust the database name, user, or password in the code if your setup is different.

## Running the Application

Start the Streamlit application by running the following command:

```bash
streamlit run app.py
```

## Code Explanation

### Loading Environment Variables

The application loads environment variables using the `dotenv` library:

```python
from dotenv import load_dotenv
import os

load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
```

### Fetching MySQL Table Names

The `fetch_table_names` function connects to the MySQL database and retrieves the names of all tables in the specified schema (`parch`):

```python
import mysql.connector

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
```

### Streamlit Application Layout

The Streamlit app starts with a title and then retrieves and displays table names from the MySQL database. The user can select a table, which will then be connected via the `MySQLConnector` from `pandasai`.

```python
st.title("MySQL with Llama-3")

if "table_names" not in st.session_state:
    st.session_state.table_names = fetch_table_names()

selected_table = st.selectbox("Select a table", st.session_state.table_names)
```

### Connecting to MySQL Database

Once a table is selected, the app initializes a `MySQLConnector` instance for that table:

```python
from pandasai.connectors import MySQLConnector

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
```

### Setting Up the Language Model

The `ChatGroq` model is initialized with specific settings, and a `ChatPromptTemplate` is created to guide the AI's response style:

```python
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You're a very knowledgeable data scientist who provides accurate and eloquent answers to historical questions."),
    ("human", "{question}")
])

model = ChatGroq(temperature=0.9, model="llama-3.1-70b-versatile")
```

### Creating a SmartDataframe

A `SmartDataframe` is created using the selected table and the language model. This enables intelligent interaction with the data:

```python
from pandasai import SmartDataframe

df_connector = None
if my_connector:
    df_connector = SmartDataframe(my_connector, config={"llm": model}, description=prompt_template)
```

### User Interaction and Response Generation

The user can input a prompt, and the app will use the `SmartDataframe` to generate a response based on the data from the selected table:

```python
prompt = st.text_input("Enter your prompt:")

if st.button("Generate"):
    if prompt and df_connector is not None:
        with st.spinner("Generating response..."):
            try:
                response = df_connector.chat(prompt)
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
    else:
        st.error("Connector is not initialized or no data is loaded.")
```

## Additional Notes

- Ensure that your MySQL server is running and accessible with the provided credentials.
- You may need to adapt the code to your specific environment or data schema.
- The Llama-3.1 model used in this example is very resource-intensive, so ensure your API access and infrastructure can handle the load.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
