import pandas as pd
import streamlit as st
import plotly.express as px
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart", layout="wide")

st.title(" :bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

file = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt", "xlsx", "xls"]))
if file is not None:
    filename = file.name

    if filename.endswith('.csv') or filename.endswith('.txt'):
        file = pd.read_csv(file)
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        file = pd.read_excel(file)
    else:
        st.error("Unsupported file format")   

    st.write("ALL DATA", file.head(1)) 

else:
    st.write("Please upload a file to proceed.")    
    
col1, col2 = st.columns(2)
file["Order Date"] = pd.to_datetime(file["Order Date"])

startDate = pd.to_datetime(file["Order Date"]).min()
endDate = pd.to_datetime(file["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

file = file[(file["Order Date"] >= date1) & (file["Order Date"] <= date2)].copy()

#create a sidebar and a region filter
st.sidebar.header("Choose your filter: ")
selectedregion = st.sidebar.multiselect("Pick your Region: ", file["Region"].unique())
if not selectedregion:
    file2 = file.copy()
else:
    file2 = file[file["Region"].isin(selectedregion)]

#create a state filter
selectedstate = st.sidebar.multiselect("Pick a State: ", file2["State"].unique()) 
if not selectedstate:
    file3 = file2.copy()
else:
    file3 = file2[file2["State"].isin(selectedstate)]

#create a city filter
selectedcity =  st.sidebar.multiselect("Pick a City: ", file3["City"].unique())


#filter the data based on region, state and city 
if not selectedregion and not selectedstate and not selectedcity:
    filtered_file = file
elif not selectedstate and not selectedcity:
    filtered_file = file[file["Region"].isin(selectedregion)]
elif not selectedregion and not selectedcity:
    filtered_file = file[file["State"].isin(selectedstate)]
elif selectedstate and selectedcity:
    filtered_file = file3[file["State"].isin(selectedstate) & file3["City"].isin(selectedcity)]
elif selectedregion and selectedcity:
    filtered_file = file3[file["Region"].isin(selectedregion) & file3["City"].isin(selectedcity)]
elif selectedregion and selectedstate:
    filtered_file = file3[file["Region"].isin(selectedregion) & file3["State"].isin(selectedstate)]
elif selectedcity:
    filtered_file = file3[file3["City"].isin(selectedcity)]
else:
    filtered_file = file3[file3["Region"].isin(selectedregion) & file3["State"].isin(selectedstate) & file3["City"].isin(selectedcity)]

#visualizations
category_file = filtered_file.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_file, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_file["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig, use_container_width=True, height = 200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_file, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_file["Region"], textposition = "outside")   
    st.plotly_chart(fig, use_container_width=True, height = 200)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_file.style.background_gradient(cmap="Blues"))
        csv = category_file.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv", help = "Click here to download the data as a CSV file")

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_file.groupby(by= "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="OrRd"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv", help = "Click here to download the data as a CSV file")       

filtered_file["month_year"] = filtered_file["Order Date"].dt.to_period("M")  
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_file.groupby(filtered_file["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y = "Sales", labels = {"Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data = csv, file_name= "TimeSeries.csv",mime = "text/csv")


# Create a treem based on Region, Category, sub-Category
st.subheader("Hierarchical view of Sales using Treemap")
fig3 = px.treemap(filtered_file, path = ["Region", "Category", "Sub-Category"], values = "Sales", hover_data=["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_file, values = "Sales", names = "Segment", template="plotly_dark")
    fig.update_traces(text = filtered_file["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_file, values = "Sales", names = "Category", template="gridon")
    fig.update_traces(text = filtered_file["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = file[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="cividis")
    st.plotly_chart(fig,use_container_width=True)

    st.markdown("Month wise Sub-Category Table")
    filtered_file["month"] = filtered_file["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data  = filtered_file, values="Sales", index=["Sub-Category"],columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))


# Create a Scatter plot
data1 = px.scatter(filtered_file, x="Sales", y="Profit", size="Quantity")
data1["layout"].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20), xaxis = dict(title="Sales", titlefont=dict(size=19)),
                       yaxis = dict(title="Profit", titlefont = dict(size=19))) 

st.plotly_chart(data1, use_container_width=True)


with st.expander("View Data"):
    st.write(filtered_file.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))


#Download Original Dataset
csv = file.to_csv(index = False).encode('utf-8')
st.download_button("Download Data", data = csv, file_name = "Data.csv", mime = "text/csv")    