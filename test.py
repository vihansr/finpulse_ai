# import os
# os.system("streamlit run app.py")
from database import create_connection
import pandas as pd

try:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, subscribed_at FROM subscribers ORDER BY subscribed_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    emails = pd.DataFrame(rows, columns=["ID", "Email", "Subscribed At"])['Email']
    for mail in emails:
        print(mail)

except Exception as e:
    print(e)
