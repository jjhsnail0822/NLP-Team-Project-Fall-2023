#한국고전종합DB 크롤러
#해당 사이트는 웹페이지 주소가 ~ITKC_BT_1370A_0020_000_0010&viewSync=OT 형식으로 이루어져 있다.
#각각 책 제목, 각 책이 여러권으로 이루어져있는 경우 해당 권의 제목, 챕터 이름, 페이지를 나타내는 숫자이다.
#이를 book_name, book_number, chap_number, page_num 4개의 변수로 분할하여 웹페이지를 탐색한다.
from selenium import webdriver
import time


driver = webdriver.Edge()
book_name = '1370'
book_number = '0160'
chap_number = '000'
page_num = '0010'
last_fail = False
while (int(book_number)<=190):
    str(book_number).zfill(4)
    try:
        url = f"https://db.itkc.or.kr/dir/item?itemId=BT#dir/node?grpId=&itemId=BT&gubun=book&depth=4&cate1=H&cate2=&dataGubun=%EC%B5%9C%EC%A2%85%EC%A0%95%EB%B3%B4&dataId=ITKC_BT_{book_name}A_{book_number}_{chap_number}_{page_num}&viewSync=OT"
        driver.get(url)
        # XPath를 사용하여 원하는 데이터 추출
        data_kor = driver.find_element_by_xpath('/html/body/div[2]/section[2]/section[2]/section/div[2]/div[1]/div/div[3]').text
        data_chn = driver.find_element_by_xpath('/html/body/div[2]/section[2]/section[2]/section/div[2]/div[2]/div/div/div[3]').text

        # 데이터를 output.txt 파일에 저장
        with open('output_kor.txt', 'a', encoding='utf-8') as output_file_kor:
            output_file_kor.write(data_kor + '\n')
        with open('output_chn.txt', 'a', encoding='utf-8') as output_file_chn:
            output_file_chn.write(data_chn + '\n')

        print("데이터가 output.txt 파일에 저장되었습니다.")
        last_fail = False
        page_num = str(int(page_num) + 10).zfill(4)
        time.sleep(1)
    except Exception as e:
        if last_fail == False:
            # page_num, chap_number 값을 조정하여 재시도
            page_num = '0010'
            chap_number = str(int(chap_number) + 10).zfill(3)
            last_fail = True
            time.sleep(2)
        else:
            # page_num, chap_number, book_number 값을 모두 조정하여 재시도
            page_num = '0010'
            chap_number = '000'
            book_number = str(int(book_number) + 10).zfill(4)
