import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

#######################################
# PAGE SETUP
#######################################

st.set_page_config(page_title="Police Station Dashboard", page_icon=":police_car:", layout="wide")

st.title("Police Station Dashboard")
st.markdown("_Prototype v0.0.1_")

# Mock user database
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "constable": {"password": "constable123", "role": "constable"},
    "commissioner": {"password": "commish123", "role": "commissioner"},
}

# Session state for user authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None

# Login form
if not st.session_state.authenticated:
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in users and users[username]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.role = users[username]["role"]
            st.success(f"Logged in as {st.session_state.role}")
        else:
            st.error("Invalid username or password")
    st.stop()

# Logout button
if st.session_state.authenticated:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.rerun()

#######################################
# DATA LOADING
#######################################

@st.cache_data
def load_data():
    df = pd.read_excel('dataset.xlsx')
    return df

df = load_data()

def save_data(df):
    df.to_excel("dataset.xlsx", index=False)

def reload_data():
    return load_data()

with st.expander("Data Preview"):
    st.dataframe(df)

#######################################
# VISUALIZATION METHODS
#######################################

def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font.size": 28,
            },
            title={
                "text": label,
                "font": {"size": 24},
            },
        )
    )

    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={
                    "color": color_graph,
                },
            )
        )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin=dict(t=30, b=0),
        showlegend=False,
        plot_bgcolor="white",
        height=200,  # Increased height
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_gauge(indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": indicator_suffix,
                "font.size": 26,
            },
            gauge={
                "axis": {"range": [0, max_bound], "tickwidth": 1},
                "bar": {"color": indicator_color},
            },
            title={
                "text": indicator_title,
                "font": {"size": 28},
            },
        )
    )
    fig.update_layout(
        height=250,  # Increased height
        margin=dict(l=10, r=10, t=50, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_top_right():
    security_data = df.groupby("Security Type").size().reset_index(name='count')
    fig = px.bar(
        security_data,
        x="Security Type",
        y="count",
        title="Security Type Distribution",
        height=500,  # Increased height
    )
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    return fig

def plot_bottom_left():
    response_time_data = df.groupby("Response time Rating").size().reset_index(name='count')
    fig = px.line(
        response_time_data,
        x="Response time Rating",
        y="count",
        markers=True,
        text="count",
        title="Response Time Rating Distribution",
        height=500,  # Increased height
    )
    fig.update_traces(textposition="top center")
    return fig

def plot_bottom_right():
    cases_data = df.groupby("City")["Cases"].sum().reset_index(name='total_cases')
    fig = px.bar(
        cases_data,
        x="City",
        y="total_cases",
        title="Total Cases by City",
        height=500,  # Increased height
    )
    return fig

#######################################
# STREAMLIT LAYOUT
#######################################

# Role-based access control
if st.session_state.role in ["admin", "commissioner"]:
    with st.sidebar:
        st.header("Configuration")
        st.info("Data is loaded from 'dataset.xlsx'.", icon="ℹ️")

    # Two columns for better visibility
    left_column, right_column = st.columns(2)

    with left_column:
        plot_metric(
            "Total Cases",
            df["Cases"].sum(),
            prefix="",
            suffix="",
            show_graph=True,
            color_graph="rgba(0, 104, 201, 0.2)",
        )
        plot_gauge(df["Response time Rating"].mean(), "#0068C9", "", "Average Response Time", 10)

    with right_column:
        plot_metric(
            "Total Security Ratings",
            df["Station Dashboard"].sum(),
            prefix="",
            suffix="",
            show_graph=True,
            color_graph="rgba(255, 43, 43, 0.2)",
        )
        plot_gauge(df["Station Dashboard"].mean(), "#FF8700", "", "Station Dashboard", 10)

    # Full-width plots
    st.plotly_chart(plot_top_right(), use_container_width=True)
    st.plotly_chart(plot_bottom_left(), use_container_width=True)
    st.plotly_chart(plot_bottom_right(), use_container_width=True)

    # Commissioner data entry form
    if st.session_state.role == "commissioner":
        st.header("Commissioner Data Entry Form")
        with st.form(key="data_entry_form"):
            city = st.text_input("City")
            response_time_rating = st.number_input("Response time Rating", min_value=0, max_value=10, step=1)
            cases = st.number_input("Cases", min_value=0, step=1)
            security_type = st.text_input("Security Type")
            station_dashboard = st.number_input("Station Dashboard", min_value=0, max_value=10, step=1)
            case_number = st.text_input("Case Number")
            kgid = st.text_input("KGID")
            report_time = st.text_input("Report time", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            new_data = pd.DataFrame({
                "City": [city],
                "Response time Rating": [response_time_rating],
                "Cases": [cases],
                "Security Type": [security_type],
                "Station Dashboard": [station_dashboard],
                "Case Number": [case_number],
                "KGID": [kgid],
                "Report time": [report_time],
                "Reported": [""],  # Initialize the "Reported" column as empty or with a default value
            })

            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)  # Save to dataset.xlsx
            st.success("New data added successfully! Data saved to 'dataset.xlsx'.")

            # Reload data and refresh plots
            df = reload_data()
            st.experimental_rerun()  # Refresh the app to reflect changes automatically

elif st.session_state.role == "constable":
    st.header("Constable Dashboard")
    st.write("This dashboard is for constables. Implement specific features for constables here.")

    kgid_input = st.text_input("Enter KGID")
    case_number_input = st.text_input("Enter Case Number")
    upload_photo = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])
    submit_button = st.button("Submit")

    if submit_button:
        if kgid_input and case_number_input and upload_photo:
            # Ensure inputs are strings for comparison
            kgid_input = str(kgid_input)
            case_number_input = str(case_number_input)

            # Check if the KGID and Case Number exist in the dataset
            if ((df["KGID"].astype(str) == kgid_input) & (df["Case Number"].astype(str) == case_number_input)).any():
                # Save the upload time in the Reported Time column
                df.loc[(df["KGID"].astype(str) == kgid_input) & (df["Case Number"].astype(str) == case_number_input), "Reported"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Save the updated dataframe to a new Excel file
                save_data(df)

                st.success("Reported Time updated successfully! Data saved to 'dataset.xlsx'.")
                st.experimental_rerun()  # Refresh the app to reflect changes automatically
            else:
                st.error("KGID and Case Number combination not found in the dataset.")
        else:
            st.error("Please enter KGID, Case Number, and upload a photo.")

    if kgid_input:
        kgid_input = str(kgid_input)
        specific_df = df[df["KGID"].astype(str) == kgid_input]

        if not specific_df.empty:
            st.write(f"Statistics for KGID: {kgid_input}")
            st.dataframe(specific_df)
        else:
            st.error("No data found for the entered KGID.")
