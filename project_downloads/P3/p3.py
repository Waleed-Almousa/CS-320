# project: p3
# submitter: walmousa
# partner: none
# hours: 8

pip3 install selenium==4.1.2 Flask lxml html5lib
sudo apt -y install chromium-browser

import pandas as pd
from io import TextIOWrapper
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from IPython.display import display, Image
import time
import requests

from collections import deque
from graphviz import Digraph


class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set and order list
        self.visited.clear()
        self.order.clear()

        # 2. start recursive search by calling dfs_visit
        self.dfs_visit(node)
        
    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        if node in self.visited:
            return
        # 2. mark node as visited by adding it to the set
        self.visited.add(node)
        
        # 3. call self.visit_and_get_children(node) to get the children
        children = self.visit_and_get_children(node)
        # 4. in a loop, call dfs_visit on each of the children
        for child in children:
            self.dfs_visit(child)
    
    def bfs_search(self, node):
#       BFS Queue:
        que1=[node]
        
        while len(que1)>0:
            curr_node=que1.pop(0)
            if curr_node not in self.visited:
                curr_children = self.visit_and_get_children(curr_node)
                self.visited.add(curr_node)
                for child in curr_children:
                    if child not in self.visited:    
                        que1.append(child)


class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df

    def visit_and_get_children(self, node):
        # TODO: Record the node value in self.order
        self.order.append(node)
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for node, has_edge in self.df.loc[node].items():
            if has_edge==1:
                children.append(node)
        return children


class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        
    def visit_and_get_children(self, filename):
        path = "file_nodes/" + str(filename)
        data=open(path, encoding="utf-8")
        content=(data.read())
        data.close()
        
        val=content[0]
        self.order.append(val)

        lines= content.split("\n")
        children = lines[1].split(",") 
        
        return (children)
    
    def concat_order(self):
        order = ""
        for val in self.order:
            order+=val
        return order


class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__() 
        self.driver = driver
        self.log=[] #records table fragments

        
    def visit_and_get_children(self, url):
        self.log.append(pd.read_html(url)[0])
        self.order.append(url)
        children=[]
        self.driver.get(url)
        for link in self.driver.find_elements("tag name", "a"):
            children.append(link.get_attribute("href"))
        
        return children
    
    def table(self):
        return pd.concat(self.log, ignore_index=True)

        



def reveal_secrets(driver, url, travellog):
    pw=""
    for num in travellog["clue"]:
        pw+=str(num)
    driver.get(url)
    text = driver.find_element("id", "password")
    go_button = driver.find_element("id", "attempt-button")
    
    text.send_keys(pw)
    go_button.click() 
    time.sleep(0.1)
    
    loc_button = driver.find_element("id", "locationBtn")
    loc_button.click()
    time.sleep(2)

    for link in driver.find_elements("tag name", "img"):
        pic_link=link.get_attribute("src")
#    code below found at the following url: https://blog.finxter.com/5-easy-ways-to-download-an-image-from-a-url-in-python/#:~:text=We%20can%20accomplish%20this%20task%20by%20one%20of,Bonus%3A%20Download%20all%20images%20using%20a%20For%20loop

    response=requests.get(pic_link)
    with open ("Current_Location.jpg", "wb") as f:
        f.write(response.content)

# end of borrowed code

    location= driver.find_element("tag name", "p").text
    driver.close()
    
    return location


