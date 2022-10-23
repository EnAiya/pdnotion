from notion_client import Client
import pandas as pd
from functools import reduce

from .query_properties import query_properties

class pdnotion:
    def __init__(self, token):
        self.client = Client(auth=token)
    def properties(self,db_id):
        props = self.client.databases.retrieve(db_id)["properties"]
        tmp =  list(map(lambda k: {k:props[k]["type"]}, props))
        return reduce(lambda a,b: a|b,tmp)

    def insert_row(self, db_id, row, props = None):
        if props is None: props = self.properties(db_id)
        self.client.pages.create(
            **{
                "parent": {"database_id": db_id},
                "properties": query_properties(row,props)
            }
        )
    def insert(self,db_id,pd):
        props = self.properties(db_id)
        for id,row in pd.iterrows():
            self.insert_row(db_id,row,props)
    def load(self,db_id):
        props = self.properties(db_id)
        hasmore = True
        data = []
        next = None
        while hasmore:
            db = self.client.databases.query(
                **{
                    "database_id": db_id,
                    "start_cursor": next,
                }
            )
            data += db["results"]
            hasmore = db["has_more"]
            next = db["next_cursor"]
        return pd.DataFrame(list(map(lambda d: self.parse_notion(d,props), data)))
        
    def parse_notion(self,row, props):
        tmp = list(map(lambda k: self.parse_item(k,props[k],row),props))
        return reduce(lambda a,b: a|b,tmp)

    def parse_item(self,name,type,row):
        props = row["properties"]
        v = ""
        if type == "title": v= props[name]["title"][0]["text"]["content"] if len(props[name]["title"]) > 0 else ""
        if type == "rich_text": v= props[name]["rich_text"][0]["text"]["content"] if len(props[name]["rich_text"]) > 0 else ""
        if type == "multi_select": v= list(map(lambda x: x["name"], props[name]["multi_select"]))
        if type == "number": v = props[name]["number"]
        if type == "formula": v= props[name]["formula"]["number"]
        if type == "files": v=props[name]["files"][0]["external"]["url"] if len(props[name]["files"]) > 0 else ""
        return {name:v}
    
