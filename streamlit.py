import streamlit as st
import pandas as pd
from SQLAlchemyORM import read_data
import plotly.express as px

full_data = read_data()
year = st.slider('Year', min_value= 2006, max_value=2023, value=[2006,2023])

st.session_state.columns = {}
ignore_columns = ["year", "title", "subtitle"]

with st.expander(label='Filters',expanded=False):
    for col in full_data.columns:
        if col not in ignore_columns:
            values = sorted(pd.unique(full_data[col]), key=lambda x: (x is None, str(x)),reverse=False)
            st.session_state.columns[col] = st.multiselect(col,values)

filtered_data = read_data(start_year=year[0], end_year=year[1],
                          seasons= st.session_state.columns["season"],
                          genres=st.session_state.columns["genres"],
                          studios=st.session_state.columns["studios"],
                          source=st.session_state.columns["source"],
                          themes=st.session_state.columns["themes"],
                          demographics=st.session_state.columns["demographics"])

filtered_data['year'] = filtered_data["year"].astype(str)

season_order = ["Spring","Summer","Fall","Winter"]
filtered_data["season"] = pd.Categorical(filtered_data['season'], categories=season_order, ordered=True)
filtered_data = filtered_data.sort_values(['year', 'season']).reset_index()

filtered_data['year_season'] = filtered_data['year'].astype(str) + ' - ' + filtered_data['season'].astype(str)

line_chart = filtered_data.groupby(["year_season"],sort=False)["title"].count()

chart, data = st.tabs(["Chart", "Data"])

with chart:
    st.plotly_chart(px.line(line_chart))


with data:
    st.write(filtered_data)

