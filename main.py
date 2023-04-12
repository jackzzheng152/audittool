
import streamlit as st
import pandas as pd
import statsmodels.api as sm
import base64
import xlsxwriter
from io import BytesIO

st.set_page_config(page_title="Audit Tool", page_icon = ":toolbox:", layout="wide")
#Load Asset
#df = pd.read_excel("data.xlsx")
def download_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="workpaper.xlsx">Download Excel File</a>'
    return href
def graph(dataframe):
    ng_conversion = 0.0551
    list = []
    #populates a new list to append to the dataframe
    for i in range(len(dataframe['NG'])):
        list.append(dataframe['NG'][i]/1000*ng_conversion)
    dataframe['Conversion'] = list

    X = dataframe['NG']
    y = dataframe['CO2 Emissions (metric tons)']

    X = sm.add_constant(X)
    model = sm.OLS(y, X)
    results = model.fit()

    slope = results.params['NG']
    intercept = results.params['const']
    #populates the y variable based on regression coefficients
    x = dataframe['NG']
    y_pred = slope*x + intercept
    dataframe['Regression'] = y_pred
    return dataframe



def materialitycheck(dataframe):
    d1 = abs(dataframe['Conversion']-dataframe['CO2 Emissions (metric tons)'])
    d2 = abs(dataframe['Regression']-dataframe['CO2 Emissions (metric tons)'])
    average = 0.7*d1+0.3*d2
    dataframe['Deviation'] = average
    return average

with st.container():
    left_title, right_title = st.columns([8,1])
    st.markdown("""
                <style>
                       .block-container {
                            padding-top: 1rem;
                            padding-bottom: 0rem;
                            padding-left: 5rem;
                            padding-right: 5rem;
                        }
                        .css-otxysd.egzxvld1
                        {
                            visibility: hidden;
                        }
                </style>
                """, unsafe_allow_html=True)
    with left_title:
        st.title("Deloitte:green[.]")
        st.subheader("Audit Tool With :green[OmniaAI]")
    with right_title:
        st.title("RD:green[.]IE")
with st.container():
    left_body, right_body = st.columns([2.3,1])

    with right_body:
        st.subheader("Upload File")
        uploaded_file = st.file_uploader("")
        st.write("---")
        st.subheader("Set Materiality")
        materiality = st.number_input("")
        st.write("---")
        st.subheader("Results")
        if uploaded_file is not None:
            df1 = pd.read_excel(uploaded_file)
            df1 = graph(df1)
            average = materialitycheck(df1)
            for i in range(len(average)):
                if average[i] > materiality:
                    st.write(f'{df1["Month"][i]} is over the materiality limit')
        if st.button("Populate Workpapers") and uploaded_file is not None:
            st.markdown(download_excel(df1), unsafe_allow_html=True)

    with left_body:
        st.subheader("CO2 Emissions")
        st.selectbox("",('1D','1W','1M','3M','YTD','1Y','ALL'))
        if uploaded_file is not None:
            st.line_chart(df1,x="Month", y=["Conversion","Regression", "CO2 Emissions (metric tons)"],height=500)
            st.dataframe(df1, width=1400)




