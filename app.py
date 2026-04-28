import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE CONNECTION ---
conn = sqlite3.connect('hospital_db.sqlite', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS patients 
                 (pid TEXT PRIMARY KEY, name TEXT, age INTEGER, gender TEXT, phone TEXT, blood TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS doctors 
                 (did TEXT PRIMARY KEY, name TEXT, specialty TEXT, fees REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS appointments 
                 (aid INTEGER PRIMARY KEY AUTOINCREMENT, pid TEXT, did TEXT, date TEXT, status TEXT)''')
    
    # Pre-fill 10 Doctors
    c.execute("SELECT count(*) FROM doctors")
    if c.fetchone()[0] == 0:
        docs = [
            ('D1', 'Dr. Ahmed Khan', 'Cardiology', 1000), ('D2', 'Dr. Fatima Ali', 'Neurology', 1000),
            ('D3', 'Dr. Zubair Sheikh', 'Dermatology', 1000), ('D4', 'Dr. Sana Mansoor', 'Gynecology', 1000),
            ('D5', 'Dr. Usman Yusuf', 'Orthopedic', 1000), ('D6', 'Dr. Hina Raza', 'Pediatrics', 1000),
            ('D7', 'Dr. Bilal Akram', 'General Physician', 1000), ('D8', 'Dr. Maryam Jameel', 'Psychiatry', 1000),
            ('D9', 'Dr. Faisal Shah', 'ENT', 1000), ('D10', 'Dr. Sadia Malik', 'Eye Specialist', 1000)
        ]
        c.executemany("INSERT INTO doctors VALUES (?, ?, ?, ?)", docs)
    conn.commit()

init_db()

# --- CUSTOM STYLING ---
st.set_page_config(page_title="Nexus Hospital", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .red-label { color: #FF0000; font-weight: bold; margin-bottom: -10px; font-size: 14px; }
    .patient-card {
        background: white; border-left: 10px solid #FF0000; padding: 20px;
        border-radius: 10px; box-shadow: 2px 2px 15px rgba(0,0,0,0.1);
        color: #333; margin-top: 20px;
    }
    .stButton>button { background-color: #00796b; color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'reg_done' not in st.session_state:
    st.session_state.reg_done = False
    st.session_state.p_info = {}

# --- SIDEBAR ---
st.sidebar.title("🏥 NEXUS HEALTHCARE")
menu = ["Dashboard", "Patient Registration", "Book Appointment", "Records & Billing"]
choice = st.sidebar.selectbox("Menu", menu)

# --- 1. DASHBOARD ---
if choice == "Dashboard":
    st.title("Hospital Dashboard")
    st.info("Welcome to the Medical Management System. Use the sidebar to begin.")
    st.image("https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&q=80&w=1000")

# --- 2. PATIENT REGISTRATION ---
elif choice == "Patient Registration":
    if st.session_state.reg_done:
        # AFTER REGISTER OVERVIEW
        st.subheader("✅ Patient Registered Successfully")
        data = st.session_state.p_info
        st.markdown(f"""
        <div class="patient-card">
            <h2 style="color:#00796b;">PATIENT PROFILE OVERVIEW</h2>
            <hr>
            <p><b>NAME:</b> {data['name']}</p>
            <p><b>PATIENT ID:</b> {data['id']}</p>
            <p><b>PHONE NUMBER:</b> {data['phone']}</p>
            <p><b>AGE:</b> {data['age']} | <b>GENDER:</b> {data['gender']}</p>
            <p><b>BLOOD GROUP:</b> {data['blood']}</p>
            <p style="color: green;"><b>STATUS:</b> RECORD ACTIVE IN DATABASE</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Register Another Patient"):
            st.session_state.reg_done = False
            st.rerun()

    else:
        st.subheader("🆕 New Patient Registration")
        with st.container():
            st.markdown("<p class='red-label'>FULL NAME (REQUIRED):</p>", unsafe_allow_html=True)
            p_name = st.text_input("", placeholder="e.g. Muhammad Ali", key="n1")
            
            st.markdown("<p class='red-label'>PATIENT ID / CNIC (REQUIRED):</p>", unsafe_allow_html=True)
            p_id = st.text_input("", placeholder="e.g. 35201-XXXXXXX-X", key="n2")
            
            st.markdown("<p class='red-label'>PHONE NUMBER (REQUIRED):</p>", unsafe_allow_html=True)
            p_phone = st.text_input("", placeholder="e.g. 0300-1234567", key="n3")
            
            c1, c2, c3 = st.columns(3)
            p_age = c1.number_input("Age", 1, 100)
            p_gender = c2.selectbox("Gender", ["Male", "Female", "Other"])
            p_blood = c3.selectbox("Blood Group", ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"])
            
            if st.button("COMPLETE REGISTRATION"):
                if p_name and p_id and p_phone:
                    try:
                        c.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?)", 
                                  (p_id, p_name, p_age, p_gender, p_phone, p_blood))
                        conn.commit()
                        st.session_state.p_info = {
                            "name": p_name, "id": p_id, "phone": p_phone, 
                            "age": p_age, "gender": p_gender, "blood": p_blood
                        }
                        st.session_state.reg_done = True
                        st.rerun()
                    except:
                        st.error("This ID is already registered in the system.")
                else:
                    st.warning("Please fill all RED labeled fields.")

# --- 3. BOOK APPOINTMENT ---
elif choice == "Book Appointment":
    st.subheader("📅 Appointment Booking (Fee: Rs. 1000)")
    patients = pd.read_sql_query("SELECT pid, name FROM patients", conn)
    doctors = pd.read_sql_query("SELECT did, name, specialty FROM doctors", conn)
    
    if patients.empty:
        st.error("No patients found. Register a patient first.")
    else:
        p_list = [f"{r['pid']} | {r['name']}" for _, r in patients.iterrows()]
        d_list = [f"{r['did']} | {r['name']} ({r['specialty']})" for _, r in doctors.iterrows()]
        
        st.markdown("<p class='red-label'>SELECT PATIENT:</p>", unsafe_allow_html=True)
        sel_p = st.selectbox("", p_list)
        
        st.markdown("<p class='red-label'>SELECT DOCTOR:</p>", unsafe_allow_html=True)
        sel_d = st.selectbox("", d_list)
        
        if st.button("CONFIRM APPOINTMENT"):
            pid = sel_p.split(" | ")[0]
            did = sel_d.split(" | ")[0]
            dt = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO appointments (pid, did, date, status) VALUES (?, ?, ?, ?)", 
                      (pid, did, dt, "Paid"))
            conn.commit()
            st.success(f"Appointment booked! Receipt generated for Rs. 1000")

# --- 4. RECORDS & BILLING ---
elif choice == "Records & Billing":
    st.subheader("📑 Patient History")
    search_id = st.text_input("Enter Patient ID to view full History")
    if search_id:
        c.execute("SELECT * FROM patients WHERE pid=?", (search_id,))
        p = c.fetchone()
        if p:
            st.write(f"### Record for {p[1]}")
            st.write(f"📞 Contact: {p[4]} | 🩸 Blood: {p[5]}")
            
            # Show Billing
            query = """SELECT a.date, d.name as Doctor, d.fees 
                       FROM appointments a JOIN doctors d ON a.did = d.did 
                       WHERE a.pid = ?"""
            history = pd.read_sql_query(query, conn, params=(search_id,))
            st.table(history)
            st.info(f"**Total Revenue from Patient: Rs. {history['fees'].sum():,.2f}**")
        else:
            st.error("Patient not found.")