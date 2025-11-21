# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 14:46:45 2025

@author: LENEVO X250
"""

import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import numpy as np

st.set_page_config(page_title="RideFair Prototype", page_icon="🚕", layout="wide")

# ------- Mock Data Structures -------
def get_initial_users():
    return {
        "rider": {"demo@rider.com": {"password":"pass", "name":"Demo Rider", "role":"Rider", "rating":4.8, "profile_badges":["Trustworthy"], "rides":[], "payment_status":"None"}},
        "driver": {"demo@driver.com":{"password":"pass", "name":"Demo Driver", "role":"Driver", "vehicle":"Tesla Model 3", "rating":4.9, "profile_badges":["Top Rated"], "earnings":320, "available":True, "rides":[], "payment_status":"None"}},
        "admin": {"admin@ridefair.com": {"password":"admin", "name":"Admin", "role":"Admin"}}
    }
def get_initial_rides():
    return [] # List of dicts for rides

def get_initial_disputes():
    return []

if "users_db" not in st.session_state:
    st.session_state.users_db = get_initial_users()
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "rides_db" not in st.session_state:
    st.session_state.rides_db = get_initial_rides()
if "disputes_db" not in st.session_state:
    st.session_state.disputes_db = get_initial_disputes()
if "ride_status" not in st.session_state:
    st.session_state.ride_status = {}
if "negotiation_log" not in st.session_state:
    st.session_state.negotiation_log = []

# ---- Branding & Color/Logo ----
def show_branding():
    st.markdown(
        "<h1 style='color:#008080;font-size:2.2em;'>🚕 RideFair</h1>" 
        "<div style='color:#555;font-size:1.2em;'>A Fair, Secure, and Modern Ride-sharing Platform</div>", 
        unsafe_allow_html=True
    )
    st.image("https://images.unsplash.com/photo-1519864600365-1e31cc7cb3a2?auto=format&fit=crop&w=800&q=80", width=340, caption="Smart, Transparent Rides")

# ------- Registration & Login -------
def login_register_ui(role):
    st.subheader(f"{role} Login / Registration")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email = st.text_input("Email", key=f"{role}-login-email")
        password = st.text_input("Password", type="password", key=f"{role}-login-pw")
        if st.button("Login", key=f"{role}-login-btn"):
            db = st.session_state.users_db.get(role.lower(), {})
            user = db.get(email, None)
            if user and user["password"] == password:
                st.session_state.current_user = user.copy()
                st.session_state.current_user["email"] = email
                st.success("Login successful! Go to App Menu.")
            else:
                st.error("Invalid credentials.")
    if role != "Admin":
        with tab2:
            name = st.text_input("Full Name", key=f"{role}-reg-name")
            email = st.text_input("Email", key=f"{role}-reg-email")
            password = st.text_input("Password", type="password", key=f"{role}-reg-pw")
            vehicle = st.text_input("Vehicle Details (Drivers only)", key=f"{role}-reg-veh")
            if st.button("Register", key=f"{role}-reg-btn"):
                db = st.session_state.users_db.get(role.lower(), {})
                if email in db:
                    st.error("Email already registered.")
                else:
                    db[email] = {"password":password, "name":name, "role":role, "rating":0, "profile_badges":[], "rides":[], "payment_status":"None"}
                    if role == "Driver": db[email]["vehicle"] = vehicle
                    st.success("Registration successful! Please log in.")

# ------- Profile Page -------
def profile_ui(user):
    st.markdown(f"#### {user.get('name','')} ({user.get('role')})")
    if user.get("vehicle"): st.write(f"Vehicle: {user['vehicle']}")
    st.write(f"Email: {user.get('email','')}")
    st.write(f"Rating: {user.get('rating', 0)} ⭐")
    st.write("Badges:", ", ".join(user.get("profile_badges", [])))
    st.write("Edit profile (simulate):")
    name = st.text_input("Change Name", value=user["name"] if "name" in user else "", key="profname")
    if st.button("Save Name Update"):
        user["name"] = name
        st.success("Name updated.")

# ------- Ride Request Flow -------
def ride_request_ui(user):
    st.subheader("Request a Ride 🛺")
    pickup = st.text_input("Pickup Location")
    dropoff = st.text_input("Drop-off Location")
    with st.expander("Map & Route (mock)"):
        st.image("https://cdn.pixabay.com/photo/2017/06/09/16/36/map-2386606_1280.png", width=500, caption="Route Visualization")

    dist = np.random.uniform(3,20) # mock distance km
    traffic = np.random.uniform(1,4) # mock traffic
    base_fare = np.round(2.5 * dist + 1.2 * traffic,2)
    st.write(f"Suggested fare range: €{base_fare:.2f} - €{base_fare+8:.2f} (AI/heuristic based on distance & traffic)")
    want_negotiate = st.toggle("Negotiate fare/counter-offer?")
    
    agreed_fare = st.number_input("Your Fare Offer (€)", min_value=base_fare, max_value=base_fare+10, value=base_fare, step=0.5)
    if want_negotiate:
        counter_fare = st.number_input("Driver Counter-Offer (€)", min_value=base_fare, max_value=base_fare+10, value=base_fare+2, step=0.5)
        st.session_state.negotiation_log.append((user["email"], agreed_fare, counter_fare))
        st.write("Negotiation Log:", st.session_state.negotiation_log)
    if st.button("Confirm Ride Request"):
        ride_id = "ride"+str(len(st.session_state.rides_db)+1)
        ride = {"ride_id":ride_id, "pickup":pickup, "dropoff":dropoff, "rider":user["email"], "driver":"demo@driver.com", "fare":agreed_fare, "status":"pending", "group":[], "payment_confirmed":False}
        st.session_state.rides_db.append(ride)
        st.success(f"Ride Requested. Waiting for driver acceptance.")
        st.session_state.ride_status[ride_id] = "Requested"

# ------- Fare Split -------
def fare_split_ui(user):
    st.subheader("Group Ride / Fare Split")
    group_members = st.multiselect("Add riders to group", ["alice@email.com","bob@email.com"], default=[])
    split_type = st.radio("Fare split type", ["Equal","Custom %","One pays"])
    if split_type == "Custom %":
        alice_pct = st.slider("Alice share (%)", 0, 100, 50)
        bob_pct = 100 - alice_pct
        st.text(f"Alice pays {alice_pct}%, Bob pays {bob_pct}%")
    elif split_type == "Equal":
        st.text("Each pays 50%")
    else:
        st.text("One member pays all")
    if st.button("Confirm Group & Commitment"):
        st.success("Fare commitment simulated for group ride.")

# ------- Payment/Escrow Simulation -------
def payment_escrow_ui(user, ride_id=None):
    st.subheader("Payment & Escrow")
    status = st.session_state.ride_status.get(ride_id, "Requested")
    payment_action = st.radio("Escrow Actions", ["Hold Funds","Release Funds","Refund"])
    if payment_action == "Hold Funds":
        st.success("Funds held in escrow. Await ride completion.")
        st.session_state.ride_status[ride_id] = "Paid"
    elif payment_action == "Release Funds":
        st.success("Driver paid automatically after ride completion.")
        st.session_state.ride_status[ride_id] = "Completed"
    else:
        st.warning("Escrow refunded to rider due to cancellation.")
        st.session_state.ride_status[ride_id] = "Refunded"

# ------- Real-time Ride Tracking and Status -------
def ride_tracking_ui(user):
    st.subheader("Live Ride Status")
    options = ["Driver en-route", "Pick-up", "Ride in progress", "Completing", "Completed"]
    status_step = st.select_slider("Current ride status", options=options)
    st.write(f"Ride is now: {status_step}")
    st.session_state.ride_status["last"] = status_step
    if status_step in ["Completed"]:
        st.success("Ride completed! Ready for payment and ratings.")
    elif status_step == "Pick-up":
        st.info("Driver arrived. Start ride!")

    st.info("Notifications: Fare agreed, driver en-route, payment held, ready for ratings.")

# ------- Dual Rating/Feedback -------
def dual_rating_ui(user, finished_ride=True):
    st.subheader("Rate your Experience")
    comms = st.slider("Communication (1-5)",1,5,4)
    fair = st.slider("Fairness (1-5)",1,5,4)
    total = (comms + fair) / 2
    st.success(f"Your overall rating for this ride: {total:.2f}")
    user_badge = "Trustworthy" if total > 4 else "Regular"
    st.write(f"Profile badge assigned: {user_badge}")
    user.setdefault("profile_badges", []).append(user_badge)
    st.info("Both rider and driver are prompted for ratings after each ride.")

# ------- Pricing Dashboard -------
def pricing_dashboard_ui():
    st.subheader("Transparent Pricing Dashboard")
    col1, col2 = st.columns(2)
    with col1: st.metric("Current demand level", np.random.randint(20,80))
    with col2: st.metric("Available drivers", np.random.randint(5,24))
    st.area_chart(np.random.normal(loc=20,scale=8,size=(12,)))
    st.write("Historic fare, surge pricing, driver/rider trends.")

# ------- Driver Earnings -------
def driver_earnings_ui(user):
    st.subheader("Driver Earnings Breakdown")
    st.metric("Pending Earnings", "€"+str(user.get("earnings",0)))
    st.write("Commission: 8% standard")
    net = user.get("earnings",0) * 0.92
    st.write(f"Take Home After Commission: €{net:.2f}")
    if st.toggle("Premium Features (Sim)"):
        st.write("Premium drivers get improved matching and lower commission!")

# ------- Admin Dashboard -------
def admin_dashboard_ui():
    st.subheader("Admin Panel")
    st.write("Monitor KPIs, ride logs, disputes:")
    st.metric("Total Users", np.random.randint(248,395))
    st.metric("Rides", np.random.randint(94,210))
    st.metric("Active Drivers", np.random.randint(19,53))
    st.metric("Volume (€)", np.random.randint(1900,6000))
    st.write("Dispute Management, Fare Negotiation Logs:")
    st.write(st.session_state.negotiation_log)

# ------- Main App Logic -------
def main_app():
    show_branding()
    # Role logic
    if not st.session_state.current_user:
        st.sidebar.header("Choose Your Role")
        chosen_role = st.sidebar.radio("Role", ["Rider", "Driver", "Admin"])
        login_register_ui(chosen_role)
        st.stop()
    user = st.session_state.current_user
    role = user.get("role", "Rider")
    menu_items = ["Dashboard","Request Ride","Fare Split","Tracking","Payment","Ratings","Pricing","Earnings","Admin","Profile","Logout"]
    menu_icons = ["house","geo-alt","columns-gap","arrow-repeat","credit-card","star","bar-chart-fill","cash-coin","tools","person","box-arrow-right"]
    selected = option_menu(None, options=menu_items, icons=menu_icons, orientation="horizontal")
    # Conditional page displays
    if selected == "Dashboard":
        st.success(f"Welcome, {user.get('name','User')}! ({role})")
    if selected == "Profile":
        profile_ui(user)
    if selected == "Request Ride" and role == "Rider":
        ride_request_ui(user)
    if selected == "Fare Split" and role == "Rider":
        fare_split_ui(user)
    if selected == "Payment":
        payment_escrow_ui(user, ride_id="ride1")
    if selected == "Tracking":
        ride_tracking_ui(user)
    if selected == "Ratings":
        dual_rating_ui(user)
    if selected == "Pricing":
        pricing_dashboard_ui()
    if selected == "Earnings" and role=="Driver":
        driver_earnings_ui(user)
    if selected == "Admin" and role=="Admin":
        admin_dashboard_ui()
    if selected == "Logout":
        st.session_state.current_user = None
        st.success("Logged out.")
        st.experimental_rerun()

if __name__ == '__main__':
    main_app()
