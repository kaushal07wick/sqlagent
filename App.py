#importing all the neccessary libraries
import streamlit as st
from sqlalchemy import create_engine
from langchain import SQLDatabase
from langchain.sql_database import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine
from PIL import Image

#Image element for the hero display
image = Image.open('sqlai.jpg')

#streamlit configs and title
st.set_page_config(page_title="SQL Agent")
st.title("AI Agent for Q/A with SQL Database")
st.caption("""
""")
st.image(image) #image config

#database connection method
def con():
    server = "DESKTOP-E3B8G9L"  #right now these are all my personal credentials as the database MS SQL are hosted on my local computer - Change the SERVER name to yours and u can run it easily
    Database = 'AdventureWorks2022'
    Driver = 'ODBC Driver 17 for SQL Server'
    Database_Con = f'mssql://@{server}/{Database}?driver={Driver}'

    engine = create_engine(Database_Con)  #creating the sqlachemy engine to connect to the sql database
    con = engine.connect()
    return Database_Con

def main(): 
    Db_Con = con()  #connection client
    db = SQLDatabase.from_uri(Db_Con) #storing it as a db 
    
    #input from user for the openai api key
    openai_key = st.sidebar.text_input('OpenAI API key', type='password')    

    #this loop runs only if the openai api key is entered
    if openai_key:
        llm = ChatOpenAI(temperature=0, openai_api_key=openai_key, model_name='gpt-3.5-turbo')  # defining the LLM to query the SQL database

        #intializing the message state to keep track of the messages sent
        if "messages" not in st.session_state:
            st.session_state.messages = []

        #this can keep track of the messages sent to the LLM
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        #taking in the query and displaying it in the message history
        if question := st.chat_input("Send a SQL query"):
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            #custom system prompt for the AI to write errorless syntax for the query
            PROMPT = """ 
            Given an input question, first create a syntactically correct MS SQL query to run, then look at the results of the query and return the answer.  
            The question: {question}
            """
            #langchian element that handles the query and passes it openai with SQL database as knowledge base
            db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, top_k=3)

            #the AI or Assistant will procide the response in a structured manner and hide unimportant stuff
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                for m in st.session_state.messages:
                    role = m["role"]
                    content = m["content"]
                    
                    if role == "user":
                        # main chain run to execute the query according to the system prompt
                        db_response = db_chain.run(PROMPT.format(question=content))
                        st.session_state.messages.append({"role": "assistant", "content": db_response})
                
                #variable to store the full response
                full_response = "\n".join(m["content"] for m in st.session_state.messages if m["role"] == "assistant")

                #the placeholder for displaying the message
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    main()