# project: p4
# submitter: walmousa
# partner: none
# hours: 10

import flask 
import time
import json
import pandas as pd
import requests
from flask import Flask, request, jsonify
import csv
import re
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io # input / output


# data source: 
# https://www.kaggle.com/datasets/shreyajagani13/imdb-movies-data?resource=download
# data was found on kaggle; this data set has 11 columns and 1000 rows. The first column is a list of movie names, and the other 10 provide details about each respective movie. I will only be using 100 rows of the data for simplicity. I also dropped 1 of the columns.

#  _repr_html_ function was coppied from stack overflow from the following link:
# https://python.hotexamples.com/examples/pandas/DataFrame/_repr_html_/python-dataframe-_repr_html_-method-examples.html#:~:text=def%20_repr_html_%20%28self%2C%20%2Aargs%2C%20%2A%2Akwargs%29%3A%20%22%22%22%20Ipython%20Notebook,proper%20size%20for%20optimal%20viewing%20and%20so%20on.

def _repr_html_(self, *args, **kwargs):
    obj = self._frame

    if isinstance(obj, Series):
        obj = DataFrame(obj, columns=[self.specifier])
    # Call DataFrame _repr_html
    dfhtml = obj._repr_html_(*args, **kwargs)
    return ('<h4>%s</h4>' % ''.join(self._header_html)) +'<br>'+ dfhtml

# end of copied code

app = Flask("my website")
num_subscribed=0
total_count=0
count_A=0
count_B=0
visit_dict={}
visit_list=[]
df = pd.read_csv("main.csv")

# browse page
@app.route("/browse.html")
def browse(): 
    global df
    df2=df._repr_html_()
    with open("browse.html") as f:
        s = f.read()
    s=s.replace("REPLACE", df2)
    return s

# browse json
@app.route("/browse.json")
def browse2():
    global last_visit_dict
    global visit_list
    visitor=request.remote_addr
    if visitor not in visit_list:
        visit_dict[visitor]=0
        visit_list.append(visitor)
    df = pd.read_csv("main.csv")
    df2=df.to_dict(orient='records')
    if time.time() - visit_dict[visitor]>60:
        visit_dict[visitor]=time.time()
        return jsonify(df2)
    else:
        return flask.Response("<b>go away</b>",
                              status=429,
                              headers={"Retry-After": "60"})
    

# visitors json
@app.route("/visitors.json")
def visitors():
    global visit_list
    return jsonify(visit_list)
    
    
# email 
@app.route("/email", methods=["POST"])
def email():
    global num_subscribed
    email = str(request.data, "utf-8")
    if len(re.findall(r"^\w+\@{1}\w+\.\w\w\w$", email)) > 0: # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
        num_subscribed+=1
        return jsonify(f"thanks, your subscriber number is {num_subscribed}!")
    return jsonify("Invalid Email!") # 3


# donate page
@app.route("/donate.html")
def donate():
    global count_A
    global count_B
    with open("donate.html") as f:
        s = f.read()
    try:
        assert (request.args['from']=='A' or request.args['from']=='B')
        if total_count<=10:
            assert (request.args['from']=='A' or request.args['from']=='B')
            if request.args['from']=='A':
                count_A+=1
            elif request.args['from']=='B':
                count_B+=1
    except KeyError:
        s=s.replace("Please make a donation!", "<p>Error: from argument not specified</p>")     
    return s

@app.route("/genreplt.svg")
def genreplt():
    global df
    genre_list=[]
    genre_count={}
    compact_genre_list=[]
    compact_count_list=[]
    compact_dict={}
    compact_dict["Other"]=0
    for idx in range(len(df)):
        if df["genre.1"][idx] not in genre_list:
            genre_list.append(df["genre.1"][idx])
            genre_count[df["genre.1"][idx]]=1
        else:
            genre_count[df["genre.1"][idx]]+=1
        if df["genre.2"][idx] not in genre_list:
            genre_list.append(df["genre.2"][idx])
            genre_count[df["genre.2"][idx]]=1
        else:
            genre_count[df["genre.2"][idx]]+=1
        if df["genre.3"][idx] not in genre_list:
            genre_list.append(df["genre.3"][idx])
            genre_count[df["genre.3"][idx]]=1
        else:
            genre_count[df["genre.3"][idx]]+=1
    for genre in genre_count:
        if genre_count[genre]<5:
            compact_dict["Other"]+=genre_count[genre]
        else:
            compact_dict[genre]=genre_count[genre]
            compact_genre_list.append(genre)
            compact_count_list.append(compact_dict[genre])
    compact_genre_list.append("Other")
    compact_count_list.append(compact_dict["Other"])
    try:
#         scatter plot if color arg is present
        gcolor= request.args['color']
        fig, ax= plt.subplots(figsize=(10, 5))
        ax=plt.scatter(x=compact_genre_list, y=compact_count_list, color=gcolor)
        plt.ylabel('Number of Movies', fontsize=15, color=gcolor)
        plt.xlabel(xlabel='Genre', fontsize=15, color= gcolor)
        plt.title(label="Number of Movies in Each Genre", fontsize=20, color=gcolor)
        f=io.StringIO()
        fig.savefig(f, format="svg")
        plt.close()
    except KeyError: 
#         line plot if no args are given
        fig, ax= plt.subplots(figsize=(10, 5))
        ax=pd.Series(compact_dict).plot.line(fontsize=10)
        ax.set_ylabel(ylabel='Number of Movies', fontsize=15)
        ax.set_xlabel(xlabel='Genre', fontsize=15)
        plt.title(label="Number of Movies in Each Genre", fontsize=20)
        f=io.StringIO()
        fig.savefig(f, format="svg")
        plt.close() 
    return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route("/ratingsbox.svg")
def tester():
    global df
    ratings=df["imdb_rating"]
    fig, ax= plt.subplots(figsize=(10, 5))
    ax.boxplot(ratings, vert=0)
    ax.set_xlabel("Ratings", fontsize=15)
    ax.set_ylabel("Value", fontsize=15)
    plt.title(label="Distribution of Movie Ratings", fontsize=20)
    f=io.StringIO()
    fig.savefig(f, format="svg")
    plt.close() 
    return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

    
# home page
@app.route('/')
def home():
    global total_count
    total_count+=1
    with open("index.html") as f:
        html = f.read()
    
    if total_count<=10:
        if total_count%2==0:
            html= html.replace("Enjoy!", "<p><font color='red'>Enjoy!</font></p>")
            html = html.replace("Browse Data",  "<p><font color='red'>Browse Data</font></p>", 1)
            html = html.replace("Donate!",  "<p> <a href='donate.html?from=B'<font color='red'>Donate!</font> </a></p>")
            return html
        else:
            html=html.replace("Donate!", "<p> <a href='donate.html?from=A'>Donate!</a></p>")
            return html
    else:
        if count_A>=count_B:
            html=html.replace("Donate!", "<p> <a href='donate.html?from=A'>Donate!</a></p>")
            return html
        elif count_B>count_A: 
            html= html.replace("Enjoy!", "<p><font color='red'>Enjoy!</font></p>")
            html = html.replace("Browse Data",  "<p><font color='red'>Browse Data</font></p>", 1)
            html = html.replace("Donate!",  "<p> <a href='donate.html?from=B'<font color='red'>Donate!</font> </a></p>")
            return html

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!


