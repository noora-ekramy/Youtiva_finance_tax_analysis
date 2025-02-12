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

st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #041317; 
        height: 100%;
        margin: 0;
        padding: 0;
    }
    .stApp {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    .tagline {
        font-size: 20px;
        font-weight: bold;
        color: #a4ffff;
        text-align: center;
        margin-top: -10px;
    }
    .subtagline {
        font-size: 14px;
        color: #fcfcfc;
        text-align: center;
        padding:20px;
        margin-bottom: 20px;
    }
     .header {
        font-size: 39px;
        font-weight: bold;
        color: #65daff;
        text-align: center;
        margin-top: -10px;
    }
    </style>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1, 5]) 

with col1:
    st.image("youtiva-logo.png", width=100)

with col2:
    st.title("Youtiva")

st.markdown('<div class="tagline">Stand Out & Excel with Your Unique AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtagline">Empowering businesses with tailored AI solutions to streamline operations, boost efficiency, and sustain competitive advantage</div>', unsafe_allow_html=True)
st.markdown('<div class="header">Financial & Tax Analysis</div>', unsafe_allow_html=True)

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
    dob = st.date_input("Date of Birth *", min_value=pd.to_datetime('1900-01-01'))
    filling_status = st.selectbox("Filing Status *", ["Single", "Married filing jointly", "Married filing separately", "Head of household"])

# Spouse Information
if filling_status != "Single":
    st.header("Spouse Information")
    col1, col2 = st.columns(2)
    with col1:
        spouse_first_name = st.text_input("Spouse First Name")
        spouse_last_name = st.text_input("Spouse Last Name")

    with col2:
        spouse_dob = st.date_input("Spouse Date of Birth", value=None, min_value=pd.to_datetime('1900-01-01'))

# Dependents
if filling_status != "Single":
    st.header("Dependents Information")
    col1, col2 = st.columns(2)
    with col1:
        num_dependents = st.number_input("Number of Dependents *", min_value=0, step=1)
    with col2:
        dependents_income = st.number_input("Dependents' Income *", min_value=0.0, step=100.0)

    dependents_ssn = st.selectbox("Do the dependents have a SSN or ITIN? *", ["Yes", "No"])
else:
    num_dependents = 0
    dependents_income = 0.0
    dependents_ssn = "No"

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
    missing_fields = []
    required_fields = {
        "Email Address": email,
        "First Name": first_name,
        "Last Name": last_name,
        "State": state if state != "Select your state" else "",
        "Total Income Last Year": total_income,
        "Total Tax Paid Last Year": total_tax_paid,
        "Date of Birth": dob,
        "Filing Status": filling_status,
        "Income Sources": income_sources,
        "Assets Acquired": assets_acquired,
        "Total Purchased Price": total_purchased_price,
        "Tax Return": tax_return,
        "Profit / Loss": profit_loss,
        "Balance Sheet": balance_sheet,
    }
    if filling_status != "Single":
        required_fields.update({
            "Number of Dependents": num_dependents,
            "Dependents' Income": dependents_income,
            "Dependents SSN/ITIN": dependents_ssn
        })

    for field, value in required_fields.items():
        if not value:
            missing_fields.append(field)

    return missing_fields

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
    missing_fields = all_fields_filled()
    if not missing_fields:
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
        st.warning(f"⚠️ Please fill in the following required fields before analyzing the data: {', '.join(missing_fields)}")