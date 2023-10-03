from azure.storage.blob import  BlobClient
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import io
from streamlit_card import card
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.title('Owner-Details')

#blob_url_with_sas =f"https://deployfirstmhg.blob.core.windows.net/excel-data/test.txt?sp=r&st=2023-09-07T09:32:19Z&se=2023-09-07T17:32:19Z&sv=2022-11-02&sr=b&sig=1Ao%2BxVb3cujw0zPU1E%2FTVa72qmo08san4YIAN4OWRKU%3D"
blob_url_with_sas = f"https://deployfirstmhg.blob.core.windows.net/excel-data/Subscription_Correction_23rdAug2023.csv?sp=r&st=2023-09-08T08:17:20Z&se=2024-09-08T16:17:20Z&sv=2022-11-02&sr=b&sig=ahWdT9mDuGQrumd%2FEd2E%2FMd7oGf4mLoy1fC82c7BKv8%3D"
# def index():
#     data = get_Data()
#     count = sub_count()

    
# def sub_count():


def get_Data():    
    try:
        # Create a BlobClient usinSg the blob URL with SAS token
        blob_client = BlobClient.from_blob_url(blob_url_with_sas)

        # Download the blob's content as storagesteam to text conversion

        blob_data = blob_client.download_blob()  # returne storagestream object
        #print(blob_data)
        blob_text = blob_data.readall() 
        #print(type(blob_text))        # converts to byte
        # print("here")
        #dt =  io.BytesIO(blob_text)                 # tries to read bytes data from IO memory 
        df = pd.read_csv(io.BytesIO(blob_text)) 
        df_first_100 = df.head(10)
          # using
        #print(df)    
        # Render the Excel data in an HTML template (assuming you are working with Excel data)
        #return render_template('excel_template.html', data=df_first_100 )
        return df
       
        #table_html = df.to_html(classes='table table-section', header='table-header', index=False)
        
        #print(table_html)
        #return render_template('table.html', table=table_html)

    except Exception as e:
        return f"An error occurred: {str(e)}"
 
def card():
    return f""" 
            <section class="intro">   
                <div class="row">
                    <div class="card text-white bg-primary col-lg-6 m-2" style="max-width: 18rem;">
                        <div class="card-header">Azure Subscriptions Count</div>
                        <div class="card-body">
                        <h5 class="card-title">Total Subscriptions Count</h5>
                        <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
                        </div>
                    </div>
                    <div class="card text-white bg-danger col-lg-6 m-2" style="max-width: 18rem;">
                        <div class="card-header"> Owner change Count</div>
                        <div class="card-body">
                        <h5 class="card-title">Subscriptions whose Owner to be changed</h5>
                        <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
                        </div>
                    </div>
                </div>
            </section>
"""
def draw_pie(o_count):
    Od= ['Unchanged-Owner', 'Owner-tobeChanged']
    values= [1000, o_count]

    fig = go.Figure(
        go.Pie(
        labels = Od,
        values = values,
        hoverinfo = "label+percent",
        textinfo = "value"
    ))
    st.header("Pie chart")
    st.plotly_chart(fig)


def filter_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    # owners = data['SubOwner'].unique()
    # filter_owners = st.selectbox('filter_Owners', owners)
    # filter_data =data[data['SubOwner'] == filter_owners]

    #modify = st.checkbox("Add filters")
    modify = st.checkbox("Add filters")

    if not modify:
        return data

    df = data.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
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
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            else:
                user_text_input = right.text_input(f"Substring or regex in {column}",)
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


data = get_Data()

st.markdown(""" 
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9" crossorigin="anonymous">
            
            """,unsafe_allow_html = True)
st.markdown(card(), unsafe_allow_html = True)
owner = data['SubOwner']
owner_change_count = owner.count()
draw_pie(owner_change_count)
st.subheader('Subscription-details')
st.dataframe(filter_dataframe(data))











