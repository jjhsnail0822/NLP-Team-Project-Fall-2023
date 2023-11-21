from transformers import AutoTokenizer, AutoModelForCausalLM, GPTQConfig
from peft import PeftModel
import pickle

MODEL_ID = "nlpai-lab/kullm-polyglot-5.8b-v2"
PEFT_ID = "hankor"
MERGED_ID = "hankor-merged"
QUANTIZED_ID = "hankor-quantized-8bit"
PKL_PATH = "Preprocessed.pkl"
PAD_TOKEN = "<|unused0|>"
QUANTIZE_BITS = 8

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = PAD_TOKEN
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map='auto')
model = PeftModel.from_pretrained(model, PEFT_ID, is_trainable=True)

model = model.merge_and_unload()
model.save_pretrained(MERGED_ID)
model = None

with open(PKL_PATH, 'rb') as f:
    dataset = pickle.load(f)

gptq_config = GPTQConfig(bits=QUANTIZE_BITS, dataset=dataset['eval']['text'], tokenizer=tokenizer, use_exllama=False)
model = AutoModelForCausalLM.from_pretrained(MERGED_ID, quantization_config=gptq_config, device_map='auto')
model.save_pretrained(QUANTIZED_ID)