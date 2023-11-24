# Hankor - 고전 한문 번역기 프로젝트

고전 한문(Classical Chinese)을 현대 한국어로 번역하는 AI 기반 번역기입니다. 원문-번역문 쌍 약 48만 건에 대해, RTX 4090 환경에서 QLoRA를 통해 약 2.6일간 학습되었습니다. 현재 checkpoint는 공개하고 있지 않습니다.

이 프로젝트에 사용된 모델은 [KULLM 5.8B v2](https://github.com/nlpai-lab/KULLM)를 기반으로 학습되었습니다.

# Prerequisites

하드웨어 요구 사항 - CUDA 11.8 이상이 설치된 NVIDIA GPU가 필요합니다. VRAM은 최소 8GB 이상 필요하며, 권장 VRAM은 12GB 이상입니다.

## For Linux

```
pip install torch transformers peft bitsandbytes scipy datasets sacrebleu[ko] auto-gptq
```

## For Windows

```
pip install torch transformers peft scipy datasets sacrebleu[ko] auto-gptq
```

Windows 환경에서는 bitsandbytes 패키지가 기본적으로 지원되지 않습니다. 따라서 다음 링크에서 제시하는 방법을 통해 수동으로 설치해야 합니다.
<https://github.com/jllllll/bitsandbytes-windows-webui>

# Getting Started

실행에는 모델 폴더가 필요합니다. 현재 모델 및 checkpoint는 공개하고 있지 않습니다.

다운로드 받은 모델 폴더를 그대로 run.py와 같은 경로에 복사합니다. 해당 경로에서 다음 커맨드를 통해 실행합니다.
```
python run.py --default
```

사용할 수 있는 옵션은 다음과 같습니다.

## --default
모델 폴더 'hankor'가 필요합니다. bitsandbytes 4bit로 양자화된 QLoRA 모델을 실행합니다. 기본 모델(KULLM 5.8B)이 자동으로 다운로드됩니다. (추천 옵션)
## --lora-merged-8bit
모델 폴더 'hankor-lora-merged-8bit'가 필요합니다. LoRA가 병합된 bitsandbytes 8bit 양자화 모델을 실행합니다.
## --gptq-8bit
모델 폴더 'hankor-quantized-8bit'가 필요합니다. GPTQ 8bit로 양자화된 모델을 실행합니다.
## --gptq-4bit
모델 폴더 'hankor-quantized-4bit'가 필요합니다. GPTQ 4bit로 양자화된 모델을 실행합니다.
## --bleu
sacreBLEU를 통해 BLEU 평가를 진행합니다. default 모델의 평가만을 지원합니다. 평가에는 학습 데이터셋인 Preprocessed.pkl 파일이 필요합니다. 현재 학습 데이터셋은 공개하고 있지 않습니다.

# Training
RTX 4090 환경에서 약 2.6일간 4300 steps, 0.84 epoch를 학습하였습니다.

train/loss

![image](https://github.com/jjhsnail0822/NLP-Team-Project-Fall-2023/assets/86543294/ce3be6c2-0671-4864-9b18-c0ac8d0aa8c4)

eval/loss

![image](https://github.com/jjhsnail0822/NLP-Team-Project-Fall-2023/assets/86543294/f7bcbb2f-57ea-4ab5-898b-06e646832e3a)


# Evaluation
default hankor 모델은 sacreBLEU 평가에서 26.53 BLEU를 기록했습니다.

![image](https://github.com/jjhsnail0822/NLP-Team-Project-Fall-2023/assets/86543294/4ac339e2-1e97-4934-aaa8-6f99b3cb887c)
