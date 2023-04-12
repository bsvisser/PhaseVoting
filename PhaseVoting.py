# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 21:11:44 2023
@author: Brent Visser
"""
import streamlit as st
import pandas as pd
import random
import gspread
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    @st.cache_resource
    def google_connect():
        credentials = st.secrets["credentials"]
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        gc = gspread.service_account_from_dict(credentials)
        print(st.secrets)
        spreadsheet_key = st.secrets["urlkey"]
        return gc, spreadsheet_key
        
    gc, spreadsheet_key = google_connect()
 
    
    @st.cache_resource 
    def read_images(IMAGE_LIST_PATH): # read list of images present
        with open(IMAGE_LIST_PATH, 'r') as f:
            image_list = f.read().strip().split(",")
        base_url = st.secrets["base_url"]
        return image_list, base_url
    
    IMAGE_LIST_PATH = r'./file_list.csv'
    image_list, base_url = read_images(IMAGE_LIST_PATH)
    
    # Initialize session state numbers
    if 'numbers' not in st.session_state:
         st.session_state.numbers = []
    if not st.session_state.numbers:
         st.session_state.numbers = image_list
         random.shuffle(st.session_state.numbers)
         selected_number = st.session_state.numbers[0]
       
    # Define the function to load the data from the Drive sheet
    def load_data():
        worksheet = gc.open_by_key(spreadsheet_key).get_worksheet(0)
        dataframe = pd.DataFrame(worksheet.get_all_records())
        return dataframe, worksheet
    
    # Define the function to save the data to the CSV file
    def save_data(worksheet, df):
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.session_state.numbers.pop(0)
        new_image()

        
    # Define the main Streamlit app

    st.title('Image Classification')

    # Choose a number to remove
    def new_image():
        with st.spinner('Saving & Loading next image...'):
            IMAGE_URL = f'{base_url}{st.session_state.numbers[0]}'
            response = requests.get(IMAGE_URL)
            image = Image.open(BytesIO(response.content))
            st.image(image, width = 512,caption=st.session_state.numbers[0])    

    # Load the data from the CSV file
    data, worksheet = load_data()
        

    if st.button("Start", key="start"):
        save_data(worksheet, data)
    # Create 5 columns for the buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Show the buttons for the user to answer
    if col1.button('Coacervate', key="Coacervate"):
        data.loc[len(data)] = [st.session_state.numbers[0], 'coacervate', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        save_data(worksheet, data)
        
    if col2.button('Solution', key="Solution"):
        data.loc[len(data)] = [st.session_state.numbers[0], 'solution', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        save_data(worksheet, data)
        
    if col3.button('Aggregate', key="Aggregate"):
        data.loc[len(data)] = [st.session_state.numbers[0], 'Aggregate', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        save_data(worksheet, data)
        
    if col4.button('Gel', key="Gel"):
        data.loc[len(data)] = [st.session_state.numbers[0], 'gel', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        save_data(worksheet, data)
        
    if col4.button('Skip', key="Skip"):
        data.loc[len(data)] = [st.session_state.numbers[0], 'Skip', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        save_data(worksheet, data)

    
    # Show the remaining number of images
    if len(st.session_state.numbers) == 0:
        st.write('No more images, clear cache to load all images again')
        if st.button("Clear cache", key = "Cache"):
            st.cache_resource.clear()
            st.experimental_rerun()
    st.write(f'{len(st.session_state.numbers)} images in session (no, you don\'t have to answer them all :) )')
