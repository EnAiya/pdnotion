from notion_client import Client
import pandas as pd
from functools import reduce


from .query_properties import query_properties
from .query_children import query_children

class pdnotion:
    def __init__(self, token):
        self.client = Client(auth=token)
    def properties(self,db_id):
        props = self.client.databases.retrieve(db_id)["properties"]
        tmp =  list(map(lambda k: {k:props[k]["type"]}, props))
        return reduce(lambda a,b: a|b,tmp)

    def insert_row(self, db_id, row, props = None, content = None, update=False):
        if props is None: props = self.properties(db_id)
        q = {
                "properties": query_properties(row,props),
            }
        if not update:
            q |={
                "parent": {"database_id": db_id},
            }
        else:
            assert("_page_id" in row)
            q |={
                "page_id": row["_page_id"]
            }
        if content is not None:
            q |= {
                "children":query_children(row[content])
            }
        if not update:
            self.client.pages.create(
                **q
            )
        else:
            self.client.pages.update(
                **q
            )
    def update(self,db_id,pd,content=None):
        props = self.properties(db_id)
        for id,row in pd.iterrows():
            self.insert_row(db_id,row,props,content,update=True)       
    def insert(self,db_id,pd,content=None):
        props = self.properties(db_id)
        for id,row in pd.iterrows():
            self.insert_row(db_id,row,props,content)
    def load(self,db_id,max_page=-1,**kwargs):
        props = self.properties(db_id)
        hasmore = True
        data = []
        page = 0
        next = kwargs.get("start_cursor",None)
        
        while hasmore:
            param = {
                    "database_id": db_id,
                    "start_cursor": next,
                    **kwargs
            }
            db = self.client.databases.query(**param)
            data += db["results"]
            hasmore = db["has_more"]
            next = db["next_cursor"]
            page += 1
            if max_page != -1 and page >= max_page: break
        return pd.DataFrame(list(map(lambda d: self.parse_notion(d,props), data)))
        
    def parse_notion(self,row, props):
        tmp = list(map(lambda k: self.parse_item(k,props[k],row),props))
        tmp += [{"_page_id": row["id"]}]
        tmp += [{"_created_time": pd.to_datetime(row["created_time"])}]
        tmp += [{"_last_edited_time": pd.to_datetime(row["last_edited_time"])}]
        return reduce(lambda a,b: a|b,tmp)

    def parse_item(self,name,type,row):
        props = row["properties"]
        v = ""
        if type == "title": v= props[name]["title"][0]["text"]["content"] if len(props[name]["title"]) > 0 else ""
        if type == "rich_text": v= props[name]["rich_text"][0]["text"]["content"] if len(props[name]["rich_text"]) > 0 else ""
        if type == "multi_select": v= list(map(lambda x: x["name"], props[name]["multi_select"]))
        if type == "select": v = props[name]["select"]["name"] if props[name]["select"] is not None else ""
        if type == "number": v = props[name]["number"]
        if type == "formula": v= props[name]["formula"]["number"] if "number" in props[name]["formula"] else ""
        if type == "files": v=props[name]["files"][0]["external"]["url"] if len(props[name]["files"]) > 0 else ""
        if type == "checkbox": v=props[name]["checkbox"]
        if type == "date": v=props[name]["date"]["start"] if props[name]["date"] is not None else ""
        return {name:v}
    
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()

    pdn = pdnotion(os.getenv("NOTION_TOKEN"))
    df = pdn.load(os.getenv("NOTION_DB"))
    print(df.head(10))

    # sort test
    print("sort test")
    df = pdn.load(os.getenv("NOTION_DB"),sorts=[{
        "property": "Name",
        "direction": "ascending"
    }])
    print(df.head(10))


    # filter test
    df = pdn.load(os.getenv("NOTION_DB"),filter={
        "property": "Checkbox",
        "checkbox":{
            "equals": True
        }
    })
    print(df.head(10))


    import datetime
    dnow = datetime.datetime.utcnow().isoformat()
    pdn.insert(os.getenv("NOTION_DB"),pd.DataFrame([{"Name":"date_test", "Date": dnow}]))
    row = df.head(1)
    row.at[row.index[0], "Name"] = "update_test"
    print(row)
    pdn.update(os.getenv("NOTION_DB"),row)
