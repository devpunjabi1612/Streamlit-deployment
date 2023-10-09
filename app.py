import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient
import io
import base64

account_name = "teststorage298"
container_name = "test"
excel_file_name = "test.xlsx"
credentials_file_name = "credentials.xlsx"
sas_token = "sp=racw&st=2023-09-25T10:57:39Z&se=2023-10-06T18:57:39Z&spr=https&sv=2022-11-02&sr=c&sig=3YisNR21XBxKZk9TEQTJkh2e3JaNyiBdLBp1bejEBRA%3D"

blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=sas_token)
container_client = blob_service_client.get_container_client(container_name)

def read_excel_from_azure_blob(filename, sheet_name, usecols, skiprows):
    blob_client = container_client.get_blob_client(filename)
    stream = blob_client.download_blob().readall()
    return pd.read_excel(io=stream, engine='openpyxl', sheet_name=sheet_name, usecols=usecols, skiprows=skiprows)

def write_excel_to_azure_blob(df, filename, sheet_name):
    blob_client = container_client.get_blob_client(filename)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    blob_client.upload_blob(output.read(), overwrite=True)

try:
    user_credentials_df = read_excel_from_azure_blob(credentials_file_name, sheet_name="Sheet1", usecols="A:B", skiprows=0)
    user_credentials = dict(zip(user_credentials_df["Email"], user_credentials_df["Password"]))
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    user_credentials = {}



st.set_page_config(page_title="DevOps ProjectSpace Dashboard", page_icon="🔑", layout="wide")




st.sidebar.header("User Login")
username = st.sidebar.text_input("Email").lower()
password = st.sidebar.text_input("Password", type="password")



if username in user_credentials and password == user_credentials[username]:
    st.sidebar.success("Login successful")
    logged_in = True
else:
    st.sidebar.error("Invalid email or password")
    logged_in = False
###############################
# Function to export "test.xlsx" from Azure Blob Storage and provide a download link
def export_data_to_excel():
    try:
        export_filename = "test_exported.xlsx"

        # Copy file as test_exported.xlsx in our storag account
        blob_client_source = container_client.get_blob_client(excel_file_name)
        blob_client_destination = container_client.get_blob_client(export_filename)
        copy_operation = blob_client_destination.start_copy_from_url(blob_client_source.url)

        while copy_operation['copy_status'] == 'pending':
            copy_operation = blob_client_destination.get_blob_properties()

        if copy_operation['copy_status'] == 'success':
            export_blob_url = blob_client_destination.url
            href = f'<a href="{export_blob_url}" download="{export_filename}">Download</a>'

            st.write(href, unsafe_allow_html=True)
            st.success(f"Data exported successfully to '{export_filename}'.")
        else:
            st.error("Copy operation did not succeed.")
    except Exception as e:
        st.error(f"An error occurred while exporting data: {str(e)}")

#######################################################
if logged_in:
    #to access data
    df_page3 = read_excel_from_azure_blob(excel_file_name, sheet_name="page3", usecols="A:F", skiprows=0)

    st.sidebar.header("Apply Filter Here")
    subscription = st.sidebar.multiselect(
        "Select the Subscription",
        options=df_page3["Subscription_id"].unique(),
        default=df_page3["Subscription_id"].unique()
    )

    # deployment_id = st.sidebar.multiselect(
    #     "Select the Deployment_ID",
    #     options=df_page3["Deployment_id"].unique(),
    #     default=df_page3["Deployment_id"].unique()
    # )

    df_selection = df_page3.query(
        "Subscription_id == @subscription"#& Deployment_id == @deployment_id"
    )

    st.subheader("EYGS Subscription🔑 Insights for DevOps_Project_Space")
    st.dataframe(df_selection)
#################
    if st.button("Refesh and Export Data"):
        export_data_to_excel()

####################
    #add new entries
    st.subheader("Create New Entry")
    requested_date = st.text_input("Requested Date")
    subscription_name = st.text_input("Subscription Name")
    subscription_id = st.text_input("Subscription ID")
    deployment_id = st.text_input("Deployment ID")
    charge_code = st.text_input("Charge Code")
    engineer_name = st.text_input("Engineer Name")

    if st.button("Add New Entry"):
        new_entry = {
            "Requested_date": [requested_date],
            "Subscription_name": [subscription_name],
            "Subscription_id": [subscription_id],
            "Deployment_id": [deployment_id],
            "Charge_code": [charge_code],
            "Engineer_name": [engineer_name],
        }

        new_entry_df = pd.DataFrame(new_entry)
        # Append the new entry to the existing data in same page
        df_page3 = pd.concat([df_page3, new_entry_df], ignore_index=True)
        # Write the updated data back to my container
        write_excel_to_azure_blob(df_page3, excel_file_name, sheet_name="page3")
        st.success("New entry added successfully.")
else:
    st.write("Please log in to access the data.")

# if __name__ == "__main__":
#     st.run()
