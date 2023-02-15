
import plotly.express as px
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import matplotlib.pyplot as plt
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.title("Claims Data Playground")

st.markdown(
    f'''
        <style>
            .sidebar .sidebar-content {{
                width: 375px;
            }}
        </style>
    ''',
    unsafe_allow_html=True
)

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Allianz_logo.svg/2560px-Allianz_logo.svg.png", use_column_width=True)
data = st.sidebar.selectbox("Select Data Set", ("Notification Data by LOB", "Motor Claims","Broker Data"))
st.sidebar.write("As data analysts and data scientists our roles don't just involve doing some analysis on data we have - there are several steps needed to understand and prepare the data before we can do any analysis. This app will walk you through the process of preparing data and analysing it. Select a data set to begin exploring!")

if data =='Notification Data by LOB':
    st.info("A report request has come in for a report explaining the different ways claims can be notified across the different lines of business. Click add filters to begin investigating the data")
    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        modify = st.checkbox("Add filters", key="1")

        if not modify:
            return df

        df = df.copy()


        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                left.write("↳")
        
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        _min,
                        _max,
                        (_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].str.contains(user_text_input)]

        return df

    df = pd.read_csv('claims.csv')
    st.dataframe(filter_dataframe(df))
    st.header("Data Summaries")
    st.info("Now you have investigated the data available, it is time to check the data quality - review the following summaries and check whether there might be any issues with the data before we use it to create a report") 
    if st.checkbox("Data Summaries", key="9"):
        option = st.selectbox("Select a Column to Summarise", ("Line of Business", "Notification Type", "Claim Status"))
        if option == "Line of Business":
            st.write(df["Line of Business"].value_counts())
        if option == "Notification Type":
            st.write(df["Notification Type"].value_counts())
        if option == "Claim Status":
            st.write(df["Claim Status"].value_counts())
    if st.button("Summary Statistics"):
        st.write(df.describe().T)
        st.info("What do you notice about the difference in the total count of claims references compared to the unique count of claims references? What do you think this could mean?")

    st.header("Data Cleansing")
    st.info("As you may have noted from your initial investigation of the data and from the data summaries you may have spotted that the data contains duplicates and incomplete references. Unfortunately we are unable to complete any data analysis and visualisation until these are removed")
    if st.checkbox("Find Duplicated Claims"):
        duplicates = df[df["Claim reference"].duplicated()]
        st.write(duplicates)
        st.write("It is really important to ensure duplicate data is removed from any data set (known as 'deduping') to preserve data quality and make sure analysis isn't skewed")

    if st.checkbox("Find incomplete claim references"):
        incomplete = df[df['Claim reference'].apply(lambda x: len(x) < 8)]
        st.write(incomplete)
        st.write("Identifying & removing or correcting invalid data is important as we often join data from multiple different sources so it is important records match - we have advanced tools to correct some invalid data but it can also be excluded which is what we will do here")

    if st.checkbox("Remove duplicated or incomplete data"):
        df = df.drop_duplicates(subset = "Claim reference")
        df = df[df['Claim reference'].map(len) > 7]
        st.write(df)
        st.write("We are now ready to do some data analysis")


    st.header("Data Analysis")
    st.info("Now we have investigated and cleansed the data it is time to create some visualisations of the data to best provide the stakeholders with the information they requested. Choose the columns and try to different types of chart to decide how to best represent how claims are notified across the different lines of business")
    df = df.drop_duplicates(subset = "Claim reference")
    df = df[df['Claim reference'].map(len) > 7]
    plots = st.selectbox("Select Type of Plot",("Bar","Pie"))
    columns = ("Line of Business", "Notification Type") 
    select_column_X = st.selectbox("Select Columns To Plot", columns)
    if plots =="Bar" and select_column_X =="Line of Business" and st.button("Generate Plot"):
        lob_bar_chart = alt.Chart(df).mark_bar().encode(alt.X("Line of Business"), y="count()", color="Notification Type")
        st.altair_chart(lob_bar_chart, use_container_width=True)
        st.success("That's correct! Both versions of the bar chart are a good way of visualising the data, take the time to look at how switching the axes changes the focus of how the data is represented then move onto the next data set")

    elif plots =="Bar" and select_column_X =="Notification Type" and st.button("Generate Plot"):
        not_bar_chart = alt.Chart(df).mark_bar().encode(alt.X("Notification Type"),y="count()", color="Line of Business")
        st.altair_chart(not_bar_chart, use_container_width=True)
        st.success("That's correct! Both versions of the bar chart are a good way of visualising the data, take the time to look at how switching the axes changes the focus of how the data is represented then move onto the next data set")

    elif plots == "Pie" and select_column_X == "Line of Business" and st.button("Generate Plot"):
        labels = ["Motor", "Casualty", "PI", "Property"]
        values = [22,16,15,9]
        fig1, ax1 = plt.subplots()
        ax1.pie(values, labels=labels, autopct='%1.1f%%',startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
        st.warning('This might not be the best way to represent the data, the request wanted to see the notification types across the different lines of business - have another go', icon="🚨")

    elif plots == "Pie" and select_column_X == "Notification Type" and st.button("Generate Plot"):
        labels = ["Email", "Telephone", "Post", "MOJ","OIC"]
        values = [18,17,12,9,6]
        fig2, ax2 = plt.subplots()
        ax2.pie(values, labels=labels, autopct='%1.1f%%',startangle=90)
        ax2.axis('equal')
        st.pyplot(fig2)
        st.warning('This might not be the best way to represent the data, the request wanted to see the notification types across the different lines of business - have another go', icon="🚨")
    

    
    
if data =='Motor Claims':
    st.info("A request has come in for a report on the number of claims with PI & credit hire broken down by blame code.  Click add filters to begin investigating the data") 
    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        modify = st.checkbox("Add filters", key="8")

        if not modify:
            return df

        df = df.copy()


        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                left.write("↳")
        
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        _min,
                        _max,
                        (_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].str.contains(user_text_input)]

        return df

    df = pd.read_csv('PICHclaims.csv')
    st.dataframe(filter_dataframe(df))

    st.header("Data Summaries")
    st.info("Now you have investigated the data available, it is time to check the data quality - review the following summaries and check whether there might be any issues with the data before we use it to create a report") 
    if st.checkbox("Data Summaries",key="4"):
        option = st.selectbox("Select a Column to Summarise", ("Blame Code", "Vehicle Make", "PI Indicator", "CH Indicator"))
        if option == "Blame Code":
            st.write(df["Blame Code"].value_counts())
        if option == "Vehicle Make":
            st.write(df["Vehicle Make "].value_counts())
        if option == "PI Indicator":
            st.write(df["PI Indicator"].value_counts())
        if option == "CH Indicator":
            st.write(df["CH Indicator"].value_counts())
    if st.button("Summary Statistics"):
        st.write(df.describe().T)
        st.info("What do you notice about the difference in the total count of claims references compared to the unique count of claims references? What do you think this could mean?")
    st.header("Data Cleansing")
    st.info("As you have may have noticed from investigating the data and the data summarisations there are some data quality issues. Like the notification data set we have some duplicated and incomplete claims references that will need removing. You may have spotted from the data summary of the Vehicle Make columns there are also some typos in the vehicle make names and these will need corecting before we can create a report")
    if st.checkbox("Remove duplicated or incomplete data"):
        df = df.drop_duplicates(subset = "Claim reference")
        df = df[df['Claim reference'].map(len) > 7]
        st.write(df)
    

    if st.checkbox("Correct Vehicle makes"):
        df = df.drop_duplicates(subset = "Claim reference")
        df = df[df['Claim reference'].map(len) > 7]
        df["Vehicle Make "] = df["Vehicle Make "].replace(['Mercedes','VW','Vord','Mercedes-Benz','Scoda', 'Peugot'],['Mercedes Benz', 'Volkswagen','Ford', 'Mercedes Benz', 'Skoda', 'Peugeot'])
        st.write(df["Vehicle Make "].value_counts())

    st.header("Data Analysis")
    st.info('Now we have cleansed the data we can select columns to visualise the data to produce a report on the number of claims with PI and credit hire split by blame code. Use the select box to select the columns and generate a graph')
    options = st.multiselect('Select Columns', ['PI Indicator', 'CH Indicator', 'Blame Code', 'Vehicle Make'])
    if options == ['PI Indicator', 'CH Indicator', 'Blame Code'] and st.button("Generate Plot"):
        df = pd.DataFrame([['PI', 'Driver', 11], ['PI', 'Both', 5], ['PI', 'Third Party', 6], ['CH', 'Driver', 8], ['CH', 'Both', 5], ['CH', 'Third Party', 8]], columns=['PI/CH', 'Blame Code', 'Count of Claims'])
        chart = alt.Chart(df).mark_bar().encode(x='Blame Code', y='Count of Claims', color='PI/CH')
        st.altair_chart(chart, use_container_width=True)
    
                             
    

if data =='Broker Data':
    st.info("A request has come in for a report on the lifecycle and notification time of claims across different lines of business. Click 'add filters' to begin exploring the data set") 
    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        modify = st.checkbox("Add filters", key="5")

        if not modify:
            return df

        df = df.copy()


        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                left.write("↳")
        
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        _min,
                        _max,
                        (_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].str.contains(user_text_input)]

        return df

    df = pd.read_csv('broker.csv')
    st.dataframe(filter_dataframe(df))
    st.header("Data Summaries")
    st.info("Now you have investigated the data available, it is time to check the data quality - review the following summaries and check whether there might be any issues with the data before we use it to create a report") 
    if st.checkbox("Data Summaries", key="9"):
        option = st.selectbox("Select a Column to Summarise", ("Claim Reference", "Broker Account Number", "Policy Number"))
        if option == "Claim Reference":
            st.write(df["Claim reference"].value_counts())
        if option == "Broker Account Number":
            st.write(df["Broker Account Number"].value_counts())
        if option == "Policy Number":
            st.write(df["Policy Number"].value_counts())
    if st.button("Summary Statistics"):
        st.write(df.describe().T)
        st.info("What do you notice about the broker account and policy number formats? Are they all the same or does there look like there might be some data quality issues?")

    st.header("Data Cleansing")
    st.info("As you have may have noticed from investigating the data and the data summarisations there are some data quality issues. Like the previous data sets we have some duplicated and missing claims references that will need removing. You may have spotted from the data summaries  there are some columns with fields that are missing or filled in incorrectly. For the ones that are swapped we will be able to correct the data, however for those filled in incorrectly or left blank we will have to exclude this data from our analysis before we are able to produce a report")
    if st.checkbox("Remove duplicated or incomplete data"):
        df = df.drop_duplicates(subset = "Claim reference")
        df = df.astype({"Claim reference": 'str'})
        df = df[df['Claim reference'].map(len) > 7]
        st.write(df)

    st.info("You may have also noticed that some of the fields have been incorrectly filled out or left blank. We have developed a dedicated reference cleansing algorithm within Claims data however applcation of this in this exercise would be too complicated so we will simply remove incorrectly filled out fields")
    if st.checkbox("Remove incomplete fields"):
        df = df.dropna()
        df["Broker Account Number"] = df["Broker Account Number"].replace(['PK12488'],['68623'])
        df["Policy Number"] = df["Policy Number"].replace(['68623'],['PK12488'])
        df.drop(df.loc[df['Broker Account Number']== 'X'].index, inplace=True)
        st.write(df)

    st.header("Data Analysis")
    st.info("We have now sufficiently prepared the data so that the information requested can be provided. In this exercise you will create a pivot table to show the average notification times and claim lifecycles split by line of business and then by broker account nunmber")
    df = df.drop_duplicates(subset = "Claim reference")
    df = df.astype({"Claim reference": 'str'})
    df = df[df['Claim reference'].map(len) > 7]
    df = df.dropna()
    df["Broker Account Number"] = df["Broker Account Number"].replace(['PK12488'],['68623'])
    df["Policy Number"] = df["Policy Number"].replace(['68623'],['PK12488'])
    df.drop(df.loc[df['Broker Account Number']== 'X'].index, inplace=True)
    df = df.dropna()
    rows = st.multiselect('Select Rows', ['Broker Account Number', 'Policy Holder', 'Line of Business'])
    columns = st.multiselect('Select Columns', [ 'Notification Time', 'Lifecycle'])
    if rows ==['Line of Business'] and columns ==['Notification Time', 'Lifecycle']:
        pivot = pd.pivot_table(df, values=['Notification Time', 'Lifecycle'], index =['Line of Business'], aggfunc={'Notification Time':np.mean, 'Lifecycle':np.mean})
        st.write(pivot)
    if rows ==['Broker Account Number'] and columns ==['Notification Time', 'Lifecycle']:
        pivot = pd.pivot_table(df, values=['Notification Time', 'Lifecycle'], index =['Broker Account Number'], aggfunc={'Notification Time':np.mean, 'Lifecycle':np.mean})
        st.write(pivot)
    if rows ==['Broker Account Number', 'Line of Business'] and columns ==['Notification Time', 'Lifecycle']:
        pivot = pd.pivot_table(df, values=['Notification Time', 'Lifecycle'], index =['Broker Account Number', 'Line of Business'], aggfunc={'Notification Time':np.mean, 'Lifecycle':np.mean})
        st.write(pivot)
    
    


    st.header("Data Joins")
    st.info("We have now been asked to match broker names to the account numbers in the report. Unfortunately not all data is always included in a single data set so in order to complete reports we often join 2 or more datasets together in order to incorporate all the information required for the report")
    df_b = pd.read_csv("brokeraccount.csv")
    df["Broker Account Number"] = df["Broker Account Number"].astype(str)
    st.dataframe(df_b)
    st.info("Here we have a dataset containing the broker account numbers and the names of the Brokers these account numbers relate to - we will need to join this on to the dataset above")
    
    dataset = st.multiselect('Select data set to join', ['Broker Data', 'Broker Names'])
    col = df.columns.values.tolist()
    st.selectbox('Select a column to join the data on',col)
    if dataset ==['Broker Data', 'Broker Names'] and col ==['Broker Account Number']:
        @st.cache
        def clean_df(data):
            df = df.drop_duplicates(subset = "Claim reference")
            df = df.astype({"Claim reference": 'str'})
            df = df[df['Claim reference'].map(len) > 7]
            df = df.dropna()
            df["Broker Account Number"] = df["Broker Account Number"].replace(['PK12488'],['68623'])
            df["Policy Number"] = df["Policy Number"].replace(['68623'],['PK12488'])
            df.drop(df.loc[df['Broker Account Number']== 'X'].index, inplace=True)
            df = df.dropna()
            return df
    df_b = pd.read_csv("brokeraccount.csv")
    df_b.dropna()
    df["Broker Account Number"] = df["Broker Account Number"].astype(int)
    df_brokers = pd.merge(df,df_b,how='left')
    st.dataframe(df_brokers)
    st.info("We are now able to complete the request - select the rows and columns to create the pivot table showing the average lifecycle and notification times split by Broker name and line of business")
    row = st.multiselect('Select Rows', ['Broker Account Number', 'Broker Name', 'Line of Business'], key="12")
    column = st.multiselect('Select Columns', [ 'Notification Time', 'Lifecycle'], key="13")
    if row ==['Line of Business'] and column ==['Notification Time', 'Lifecycle']:
        pivot = pd.pivot_table(df_brokers, values=['Notification Time', 'Lifecycle'], index =['Line of Business'], aggfunc={'Notification Time':np.mean, 'Lifecycle':np.mean})
        st.write(pivot)
    if row ==['Broker Name'] and column ==['Notification Time', 'Lifecycle']:
        pivot = pd.pivot_table(df_brokers, values=['Notification Time', 'Lifecycle'], index =['Broker Name '], aggfunc={'Notification Time':np.mean, 'Lifecycle':np.mean})
        st.write(pivot)
    if row ==['Broker Name', 'Line of Business'] and column ==['Notification Time', 'Lifecycle']:
        pivot = pd.pivot_table(df_brokers, values=['Notification Time', 'Lifecycle'], index =['Broker Name ', 'Line of Business'], aggfunc={'Notification Time':np.mean, 'Lifecycle':np.mean})
        st.write(pivot)
        
    st.header("Data Visualisation")
    st.info("A good way to visualise this data with be with use of a box plots. Box plots are useful tools to show the spread of a data set. The 'box' of the plot holds the middle 50% of the data set - the longer the box means the middle values of the data set are spread further apart (i.e. have a wider range of values), if the box is short it means the middle values of the data set are all quite close together. The line that divides the box is the median - this shows the middle value of the date set. The line below the box shows the bottom 25% of values of the data set, the line at the bottom indicates the minimum value of the data set. Likewise the line above the box shows the top 25% of the data set with the line at the top showing the maximum value of the data set.")      
    fig1 = px.box(df_brokers, x='Line of Business', y='Notification Time')
    st.plotly_chart(fig1, use_container_width=True)
    range = st.selectbox("Which Line of Business has the biggest range of notification times?", ('Motor', 'Casualty','PI','Property'))
    if range ==['Motor']:
        st.success('That is correct!',icon="✅")
    elif range==['Casualty']:
        st.error('Not quite, have a look at which box plot has the longest lines',icon="🚨")
    elif range==['PI']:
        st.error('Not quite, have a look at which box plot has the longest lines',icon="🚨")
    elif range==['Property']:
        st.error('Not quite, have a look at which box plot has the longest lines',icon="🚨")
    st.info("Box plots are also useful tools to identify unusual values within a data set - these are values that differ notably for the main set of data generally because they are either unusually large or unusually small values. These are represented as dots above or below the main plot.")   
    fig2 = px.box(df_brokers, x='Line of Business', y='Lifecycle')
    st.plotly_chart(fig2, use_container_width=True)
    lob = df_brokers["Line of Business"].unique()
    
  
    
    if st.button("Complete Section"):
        st.balloons()
    


        
