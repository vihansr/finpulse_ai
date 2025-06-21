import streamlit as st
import pandas as pd
from database import create_connection

st.set_page_config(page_title="Admin Panel", layout="wide")

# --- Optional: Simple Password Auth ---
PASSWORD = "admin123"
user_pass = st.text_input("🔐 Enter Admin Password", type="password")
if user_pass != PASSWORD:
    st.warning("Please enter correct password to access admin features.")
    st.stop()

st.title("📋 Email Subscribers Admin Panel")

# --- Delete Email Function ---
def delete_email(email):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
        conn.commit()
        cursor.close()
        conn.close()
        st.success(f"🗑️ Deleted {email}")
    except Exception as e:
        st.error(f"Error deleting {email}")
        st.exception(e)

# --- Fetch Subscribers ---
try:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, subscribed_at FROM subscribers ORDER BY subscribed_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(rows, columns=["ID", "Email", "Subscribed At"])

    st.success(f"We have {len(df)} subscribers!")

    # Display Table with Delete Buttons
    for i, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 5, 2])
        with col1:
            st.write(f"📧 {row['Email']}")
        with col2:
            st.write(f"🕒 {row['Subscribed At'].strftime('%Y-%m-%d %H:%M:%S')}")
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{row['ID']}"):
                delete_email(row["Email"])

    # --- Export to CSV ---
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "subscribers.csv", "text/csv")

except Exception as e:
    st.error("Failed to load subscribers.")
    st.exception(e)
