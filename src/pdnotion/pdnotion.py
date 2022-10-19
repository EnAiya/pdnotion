from notion_client import Client
import pandas as pd
from functools import reduce

class pdnotion:
    def __init__(self, token):
        self.client = Client(auth=token)
    def properties(self,db_id):
        props = self.client.databases.retrieve(db_id)["properties"]
        tmp =  list(map(lambda k: {k:props[k]["type"]}, props))
        return reduce(lambda a,b: a|b,tmp)
    def query_properties(self,row,props):
        tmp = list(map(lambda k: self.query_item(k,row[k],props),row.index))
        return reduce(lambda a,b: a|b,tmp)
    def query_item(self,col_name,value,props):
        if col_name not in props: return {}
        type = props[col_name]
        if type == "title": return self.query_title(col_name,value)
        if type == "multi_select":
            return {
                col_name:{
                    "multi_select": list(map(lambda x: {"name": x}, value))
                }
            }
        if type == "number":
            return {
                col_name:{
                    "number" : value
                }
            }
        if type == "files": return self.query_files(col_name,value)
        return {}
    def query_title(self,col_name,value):
        return {
            col_name:{
                "title": [
                    {
                        "type": "text",
                        "text":{
                            "content": value
                        }
                    }
                ]
            }
        }
    def query_files(self,col_name,value):
        return {
            col_name:{
                "files":[{
                    "type": "external",
                    "name": "file",
                    "external":{
                        "url":value
                    }
                }]
            }
        }
    def insert_row(self, db_id, row, props = None):
        if props is None: props = self.properties(db_id)
        self.client.pages.create(
            **{
                "parent": {"database_id": db_id},
                "properties": self.query_properties(row,props)
            }
        )
    def insert(self,db_id,pd):
        props = self.properties(db_id)
        for id,row in pd.iterrows():
            print(row)
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
        print(props)
        if type == "title": v= props[name]["title"][0]["text"]["content"] if len(props[name]["title"]) > 0 else ""
        if type == "rich_text": v= props[name]["rich_text"][0]["text"]["content"] if len(props[name]["rich_text"]) > 0 else ""
        if type == "multi_select": v= list(map(lambda x: x["name"], props[name]["multi_select"]))
        return {name:v}
    
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    DB = "b6001e9f4ffc46f4a6a0a33d1c6c33bf"
    pdn = pdnotion(os.getenv("NOTION_TOKEN"))

    df = pd.DataFrame([["test",["test_tag"]], ["test2",["test2_tag"]]],columns=["Name","Tags"])
    props = pdn.properties(DB)
    row = df.iloc[0]
    pdn.insert(DB,df)

    tmp = pdn.load(DB)
    print(tmp)