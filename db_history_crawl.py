import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
url = 'https://db.history.go.kr/item/compareViewer.do?levelId=sg_006r_0020_0050'
req = requests.get(url,verify=False)
soup = BeautifulSoup(req.text,'html.parser')
cn_select = soup.find('div', {'style': 'text-align:justify;word-break:break-all;'})
for tag in cn_select(['a','sup','span']):
    tag.decompose()
text_cn = cn_select.get_text()
text_cn = text_cn.strip()

kor_select = soup.select('#cont_view > div')[1]
for tag in kor_select(['a','sup','span']):
    tag.decompose()
text_kr = kor_select.get_text()
text_kr = text_kr.strip()
print(text_cn)
print(text_kr)
