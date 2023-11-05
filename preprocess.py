from datasets import Dataset
import json
import os
import pickle
import re
from transformers import AutoTokenizer
from tqdm import tqdm
import unicodedata

# for now, preprocessing of only Joseon Dynasty Silok is supported

PATH_SILOK = r'parsed\\'
PATH_ITKC = r'itkc\\' # 한국고전종합DB

MODEL_ID = "EleutherAI/polyglot-ko-5.8b"
# MODEL_ID = "KT-AI/midm-bitext-S-7B-inst-v1"
PKL_PATH = "Preprocessed.pkl"
SILOK_SUFFIXES = ['太祖康獻大王實錄',
                  # 정종
                  '太宗恭定大王實錄',
                  '世宗莊憲大王實錄',
                  # 문종
                  # 단종
                  '世祖惠莊大王實錄',
                  '睿宗襄悼大王實錄',
                  '成宗康靖大王實錄',
                  '燕山君日記',
                  '中宗恭僖徽文昭武欽仁誠孝大王實錄',
                  # 인종
                  '明宗大王實錄',
                  '宣宗大王實錄', # 선조 1
                  '宣宗昭敬大王實錄', # 선조 2
                  '宣祖昭敬大王實錄', # 선조 3
                  '宣祖大王修正實錄', # 선조 4
                  '《光海君日記》', # 광해군 1
                  '光海君日記', # 광해군 2
                  '仁祖大王實錄',
                  '孝宗大王實錄',
                  '顯宗純文肅武敬仁彰孝大王實錄', # 현종 1
                  '顯宗純文肅武敬仁彰孝大王改修實', # 현종 2
                  '肅宗顯義光倫睿聖英烈章文憲武敬明元孝大王實錄', # 숙종 1
                  '肅宗顯義光倫睿聖英烈章文憲武敬明元孝大王實錄補闕正誤', # 숙종 2
                  '景宗德文翼武純仁宣孝大王實錄', # 경종 1
                  '景宗德文翼武純仁宣孝大王修正實錄', # 경종 2
                  '英宗至行純德英謨毅烈章義弘倫光仁敦禧體天建極聖功神化大成廣運開泰基永堯明舜哲乾健坤寧翼文宣武熙敬顯孝大王實錄',
                  '正宗文成武烈聖仁莊孝大王實錄',
                  '純宗淵德顯道景仁純禧文安武靖憲敬成孝大王實錄',
                  '憲宗經文緯武明仁哲孝大王實錄',
                  '哲宗熙倫正極粹德純聖文顯武成獻仁英孝大王實錄',
                  # 고종, 순종 X
                  ]
SILOK_SUFFIXES = '|'.join(SILOK_SUFFIXES) # for regex searching
CHEONGAN = r'(甲|乙|丙|丁|戊|己|庚|辛|壬|癸)'
JIJI = r'(子|丑|寅|卯|辰|巳|午|未|申|酉|戌|亥)'

def preprocess_silok():
    def preprocess_chn(text):
        text = re.sub(f'○', '', text) # remove '○' symbols
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        suffix_found = re.search(f'({SILOK_SUFFIXES})', text)
        if suffix_found:
            if len(text[suffix_found.start():]) <= 54*2+2: # 54 is the length of the longest silok suffix
                text = text[:suffix_found.start()]
        text = re.sub(f'{CHEONGAN}{JIJI}/', '', text).strip() # remove prefixed 갑자
        return text

    def preprocess_kor(text):
        text = unicodedata.normalize('NFC', text)
        text = re.sub(f'○', '', text) # remove '○' symbols
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    chn_data = {}
    kor_data = {}

    for filename in os.listdir(PATH_SILOK):
        with open(os.path.join(PATH_SILOK, filename), 'rb') as f:
            if filename.endswith('han'):
                chn_data.update(pickle.load(f))
                print('chn data loaded from', filename)
            else:
                kor_data.update(pickle.load(f))
                print('kor data loaded from', filename)

    result = []

    for key in tqdm(kor_data.keys()):
        if key in chn_data:
            data = {'chn': preprocess_chn(chn_data[key]), 'kor': preprocess_kor(kor_data[key])}
            result.append(data)
    return result

def preprocess_itkc():
    def preprocess_chn(text):
        text = re.sub(f'○', '', text) # remove '○' symbols
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def preprocess_kor(text):
        text = re.sub(f'○', '', text) # remove '○' symbols
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r' (/|／) [^가-힣\s]{2,13}', '', text).strip() # remove poems of original text
        return text

    itkc_data = []
    for filename in os.listdir(PATH_ITKC):
        with open(os.path.join(PATH_ITKC, filename), 'rb') as f:
            data = json.load(f)
            for i in range(len(data['chn'])):
                itkc_data.append({'chn': data['chn'][i], 'kor': data['kor'][i]})
            print('itkc data loaded from', filename)

    for i in tqdm(range(len(itkc_data))):
        itkc_data[i]['chn'] = preprocess_chn(itkc_data[i]['chn'])
        itkc_data[i]['kor'] = preprocess_kor(itkc_data[i]['kor'])

    return itkc_data

result_data = preprocess_silok()
itkc_data = preprocess_itkc()
result_data.extend(itkc_data)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
dataset = {'text': []}
for p in tqdm(result_data):
    if len(p['chn']) > 2000: # too long
        continue
    if len(p['chn']) <= 4 or len(p['kor']) <= 4: # too short or no translation
        continue
    if p['kor'] == '[번역문 없음]' or p['kor'] == '[본문 내용 없음]' or p['chn'] == '[本文缺]': # no translation
        continue
    if len(re.findall(r'[가-힣]', p['chn'])) >= 4: # too many korean characters
        continue

    # data = f"아래는 작업을 설명하는 명령어와 추가 컨텍스트를 제공하는 입력이 짝을 이루는 예제입니다. 요청을 적절히 완료하는 응답을 작성하세요.\n\n### 명령어:\n한문을 한국어로 번역하세요.\n\n### 입력:\n{p['chn']}\n\n### 응답:\n{p['kor']}" + tokenizer.eos_token
    data = f"### 한문: {p['chn']}\n### 한국어: {p['kor']}" + tokenizer.eos_token
    # data = f"###System;한문을 한국어로 번역하세요.\n###User;{p['chn']}\n###Midm;{p['kor']}"
    dataset['text'].append(data)

# train, test, validation split
dataset = Dataset.from_dict(dataset).train_test_split(test_size=0.01)
dataset_eval = dataset['test'].train_test_split(test_size=0.5)
dataset['test'] = dataset_eval['test']
dataset['eval'] = dataset_eval['train']

dataset = dataset.map(lambda x: tokenizer(x["text"], truncation=True, max_length=2048), batched=True)

with open(PKL_PATH, 'wb') as f:
    pickle.dump(dataset, f)