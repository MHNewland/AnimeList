import streamlit as st
import pandas as pd
from SQLAlchemyORM import read_data, create_database

year = st.slider('year', min_value= 2006, max_value=2023, value=[2006,2023])
st.write(read_data(start_year=year[0], end_year=year[1]))