from functools import reduce

def query_properties(row,props):
    tmp = list(map(lambda k: query_item(k,row[k],props),row.index))
    return reduce(lambda a,b: a|b,tmp)
def query_item(col_name,value,props):
    if col_name not in props: return {}
    type = props[col_name]
    if type == "title": return query_title(col_name,value)
    if type == "multi_select":
        print(col_name)
        print(value)
        print(props)
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
    if type == "files": return query_files(col_name,value)
    if type == "rich_text": 
        return{
            col_name:{
                "rich_text":[{
                    "type": "text",
                    "text":{
                        "content":value
                    }
                }]
            }
        }
    if type == "checkbox": return query_checkbox(col_name,value)
    if type == "date": return query_date(col_name,value)
    return {}
def query_date(col_name,value):
    if value == "": return {}
    return {
        col_name:{
            "date":{
                "start": value
            }
        }
    }
def query_title(col_name,value):
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
def query_files(col_name,value):
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

def query_checkbox(col_name,value):
    return{
        col_name:{
            "checkbox": value
        }
    }