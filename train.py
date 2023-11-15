import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model, PeftModel
import pickle

# pip install torch transformers peft bitsandbytes scipy datasets tensorboard
# apt update
# apt install vim
# export HF_HOME=/workspace/hf

# on A100 80GB, 1 epoch takes about 80 hours, 5000 steps

# MODEL_ID = "EleutherAI/polyglot-ko-5.8b"
MODEL_ID = "nlpai-lab/kullm-polyglot-5.8b-v2"
# MODEL_ID = "KT-AI/midm-bitext-S-7B-inst-v1"
PEFT_ID = "hankor"
LOGGING_DIR = "hankor/runs"
PKL_PATH = "Preprocessed.pkl"
PAD_TOKEN = "<|unused0|>"
SPLIT = '\n\n### 응답:\n'
BATCH_SIZE = 1 # 24 on A100
ACC_STEPS = 16 # 4 on A100
LEARNING_RATE = 3e-4
LOGGING_STEPS = 10
LR_SCHEDULER_TYPE = "cosine_with_restarts"
STEPS = 10000
LORA_R = 64
LORA_ALPHA = 128
LORA_DROPOUT = 0.05
SAVE_STEPS = 200
EVAL_STEPS = 200
WARMUP_STEPS = 200 # 50 on A100
NUM_WORKERS = 0
CONTINUE_TRAINING = 0

if __name__ == '__main__':
    torch.multiprocessing.freeze_support()

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    # bnb_config = BitsAndBytesConfig(
    #     load_in_8bit=True,
    # )

    device = torch.device("cuda:0" if torch.cuda.is_available() 
                        else "mps" if torch.backends.mps.is_available()
                        else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb_config, device_map=device, trust_remote_code=True)

    with open(PKL_PATH, 'rb') as f:
        dataset = pickle.load(f)

    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

# for polyglot-ko & kullm model
    config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=[
            "query_key_value",
            "dense",
            "dense_h_to_4h",
            "dense_4h_to_h",
        ],
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM"
    )

# for midm model
    # config = LoraConfig(
    #     r=LORA_R,
    #     lora_alpha=LORA_ALPHA,
    #     target_modules=[
    #         "c_attn",
    #         "c_proj",
    #         "c_fc",
    #     ],
    #     lora_dropout=LORA_DROPOUT,
    #     bias="none",
    #     task_type="CAUSAL_LM"
    # )

# for llama-2-kor model
    # config = LoraConfig(
    #     r=LORA_R,
    #     lora_alpha=LORA_ALPHA,
    #     target_modules=[
    #         "q_proj",
    #         "k_proj",
    #         "v_proj",
    #         "o_proj",
    #         "gate_proj",
    #         "up_proj",
    #         "down_proj",
    #     ],
    #     lora_dropout=LORA_DROPOUT,
    #     bias="none",
    #     task_type="CAUSAL_LM"
    # )

    if CONTINUE_TRAINING == 1: # 1 is True, 0 is False
        model = PeftModel.from_pretrained(model, PEFT_ID, is_trainable=True)
    else:
        model = get_peft_model(model, config)

    tokenizer.pad_token = PAD_TOKEN

    class MaskedTrainer(Trainer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.split_tokens = torch.Tensor(tokenizer(SPLIT)['input_ids']).to(device)
            self.split_tokens_len = len(self.split_tokens)
        
        def compute_loss(self, model, inputs, return_outputs=False):
            for labels_seq in inputs['labels']:
                maskIndex = (labels_seq.unfold(0, self.split_tokens_len, 1) == self.split_tokens).all(dim=1).nonzero().squeeze()
                if maskIndex.numel() > 0:
                    labels_seq[:maskIndex+self.split_tokens_len] = -100

            outputs = model(**inputs)
            loss = outputs['loss']

            return (loss,outputs) if return_outputs else loss

    trainer = MaskedTrainer(
        model=model,
        train_dataset=dataset['train'],
        eval_dataset=dataset['eval'],
        args=TrainingArguments(
            do_train=True,
            do_eval=True,
            per_device_train_batch_size=BATCH_SIZE,
            per_device_eval_batch_size=BATCH_SIZE,
            evaluation_strategy="steps",
            gradient_accumulation_steps=ACC_STEPS,
            max_steps=STEPS,
            eval_steps=EVAL_STEPS,
            warmup_steps=WARMUP_STEPS, # 200 was used in koalpaca training
            learning_rate=LEARNING_RATE,
            bf16=True,
            logging_steps=LOGGING_STEPS,
            logging_dir=LOGGING_DIR,
            report_to="tensorboard",
            lr_scheduler_type=LR_SCHEDULER_TYPE,
            save_steps=SAVE_STEPS,
            dataloader_num_workers=NUM_WORKERS,
            output_dir=PEFT_ID
        ),
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )
    model.config.use_cache = False

    if CONTINUE_TRAINING == 1:
        trainer.train(resume_from_checkpoint=PEFT_ID)
    else:
        trainer.train()

    trainer.save_model(PEFT_ID)