import os
import pickle
from selenium import webdriver
import time

driver = webdriver.Edge()
book_name = '0000'
book_number = '0010'
chap_number = '000'
page_num = '0010'
page_trial = False
chap_trial = False

output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

while (int(book_name) < 9999):
    str(book_number).zfill(4)
    try:
        url = f"https://db.itkc.or.kr/dir/item?itemId=BT#dir/node?grpId=&itemId=BT&gubun=book&depth=4&cate1=H&cate2=&dataGubun=%EC%B5%9C%EC%A2%85%EC%A0%95%EB%B3%B4&dataId=ITKC_BT_{book_name}A_{book_number}_{chap_number}_{page_num}&viewSync=OT"
        driver.get(url)
        time.sleep(0.1)
        # XPath를 사용하여 원하는 데이터 추출
        data_kor = driver.find_element_by_xpath(
            '/html/body/div[2]/section[2]/section[2]/section/div[2]/div[1]/div/div[3]').text
        data_chn = driver.find_element_by_xpath(
            '/html/body/div[2]/section[2]/section[2]/section/div[2]/div[2]/div/div/div[3]').text

        # Create a folder with book_name as the name
        book_folder = os.path.join(output_folder, book_name)
        if not os.path.exists(book_folder):
            os.makedirs(book_folder)

        # Save data as pickle files
        with open(os.path.join(book_folder, f"{book_name}_kor.pkl"), 'wb') as output_file_kor:
            pickle.dump({"data": data_kor}, output_file_kor)

        with open(os.path.join(book_folder, f"{book_name}_chn.pkl"), 'wb') as output_file_chn:
            pickle.dump({"data": data_chn}, output_file_chn)

        print(f"데이터가 {book_name} 폴더에 저장되었습니다.")
        page_num = str(int(page_num) + 10).zfill(4)
        page_trial = False
        chap_trial = False

    except Exception as e:
        if page_trial == False:
            # page_num, chap_number 값을 조정하여 재시도
            page_num = '0010'
            chap_number = str(int(chap_number) + 10).zfill(3)
            page_trial = True
        elif page_trial == True and chap_trial == False:
            # page_num, chap_number, book_number 값을 모두 조정하여 재시도
            page_num = '0010'
            chap_number = '000'
            book_number = str(int(book_number) + 10).zfill(4)
            chap_trial = True
        else:
            page_num = '0010'
            chap_number = '000'
            book_number = '0010'
            book_name = int(book_name) + 1
            book_name = str(book_name).zfill(4)
