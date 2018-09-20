from PIL import Image
from io import BytesIO
from docx import Document
from docx.shared import Inches
from bs4 import BeautifulSoup

import os
import re
import requests

document = Document()
url = 'http://61.183.11.150/graph_view.php?'
headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',

'cookie':'Cacti=vmq88r5e8bmfitjde7m2ol42t2'
}

for i in range(12,18):
    for n in (1,6):
        payload1 = {'action':'tree','tree_id':'3','leaf_id':'%s'%i,'page':'%d'%n}
#        print (payload1)
    
        for m in(708,648,975,768,916):
            Regular1 = '(graph\Simage\Sphp.*local_graph_id=%d.*end=\d+)'%m
            print (Regular1)
            First_Page = requests.get(url,headers=headers,params=payload1)
            print (First_Page.url)
            plt = re.findall(Regular1,First_Page.text)
            if len(plt): 
                a=(plt[0])
            else:
                True

            JPG_url = ( 'http://61.183.11.150/'+ a)
            print( 'http://61.183.11.150/'+ a)
            JPG_url_r = JPG_url.replace(';','&')
            print(JPG_url_r)

            r = requests.get(JPG_url_r,headers=headers)
            image = Image.open(BytesIO(r.content))
            image.save('image%d.bmp'%i)
    document.add_picture('image%d.bmp'%i, width=Inches(6))
document.save('demo.docx')
