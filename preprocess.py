from datasets import Dataset
import hanja
from hanja import hangul
import json
import os
import pandas as pd
import pickle
import re
from transformers import AutoTokenizer
from tqdm import tqdm
import unicodedata

# for now, preprocessing of only Joseon Dynasty Silok is supported

PATH_SILOK = r'parsed\\'
PATH_ITKC = r'itkc\\' # 한국고전종합DB
PATH_CYBER = r'cyberseodang\\' # 동양고전종합DB

# MODEL_ID = "EleutherAI/polyglot-ko-5.8b"
MODEL_ID = "nlpai-lab/kullm-polyglot-5.8b-v2"
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

CYBER_NO_DIRECT_HANJA = ['논어집주.json',
                         '대학장구.json',
                         '맹자집주.json',
                         '중용장구.json',
                         '추구.json',]

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

def preprocess_cyber():
    def preprocess_chn(text):
        text = re.sub(f'(○|◑|●|◎)', '', text) # remove '○' symbols
        text = re.sub(f'注\+', ' 注 ', text)
        text = re.sub(f'^[0-9]+(-|－|\.|‧)?([0-9])*(-|－|\.|‧)?(가([0-9])*|([0-9])*)', '', text) # remove line numbers
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def preprocess_kor(text):
        text = re.sub(f'(○|◑|●|◎)', '', text) # remove '○' symbols
        text = re.sub(f'주\(注\)\+([①-㊿])?', ' 주석: ', text)
        text = re.sub(f'^[0-9]+(-|－|\.|‧)?([0-9])*(-|－|\.|‧)?(가([0-9])*|([0-9])*)', '', text) # remove line numbers
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def is_all_hanja(text):
        for c in text:
            if not hanja.is_hanja(c):
                return False
        return True

    cyber_data = []
    for filename in os.listdir(PATH_CYBER):
        with open(os.path.join(PATH_CYBER, filename), 'rb') as f:
            data = json.load(f)
            if filename in CYBER_NO_DIRECT_HANJA: # no need to convert hanja to hangul
                for i in range(len(data['chn'])):
                    cyber_data.append({'chn': data['chn'][i], 'kor': data['kor'][i]})
            else:
                for i in range(len(data['chn'])):
                    converted_kor = [x for x in hanja.split_hanja(data['kor'][i])]
                    for j in range(len(converted_kor)):
                        if not is_all_hanja(converted_kor[j]): # if not all hanja
                            continue
                        if j > 0 and j < len(converted_kor) - 1: # if not first or last split
                            if converted_kor[j-1][-1] == '(' and converted_kor[j+1][0] == ')': # dismiss hanja in parentheses
                                continue
                        converted_kor[j] = hanja.translate(converted_kor[j], 'substitution') + '(' + converted_kor[j] + ')'
                        if j > 0:
                            if hangul.is_hangul(converted_kor[j-1][-1]) or converted_kor[j-1][-1] in ['.',',','?','!',')',']','〉','》','≫','’','”']:
                                converted_kor[j] = ' ' + converted_kor[j] # add deleted space before hanja
                    converted_kor = ''.join(converted_kor)
                    cyber_data.append({'chn': data['chn'][i], 'kor': converted_kor})
            print('cyber data loaded from', filename)

    for i in tqdm(range(len(cyber_data))):
        cyber_data[i]['chn'] = preprocess_chn(cyber_data[i]['chn'])
        cyber_data[i]['kor'] = preprocess_kor(cyber_data[i]['kor'])
    
    return cyber_data

result_data = preprocess_silok()
itkc_data = preprocess_itkc()
cyber_data = preprocess_cyber()
result_data.extend(itkc_data)
result_data.extend(cyber_data)

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
    if '《》' in p['chn'] or '、、' in p['chn']: # something wrong
        continue

    data = f"아래는 작업을 설명하는 명령어와 추가 컨텍스트를 제공하는 입력이 짝을 이루는 예제입니다. 요청을 적절히 완료하는 응답을 작성하세요.\n\n### 명령어:\n한문을 한국어로 번역하세요.\n\n### 입력:\n{p['chn']}\n\n### 응답:\n{p['kor']}" + tokenizer.eos_token
    # data = f"### 명령어: 한문을 한국어로 번역하세요.\n### 입력: {p['chn']}\n### 응답: {p['kor']}" + tokenizer.eos_token
    # data = f"###System;한문을 한국어로 번역하세요.\n###User;{p['chn']}\n###Midm;{p['kor']}"
    dataset['text'].append(data)

# remove duplicates
dataset = pd.DataFrame(dataset)
dataset = pd.DataFrame.drop_duplicates(dataset, ignore_index=True)
dataset = Dataset.from_pandas(dataset, preserve_index=False)

# train, test, validation split
dataset = dataset.train_test_split(test_size=0.01)
dataset_eval = dataset['test'].train_test_split(test_size=0.5)
dataset['test'] = dataset_eval['test']
dataset['eval'] = dataset_eval['train']

dataset = dataset.map(lambda x: tokenizer(x["text"], truncation=True, max_length=2048), batched=True)
dataset = dataset.filter(lambda batch: [x[-1] == tokenizer.eos_token_id for x in batch['input_ids']], batched=True) # remove incomplete data

with open(PKL_PATH, 'wb') as f:
    pickle.dump(dataset, f)