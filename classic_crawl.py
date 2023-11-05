import requests
from bs4 import BeautifulSoup
import os
import json
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
num=2


data_of_a_book = {'chn': [], 'kor': []}

# 특정 부분 선택
while num<261:
    url = f'http://db.cyberseodang.or.kr/front/alphaList/BookMain.do?tab=tab1_01&bnCode=jti_1h0601&titleId=C{num}'
    req = requests.get(url, verify=False)
    soup = BeautifulSoup(req.text, 'html.parser')
    select_chn = soup.select('#_content > div.org > div')

    # em 태그와 태그 내부의 내용 제거하고 본문만 출력
    for element in select_chn:
        for em in element.find_all('em'):
            em.extract()
        # class 속성 삭제
        for tag in element.find_all(True):
            del tag['class']
        content_chn = element.get_text(strip=True)  # 태그 내부의 내용만 가져옴
        if content_chn:
            data_of_a_book['chn'].append(content_chn)
            print(content_chn)
    select_kor = soup.select('#_content > div.trans_org._bonmun')
    for element in select_kor:
        for em in element.find_all('em'):
            em.extract()
        content_kor = element.get_text(strip=True)  # 태그 내부의 내용만 가져옴
        if content_kor:
            data_of_a_book['kor'].append(content_kor)
            print(content_kor)
    num+=1
with open(os.path.join(output_folder, f"맹자집주.json"), 'w', encoding='utf-8') as output_file:
    json.dump(data_of_a_book, output_file, ensure_ascii=False)
print(f"데이터가 파일에 저장되었습니다.")
