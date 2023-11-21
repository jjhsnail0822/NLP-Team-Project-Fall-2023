import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextStreamer, GPTQConfig
from peft import PeftConfig, PeftModel
import pickle
from sacrebleu.metrics import BLEU

RUN_GPTQ = False
RUN_LORA_MERGED_8BIT = False

MODEL_ID = "nlpai-lab/kullm-polyglot-5.8b-v2"
PEFT_ID = "hankor"
QUANTIZED_ID = "hankor-quantized-8bit"
LORA_MERGED_8BIT_ID = "hankor-lora-merged-8bit"
MAX_NEW_TOKENS = 2048
CONTEXT_CHN = '아래는 작업을 설명하는 명령어와 추가 컨텍스트를 제공하는 입력이 짝을 이루는 예제입니다. 요청을 적절히 완료하는 응답을 작성하세요.\n\n### 명령어:\n한문을 한국어로 번역하세요.\n\n### 입력:\n'
SPLIT = '\n\n### 응답:\n'
PKL_PATH = 'Preprocessed.pkl'

device = torch.device("cuda:0" if torch.cuda.is_available() 
                        else "mps" if torch.backends.mps.is_available()
                        else "cpu")

if RUN_GPTQ:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(QUANTIZED_ID, device_map='auto')
    model.to(device)
elif RUN_LORA_MERGED_8BIT:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(LORA_MERGED_8BIT_ID, device_map='auto')
else:
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    config = PeftConfig.from_pretrained(PEFT_ID)
    model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path, quantization_config=bnb_config, device_map=device)
    model = PeftModel.from_pretrained(model, PEFT_ID)
    tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path, skip_special_tokens=True)
    model.to(device)

streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

model.eval()
model.config.use_cache = True

def translate(user_input):
    context = CONTEXT_CHN + user_input + SPLIT
    print('한국어  > ')
    gened = model.generate(
        **tokenizer(
            context, 
            return_tensors='pt', 
            return_token_type_ids=False
        ).to(device),
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
        streamer=streamer,
        temperature=0.9,
        top_p=0.95,
        top_k=50,
        # num_beams=5,
        no_repeat_ngram_size=3,
    )
    return gened

def chat():
    while True:
        user_input = input('한 문  > ')
        if user_input == 'exit':
            break
        gen = translate(user_input)

# calculate BLEU score of test dataset
# use sacreBLEU with ko-mecab tokenizer
# pip install sacrebleu[ko]
def calculate_bleu():
    with open(PKL_PATH, 'rb') as f:
        dataset = pickle.load(f)
    dataset = list(dataset['test']['text'])
    bleu_score = 0
    bleu_score_list = []
    bleu = BLEU(tokenize='ko-mecab')
    for data in tqdm(dataset):
        data = data.split(SPLIT)
        context = data[0]
        target = data[1].split(tokenizer.eos_token)[0]
        gened = model.generate(
            **tokenizer(
                context + SPLIT, 
                return_tensors='pt', 
                return_token_type_ids=False
            ).to(device),
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.9,
            top_p=0.95,
            top_k=50,
            no_repeat_ngram_size=3,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )
        candidate = tokenizer.decode(gened[0], skip_special_tokens=True).split(SPLIT)[1]
        score = bleu.corpus_score([candidate], [[target]]).score
        print(target)
        print(candidate)
        print(score)
        bleu_score += score
        bleu_score_list.append(score)
    bleu_score /= len(dataset)
    print('BLEU score:', bleu_score)
    return bleu_score_list, bleu_score

chat()

# blist, bscore = calculate_bleu()
# with open('bleu.pkl', 'wb') as f:
#     pickle.dump(blist, f)
# print(bscore)