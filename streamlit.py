import streamlit as st
import pandas as pd
from SQLAlchemyORM import *
import plotly.express as px
#import time


def get_data():
    # print('\n\n\n\n\ngetting full table')
    # start_time = time.time()
    st.session_state.joined_tables, st.session_state.sql_session = get_full_table()
    # end_time = time.time()
    # print(f'time: {end_time-start_time}')

    # start_time = time.time()
    # print('getting full data')
    st.session_state.data_table, st.session_state.sql_session = read_data(
        joined_tables=st.session_state.joined_tables, 
        session=st.session_state.sql_session)
    st.session_state.full_data, st.session_state.sql_session = execute_table(
        st.session_state.data_table,
        st.session_state.sql_session)
    # end_time = time.time()
    # print(f'time: {end_time-start_time}')

    # start_time = time.time()
    # print('making dataframe')
    st.session_state.full_data = pd.DataFrame(
        st.session_state.full_data,
        dtype=object)
    # end_time = time.time()
    # print(f'time: {end_time-start_time}')

    # start_time = time.time()
    # print('filling n/a with "none"')
    st.session_state.full_data.fillna('None', inplace=True)
    # end_time = time.time()
    # print(f'time: {end_time-start_time}')


def create_filters():
    st.session_state.year = st.slider('Year', min_value= 2006, max_value=2022, value=[2006,2022])
    st.session_state.columns = {}
    st.session_state.ignore_columns = ['year', 'title', 'subtitle']

    # start_time = time.time()
    # print("creating filters")
    with st.expander(label='Filters',expanded=False):
        st.session_state.columns['title'] = st.text_input('Title/subtitle:')
        for col in st.session_state.full_data.columns:
            if col not in st.session_state.ignore_columns:
                values = sorted(pd.unique(st.session_state.full_data[col]))
                st.session_state.columns[col] = st.multiselect(col,values)
    # end_time = time.time()
    # print(f'time: {end_time-start_time}')

def display_data():
    # start_time = time.time()
    # print("getting filtered data")
    st.session_state.filtered_table, st.session_state.sql_session = filter_data(
                                start_year=st.session_state.year[0],
                                end_year=st.session_state.year[1],
                                title=st.session_state.columns['title'],
                                seasons= st.session_state.columns['season'],
                                genres=st.session_state.columns['genres'],
                                studios=st.session_state.columns['studios'],
                                source=st.session_state.columns['source'],
                                themes=st.session_state.columns['themes'],
                                demographics=st.session_state.columns['demographics'],
                                session=st.session_state.sql_session,
                                joined_tables=st.session_state.joined_tables)
    # end_time = time.time()
    # print(f'time: {end_time-start_time}')

    # start_time = time.time()
    # print('making filtered dataframe')
    st.session_state.filtered_data_table, st.session_state.sql_session = execute_table(
        st.session_state.filtered_table, 
        st.session_state.sql_session)
    
    st.session_state.filtered_data = pd.DataFrame(
        st.session_state.filtered_data_table,
        dtype=object)
    # end_time = time.time()
    # print(f'time: {end_time-start_time}')


    if len(st.session_state.filtered_data)==0:
        st.write('No data found.')
    else:
        # start_time = time.time()
        # print('converting year to string')        
        st.session_state.filtered_data['year'] = st.session_state.filtered_data['year'].astype(str)
        # end_time = time.time()
        # print(f'time: {end_time-start_time}')

        # start_time = time.time()
        # print('sorting data')
        season_order = ['Spring','Summer','Fall','Winter']
        st.session_state.filtered_data['season'] = pd.Categorical(st.session_state.filtered_data['season'], categories=season_order, ordered=True)
        st.session_state.filtered_data = st.session_state.filtered_data.sort_values(['year', 'season', 'title']).reset_index()
        # end_time = time.time()
        # print(f'time: {end_time-start_time}')
        
        #creating another dataframe as plotly can't do multi-index graphing
        # start_time = time.time()
        # print("grouping data")
        st.session_state.grouped_table, st.session_state.sql_session = execute_table(
            group_table(st.session_state.filtered_table, groupby=['year', 'season','title']),
            st.session_state.sql_session)
        
        st.session_state.grouped_data = pd.DataFrame(
            st.session_state.grouped_table,
            dtype=object)
        # end_time = time.time()
        # print(f'time: {end_time-start_time}')

        # start_time = time.time()
        # print('creating grouped column')
        st.session_state.grouped_data['year_season'] = st.session_state.grouped_data['year'].astype(str) + \
                                            ' - ' + st.session_state.grouped_data['season'].astype(str)
        # end_time = time.time()
        # print(f'time: {end_time-start_time}')

        # start_time = time.time()
        # print('generating line_chart data')
        st.session_state.line_chart = st.session_state.grouped_data.groupby('year_season')['title'].count()
        # end_time = time.time()
        # print(f'time: {end_time-start_time}')

        chart, data = st.tabs(['Chart', 'Data'])

        with chart:
            # start_time = time.time()
            # print('drawing chart')
            line_len = len(st.session_state.line_chart)
            fig=None
            match line_len:
                case 0:
                    st.write('No results found')
                case 1:
                    fig = px.scatter(st.session_state.line_chart)
                case _:
                    fig = px.line(st.session_state.line_chart)
            
            if fig !=None:
                st.plotly_chart(fig)
            # end_time = time.time()
            # print(f'time: {end_time-start_time}')

        with data:
            # start_time = time.time()
            # print('displaying database')
            st.write(st.session_state.filtered_data)
            # end_time = time.time()
            # print(f'time: {end_time-start_time}')

with st.form("test"):
    try:
        data = st.session_state.full_data
    except Exception as e:
        get_data()
    
    try:
        st.slider(st.session_state.year)
        with st.expander(label='Filters',expanded=False):
            st.session_state.columns['title'] = st.text_input('Title/subtitle:')
            for col in st.session_state.columns:
                if col not in st.session_state.ignore_columns:
                    st.multiselect(col,st.session_state.columns[col]) 
    except Exception as e:
        create_filters()
        

    submit = st.form_submit_button("Submit")
    if submit:
        display_data()
