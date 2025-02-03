import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# Set up OpenAI client
client = OpenAI(api_key=api_key)

st.title("📊 Financial & Tax Analysis")

# Personal Information
st.header("Personal Information")
col1, col2 = st.columns(2)
with col1:
    email = st.text_input("Email Address *")
    first_name = st.text_input("First Name *")
    last_name = st.text_input("Last Name *")
    state = st.selectbox("State *", ["Select your state", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"])

with col2:
    total_income = st.number_input("Total Income Last Year *", min_value=0.0, step=1000.0)
    total_tax_paid = st.number_input("Total Tax Paid Last Year *", min_value=0.0, step=100.0)
    dob = st.date_input("Date of Birth *")
    filling_status = st.selectbox("Filing Status *", ["Single", "Married filing jointly", "Married filing separately", "Head of household"])

# Spouse Information
st.header("Spouse Information (if applicable)")
col1, col2 = st.columns(2)
with col1:
    spouse_first_name = st.text_input("Spouse First Name")
    spouse_last_name = st.text_input("Spouse Last Name")

with col2:
    spouse_dob = st.date_input("Spouse Date of Birth", value=None)

# Dependents
st.header("Dependents Information")
col1, col2 = st.columns(2)
with col1:
    num_dependents = st.number_input("Number of Dependents *", min_value=0, step=1)
with col2:
    dependents_income = st.number_input("Dependents' Income *", min_value=0.0, step=100.0)

dependents_ssn = st.selectbox("Do the dependents have a SSN or ITIN? *", ["Yes", "No"])

# Income Sources
st.header("Income Sources")
income_sources = st.multiselect("Select all applicable sources of income *", [
    "W2/ Salaried Employed", "Self-employed 1099", "Have Companies structure (LLC, S Corp, C Corp)",
    "Real Estate Investment", "Stocks and bonds Investment", "Other types of investments"
])

# Assets Acquired
st.header("Assets & Investments")
assets_acquired = st.text_area("List assets acquired this year (cars, machines, land, buildings, etc.) *")
total_purchased_price = st.number_input("Total Purchased Price *", min_value=0.0, step=1000.0)

# File Uploads
st.header("Upload Documents")
col1, col2 = st.columns(2)
with col1:
    tax_return = st.file_uploader("Upload Last Year Tax Return *", type=["csv"])
    profit_loss = st.file_uploader("Profit / Loss Upload *", type=["csv"])
with col2:
    balance_sheet = st.file_uploader("Balance Sheet Upload *", type=["csv"])

# LLM Section
st.header("AI Financial Assistant")
user_question = st.text_area("Ask a question about your financial data:")

# Processing CSV files
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file).to_string()
    return "No data uploaded."

# Check if all required fields are filled
def all_fields_filled():
    required_fields = [email, first_name, last_name, state, total_income, total_tax_paid, dob, filling_status, num_dependents, dependents_ssn, income_sources, assets_acquired, total_purchased_price, tax_return, profit_loss, balance_sheet]
    return all(required_fields) and user_question

def ask_llm(question, data_text):
    """Send financial data and user question to OpenAI API."""
    prompt = f"""
    The following is the user's financial data:
    {data_text}
    
    Question: {question}
    Answer:
    """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst. Answer user questions based on the given financial data."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

if st.button("Analyze Data"):
    if all_fields_filled():
        financials_text = f"""
        Total Income: {total_income}
        Total Tax Paid: {total_tax_paid}
        Filing Status: {filling_status}
        Number of Dependents: {num_dependents}
        Income Sources: {', '.join(income_sources)}
        Assets Acquired: {assets_acquired}
        Total Purchased Price: {total_purchased_price}
        
        Tax Return Data:
        {process_uploaded_file(tax_return)}
        
        Profit & Loss Data:
        {process_uploaded_file(profit_loss)}
        
        Balance Sheet Data:
        {process_uploaded_file(balance_sheet)}
        """
        answer = ask_llm(user_question, financials_text)
        st.subheader("📢 Analysis")
        st.write(answer)
    else:
        st.warning("⚠️ Please fill in all required fields and upload the necessary documents before analyzing the data.")
