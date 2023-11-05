from konlpy.tag import Okt
from nltk.translate.bleu_score import sentence_bleu
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextStreamer
from peft import PeftConfig, PeftModel
import pickle

PEFT_ID = "hankor"
MAX_NEW_TOKENS = 2048
CONTEXT_CHN = '### 명령어: 한문을 한국어로 번역하세요.\n### 한문: '
SPLIT = '\n### 한국어: '
PKL_PATH = 'Preprocessed.pkl'

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

device = torch.device("cuda:0" if torch.cuda.is_available() 
                      else "mps" if torch.backends.mps.is_available()
                      else "cpu")
config = PeftConfig.from_pretrained(PEFT_ID)
model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path, quantization_config=bnb_config, device_map=device)
model = PeftModel.from_pretrained(model, PEFT_ID)
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path, skip_special_tokens=True)
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

model.to(device)
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
    )
    return gened

def chat():
    while True:
        user_input = input('한 문  > ')
        if user_input == 'exit':
            break
        gen = translate(user_input)

# calculate BLEU score
# to be implemented faster
def calculate_bleu():
    okt = Okt()
    with open(PKL_PATH, 'rb') as f:
        dataset = pickle.load(f)
    dataset = list(dataset['test']['text'])
    bleu_score = 0
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
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )
        candidate = tokenizer.decode(gened[0], skip_special_tokens=True).split(SPLIT)[1]
        target = okt.morphs(target)
        candidate = okt.morphs(candidate)
        score = sentence_bleu([target], candidate)
        print(score)
        bleu_score += score
    bleu_score /= len(dataset)
    print('BLEU score:', bleu_score)

chat()