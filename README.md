# pdnotion
 
in progress


## install

```sh
pip install git+https://github.com/EnAiya/pdnotion.git
```

## usage

```python
import pdnotion
import pandas as pd

DB_ID = "database_id"
NOTION_TOKEN = "notion_token"
pdn = pdnotion(NOTION_TOKEN)

# insert pandas DataFrame to notion database
df = pd.DataFrame([["test",["test_tag"]], ["test2",["test2_tag"]]],columns=["Name","Tags"])
pdn.insert(DB,df)

# load notion database as pandas DataFrame
tmp = pdn.load(DB)
print(tmp)
```