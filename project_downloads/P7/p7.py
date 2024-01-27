
# project: p7
# submitter: walmousa
# partner: none
# hours: 10




import pandas as pd
import re
import geopandas as gpd
import netaddr
from bisect import bisect 
import zipfile
from io import BytesIO
import rasterio
from graphviz import Graph, Digraph
import numpy as np
from rasterio.mask import mask
import sqlite3
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import sklearn
from matplotlib.colors import ListedColormap
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.cluster import KMeans


class UserPredictor:
    
    def __init__(self):
        self.model  = Pipeline([
            ("pf", PolynomialFeatures(degree=5, include_bias=False)),
            ("std", StandardScaler()),
            ("lr", LogisticRegression(fit_intercept=False)),
        ])
    
    def fit(self, train_users, train_logs, train_y):
      
        full_train= pd.merge(train_y, train_users, on="user_id", how="outer")
        merged_df=pd.merge(train_users, train_logs, on="user_id", how = "outer").fillna(0)
        merged_df=merged_df.groupby("user_id")["seconds"].sum().reset_index()
        full_train= pd.merge(full_train, merged_df, on="user_id", how="outer")

#         the following block of code can be used to improve the model, but takes considerably longer:
#         full_train["badge_num"]=0
#         for idx in range(len(full_train)):
#             if full_train["badge"][idx] =="gold":
#                 full_train["badge_num"][idx]=3
#             if full_train["badge"][idx] =="silver":
#                 full_train["badge_num"][idx]=2
#             if full_train["badge"][idx] =="bronze":
#                 full_train["badge_num"][idx]=1


        xcols=["past_purchase_amt", "age", "seconds"]
        ycol="y"

        self.model.fit(full_train[xcols], full_train[ycol])
        
    def predict(self, test_users, test_logs):
        
        merged_df=pd.merge(test_users, test_logs, on="user_id", how = "outer").fillna(0)
        merged_df=merged_df.groupby("user_id")["seconds"].sum().reset_index()
        full_test= pd.merge(test_users, merged_df, on="user_id", how="outer")
        
        ycol="y"
        # test_users["badge_num"]=0
        # for idx in range(len(test_users)):
        #     if test_users["badge"][idx] =="gold":
        #         test_users["badge_num"][idx]=3
        #     if test_users["badge"][idx] =="silver":
        #         test_users["badge_num"][idx]=2
        #     if test_users["badge"][idx] =="bronze":
        #         test_users["badge_num"][idx]=1
                
        xcols=["past_purchase_amt", "age", "seconds"]


        full_test["y pred"] = self.model.predict(full_test[xcols])
        return np.array(full_test["y pred"])
    
        
        
        