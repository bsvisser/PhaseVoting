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
#import df2gspread as d2g


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
    

        
    # Initialize session state
    if 'numbers' not in st.session_state:
         st.session_state.numbers = []
    
    @st.cache_resource 
    def read_images(IMAGE_LIST_PATH):
        with open(IMAGE_LIST_PATH, 'r') as f:
            image_list = f.read().strip().split(",")
        return image_list
    
    IMAGE_LIST_PATH = r'./file_list.csv'
    image_list = read_images(IMAGE_LIST_PATH)
    
    # Generate random numbers if list is empty
    if not st.session_state.numbers:
         st.session_state.numbers = image_list
         random.shuffle(st.session_state.numbers)
    
    # Define the path for the CSV file
    CSV_PATH = 'E://data_quiz.csv'
    
    # Define the function to load the data from the CSV file
    @st.cache_resource
    def load_data(CSV_PATH):
        worksheet = gc.open_by_key(spreadsheet_key).get_worksheet(0)
        dataframe = pd.DataFrame(worksheet.get_all_records())
        return dataframe, worksheet
    
    # Define the function to save the data to the CSV file
    def save_data(worksheet, df):
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    
    
    # Define the main Streamlit app
    
    st.title('Image Classification')
    
    # Load the data from the CSV file
    data, worksheet = load_data(CSV_PATH)
               
    if len(image_list) == 0:
        st.write('No more images, clear cache to load all images again')
        if st.button("Clear cache", key = "Cache"):
            st.cache_resource.clear()
            st.experimental_rerun()
    else:
        random_image = random.choice(image_list)
    
    
    # Choose a number to remove
    selected_number = st.session_state.numbers[0]
    base_url = st.secrets["base_url"]
    IMAGE_URL = f'{base_url}{selected_number}'
    response = requests.get(IMAGE_URL)
    image = Image.open(BytesIO(response.content))
    st.image(image, width = 256)
    
    # Create two columns for the buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    
    # Show the buttons for the user to answer
    if col1.button('Coacervate', key="Coacervate"):
        data.loc[len(data)] = [random_image, 'coacervate']
        save_data(worksheet, data)
        image_list.remove(random_image)
        st.session_state.numbers.remove(selected_number)
        

    if col2.button('Solution', key="Solution"):
        data.loc[len(data)] = [random_image, 'solution']
        save_data(worksheet, data)
        st.session_state.numbers.remove(selected_number)
    
    if col3.button('Aggregate', key="Aggregate"):
        data.loc[len(data)] = [random_image, 'Aggregate']
        save_data(worksheet, data)
        st.session_state.numbers.remove(selected_number)

    
    if col4.button('Gel', key="Gel"):
        data.loc[len(data)] = [random_image, 'gel']
        save_data(worksheet, data)
        st.session_state.numbers.remove(selected_number)
        
    if col4.button('Skip', key="Skip"):
        data.loc[len(data)] = [random_image, 'Skip']
        save_data(worksheet, data)
        st.session_state.numbers.remove(selected_number)


    
    # Show the remaining number of images
    if len(image_list) == 0:
        st.write('No more images, clear cache to load all images again')
        if st.button("Clear cache", key = "Cache"):
            st.cache_resource.clear()
            st.experimental_rerun()
    else:
        random_image = random.choice(image_list)
    #st.write(f'{len(image_list)} images remaining')

# to do: upload images to server, test script
# upload script to github and deploy with ecrets
#check if writing still works..
# add skip button