import streamlit as st
import yfinance as yf
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return price

def send_email_alert(subject, message, sender_email, receiver_email, password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# Initialize session state variables
if 'alert_sent' not in st.session_state:
    st.session_state.alert_sent = False
if 'current_price' not in st.session_state:
    st.session_state.current_price = 0.0

st.title("Stock Price Alert System")

ticker = st.text_input("Enter stock ticker (e.g., RELIANCE.NS)", value="")
target_price = st.number_input("Set target price", min_value=0.0, value=120.0)

sender_email = st.text_input("Sender Email (Gmail)", value="")
receiver_email = st.text_input("Receiver Email", value="")
email_password = st.text_input("Email App Password", type="password")

monitor = st.checkbox("Start Monitoring")

if monitor and not st.session_state.alert_sent:
    try:
        price = get_stock_price(ticker)
        st.session_state.current_price = price
        st.write(f"Current price of {ticker}: {price}")

        if price >= target_price:
            subject = f"Stock Alert: {ticker} reached {price}"
            message = f"The stock price of {ticker} has reached {price}, which is above your target of {target_price}."
            send_email_alert(subject, message, sender_email, receiver_email, email_password)
            st.success("Alert sent!")
            st.session_state.alert_sent = True
        else:
            st.info(f"Waiting for price to reach {target_price}...")

    except Exception as e:
        st.error(f"Error: {e}")

    # Rerun the app every 60 seconds to update price
    st.rerun()
else:
    if st.session_state.alert_sent:
        st.success(f"Alert already sent for {ticker} at price {st.session_state.current_price}")
    else:
        st.write("Enter details and check 'Start Monitoring' to begin.")
