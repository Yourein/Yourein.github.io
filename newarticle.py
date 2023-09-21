import hashlib
from datetime import datetime
import os

hasher = hashlib.sha256()
now = datetime.now()

article_name_prefix = now.strftime("%Y-%m-%d")
hasher.update(now.strftime("%Y-%m-%d-%H:%M:%S").encode())
article_name = article_name_prefix + '-' + hasher.hexdigest()[:6]
title = input("Enter the title: ").rstrip("\n")

cwd = os.getcwd()
with open(cwd + "/_posts/" + article_name + ".md", 'a') as f:
    f.write(f"---\nlayout: page\ntitle: {title}\n---\n")
