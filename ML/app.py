from flask import Flask,jsonify
import datetime as dt

from pandas.tests.frame.test_validate import dataframe
from sklearn import linear_model
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from flask_cors import CORS
sc = StandardScaler()
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade import quit_spade
import numpy as np
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import json
from flask_pymongo import PyMongo
app=Flask(__name__)
app.config['MONGO_URI']='mongodb://localhost:27017/covid'
mongo=PyMongo(app)

CORS(app)
cors=CORS(app, resources={
    r"/*":{
        "origins": "*"
    }
})

#start scraping
url =  "https://www.worldometers.info/coronavirus/#countries"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find("table", id="main_table_countries_today")
content = results.tbody.find_all("tr")
dic = {}
for i in range(len(content)):
    try:
        country = content[i].find_all("a", href=True)[0].string
    except:
        country = content[i].find_all("td")[0].string

    values = [j.string for j in content[i].find_all('td')]
    values = [item and item.replace(",","") for item in values]
    dic[country] = values

    column_names = ["Total cases", "New Cases", "Total deaths", "New deaths", "Total recovered", "Active Cases",
                    "Serious critical", "Tot Cases/1M pop", "Deaths/1M pop", "Total Tests", "Tests/ 1M pop"]
df = pd.DataFrame(dic).iloc[2:, :].T.iloc[1:, :11]
df.columns = column_names
df['Total cases'] = df['Total cases'].astype(int)
df['Total deaths'] = pd.to_numeric(df['Total deaths'], errors='coerce')
df['Total recovered'] = pd.to_numeric(df['Total recovered'], errors='coerce')
df= df.replace(np.nan, 0.0)
df['country']=df.index
df.set_index('country')
#file = df.to_csv(datetime.now().strftime("COVID-19 %Y-%m-%d-%H-%M.csv"))
#scraping from graphs
url2 = "https://www.worldometers.info/coronavirus/worldwide-graphs/#total-cases"
page2 = requests.get(url2)
soup2 = BeautifulSoup(page2.content, 'html.parser')
scripts = soup2.find_all('script')
script = str(scripts[23])
dates = script.split("categories: [", 1)[1].split("]", 1)[0]
dates = "[" + dates + "]"
dates = json.loads(dates)
# get the cases
cases = script.split("data: [", 1)[1].split("]", 1)[0]
cases = "[" + cases + "]"
cases = json.loads(cases)
# GET THE DEATHS
deaths = str(scripts[33])
deaths = deaths.split("data: [", 1)[1].split("]", 1)[0]
deaths = "[" + deaths + "]"
deaths = json.loads(deaths)
year = "2020"
d = {'Date': dates, 'World Cases': cases, 'Total Deaths': deaths, 'Year': year}
dataframe = pd.DataFrame(d, columns=['CurrentDate','Date', 'World Cases', 'Total Deaths'])
dataframe['Year']='2020'
dict=dataframe.to_dict('records')
dataframe[['month','day']] = dataframe.Date.str.split(" ",expand=True)
look_up = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05',
    'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

dataframe['month'] = dataframe['month'].apply(lambda x: look_up[x])
dataframe["CurrentDate"] = dataframe["day"] +"-"+ dataframe["month"] + "-"+dataframe["Year"]
dataframe["CurrentDate"]=pd.to_datetime(dataframe["CurrentDate"])
dataframe.set_index('CurrentDate')
#file = dataframe.to_csv('covid_cases_from_january.csv')

# scraping world recovered
recovered = str(scripts[26])
dates2 = recovered.split("categories: [", 1)[1].split("]", 1)[0]
dates2 = "[" + dates2 + "]"
dates2 = json.loads(dates2)

recovered = recovered.split("data: [", 1)[1].split("]", 1)[0]
recovered = "[" + recovered + "]"
recovered = json.loads(recovered)
d1 = {'Date': dates2,'Total Cured':recovered }
df2 = pd.DataFrame(d1, columns=['CurrentDate','Date', 'Total Cured'])
df2['Year']='2020'
df2[['month','day']] = df2.Date.str.split(" ",expand=True)
look_up = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05',
    'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
df2['month'] = df2['month'].apply(lambda x: look_up[x])
df2["CurrentDate"] = df2["day"] +"-"+ df2["month"] + "-"+df2["Year"]
df2["CurrentDate"]=pd.to_datetime(df2["CurrentDate"])
df2.set_index("CurrentDate")
#file = df2.to_csv('total_cured.csv')

dataframe = dataframe.merge(df2,how='outer')
dataframe=dataframe.drop_duplicates()
dataframe= dataframe.replace(np.nan, 0.0)

#store the dataframes into MongoDB
client = MongoClient('mongodb://localhost:27017')
#Creaing database with name covid
db = client["covid"]
#creating collections for our dataframes
covid_table = db["daily_cases"]
covid_table_from_january = db["cases_deaths_from_january"]
df_dict = df.to_dict('records')
dict = dataframe.to_dict('records')
dict2 = df2.to_dict('records')
#Insert tables to database
covid_table.insert_many(df_dict)
covid_table_from_january.insert_many(dict)

#plot top 15 countries in recoveries, deaths and total cases
@app.route("/top_15")
def index():
    instant_cases=mongo.db.daily_cases
    results=[]
    for i in instant_cases.find():
        results.append({'total_cases':i['Total cases'],'Total_deaths':i['Total deaths'],'Total_recovered':i['Total recovered'],'country':i['country']})
    return jsonify({'result':results})

@app.route("/chart_active_case")
def active_cases():
    table1=mongo.db.cases_deaths_from_january
    results=[]
    for i in table1.find():
        results.append({'Date':i['Date'],'total_cases':i['World Cases'],'total_deaths':i['Total Deaths'],'total_cured':i['Total Cured']})
    return jsonify({'result':results})

#vizualize the prediction
@app.route("/prediction")
def predict():
    dataframe.dropna(inplace=True)
    dataframe['CurrentDate'] = pd.to_datetime(dataframe['CurrentDate'])
    dataframe['CurrentDate'] = dataframe['CurrentDate'].map(dt.datetime.toordinal)
    X = dataframe['CurrentDate'].values
    y = dataframe['World Cases'].values
    X = X.reshape(1, -1)
    X = X.reshape(X.shape[0:])
    X = X.transpose()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    reg = linear_model.LinearRegression()
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    dfff = pd.DataFrame({'Actual': y_test.flatten(), 'Predicted': y_pred.flatten()})
    dict=dfff.to_dict('records')
    prediction_table=db['prediction']
    prediction_table.insert_many(dict)
    results = []
    for i in mongo.db.prediction.find():
        results.append({'Actual':i['Actual'], 'Predicted': i['Predicted']})
    return jsonify({'result': results})

#for plotting the clusters
@app.route("/clustering")
def make_clusters():
    global df
    df=df.dropna()
    A = df[["Total cases", "Total deaths", "Total recovered"]]
    A = sc.fit_transform(A)
    clf_final = KMeans(n_clusters=6, init='k-means++', random_state=42)
    clf_final.fit(A)
    df = df.reset_index(drop=True)
    df["Clusters"] = clf_final.predict(A)
    dfff = pd.DataFrame({'cases': df["Total cases"], 'deaths':df["Total deaths"],'recovered':df["Total recovered"],'cluster':df["Clusters"],'country':df["country"]})
    dict = dfff.to_dict('records')
    clustering_table = db['clustering']
    clustering_table.insert_many(dict)
    results=[]
    for i in mongo.db.clustering.find():
        results.append({'cases':i['cases'],'deaths': i['deaths'],'recovered':i['recovered'],'cluster':i['cluster'],'country':i['country']})
    return jsonify({'result': results})

if __name__ == '__main__':
    app.run(debug=True)
