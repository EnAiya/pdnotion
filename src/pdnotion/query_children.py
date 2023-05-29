def query_children(text):
    if type(text) is list:
        blocks = text
    else:
        blocks = split_in_n(text, 2000)
    return [query_block(text) for text in blocks]

def query_block(text):
    return  {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text":{
                            "content": text
                        }
                    }]
                }
            }

def split_in_n(s,n):
    return [s[i:i+n] for i in range(0,len(s), n)]