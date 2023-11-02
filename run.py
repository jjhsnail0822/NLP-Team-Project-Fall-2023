import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextStreamer
from peft import PeftConfig, PeftModel

PEFT_ID = "hankor"
MAX_NEW_TOKENS = 2048

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
streamer = TextStreamer(tokenizer, skip_prompt=True)

model.to(device)
model.eval()
model.config.use_cache = True

def translate(user_input):
    context = f"아래는 작업을 설명하는 명령어와 추가 컨텍스트를 제공하는 입력이 짝을 이루는 예제입니다. 요청을 적절히 완료하는 응답을 작성하세요.\n\n### 명령어:\n한문을 한국어로 번역하세요.\n\n### 입력:\n{user_input}\n\n### 응답:\n"
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

chat()