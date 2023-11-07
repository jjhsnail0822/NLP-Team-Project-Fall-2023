import requests
from bs4 import BeautifulSoup
import os
import json
import re

output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

url = f"http://db.cyberseodang.or.kr/front/main/mainmenu.do?tab=tab1_03"
req = requests.get(url, verify=False)
soup = BeautifulSoup(req.text, "html.parser")

# 책 url 추출
books = soup.find("div", class_="mcont tab1 tab1_03").select("a.cover")
books_url = []
for book in books:
    books_url.append("http://db.cyberseodang.or.kr" + book.attrs["href"])

# 페이지 url 추출
for book_url in books_url:
    req = requests.get(book_url, verify=False)
    soup = BeautifulSoup(req.text, "html.parser")
    book_name = soup.select_one("div.hd_tit > h3").get_text()
    print(book_name)
    pages = soup.select("li.li_last")
    pages_url = []
    for page in pages:
        pages_url.append("http://db.cyberseodang.or.kr" + page.find("a").attrs["href"])

    data_of_a_book = {"chn": [], "kor": []}
    for url in pages_url:
        url = f"{url}"
        req = requests.get(url, verify=False)
        soup = BeautifulSoup(req.text, "html.parser")

        select_chn = soup.select("#_content > div.org > div")

        # em 태그와 태그 내부의 내용 제거하고 본문만 출력
        for element in select_chn:
            for em in element.find_all("em"):
                em.extract()
            # class 속성 삭제
            for tag in element.find_all(True):
                del tag["class"]
            content_chn = element.get_text(strip=True)  # 태그 내부의 내용만 가져옴
            if content_chn:
                data_of_a_book["chn"].append(content_chn)
                print(content_chn)
        select_kor = soup.select("#_content > div.trans_org._bonmun")
        for element in select_kor:
            for em in element.find_all("em"):
                em.extract()
            content_kor = element.get_text(strip=True)  # 태그 내부의 내용만 가져옴
            if content_kor:
                data_of_a_book["kor"].append(content_kor)
                print(content_kor)
    with open(
        os.path.join(output_folder, f"{book_name}.json"), "w", encoding="utf-8"
    ) as output_file:
        json.dump(data_of_a_book, output_file, ensure_ascii=False)
    print(f"데이터가 파일에 저장되었습니다.")
