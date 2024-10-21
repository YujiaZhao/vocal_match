import torch
import librosa
import time
import argparse

from model.wav2ph.models import whisper_asr, mandarin


def load_asr_model():
    # 检测GPU
    if torch.cuda.is_available():
        device_name = "cuda"
        print('gpu')
        device = torch.device(device_name)
    else:
        device_name = "cpu"
        device = torch.device(device_name)
    asr_model = whisper_asr.load_asr_model(
            "model/wav2ph/checkpoints/whisper",     # NOTE: 修改为你自己的checkpoint 位置
            device_name,
            compute_type="float32",
            threads=4,
            asr_options={
                "initial_prompt": "Um, Uh, Ah. Like, you know. I mean, right. Actually. Basically, and right? okay. Alright. Emm. So. Oh. 生于忧患,死于安乐。岂不快哉?当然,嗯,呃,就,这样,那个,哪个,啊,呀,哎呀,哎哟,唉哇,啧,唷,哟,噫!微斯人,吾谁与归?ええと、あの、ま、そう、ええ。äh, hm, so, tja, halt, eigentlich. euh, quoi, bah, ben, tu vois, tu sais, t'sais, eh bien, du coup. genre, comme, style. 응,어,그,음."
            },
        )

    return asr_model
asr_model=load_asr_model()
def asr(audio, sample_rate = 44100, language='zh'):
    # resample to 16k
    if sample_rate != 16000:
        temp_audio = librosa.resample(
            audio, orig_sr=sample_rate, target_sr=16000
        )
    else:
        temp_audio = audio
    
    segment = [{"start":0, "end": len(audio)/sample_rate}]
    
    transcribe_result = asr_model.transcribe(
        temp_audio,
        segment,
        batch_size=16,
        language=language,
        print_progress=True,
    )
    result = transcribe_result["segments"][0]['text']
    return result

def process_one(audio, sr,with_tone = False):
    r"""
    audio_path: 音频路径
    with_tone: 音频是否有音调. 如果with_tone是True, 返回带有音调, 如果是False返回不带音调
    """
    text = asr(audio, sr, 'zh')

    # text preprocess
    text = text.replace("\n", "").strip(" ")
    raw_text, g2p_text = mandarin.chinese_to_ipa(text, with_tone)

    return raw_text, g2p_text
    
def infer_asr(audio,sr, with_tone = False):
# 检测运行时间
    start_time = time.time()
    # Load models
    # ASR
    raw_text, g2p_text = process_one(audio,sr, with_tone)
    raw_text = ' '.join(raw_text)
    g2p_text = ' '.join(g2p_text)
    print(raw_text, g2p_text)
    end_time = time.time()
    print("识别所用时间: ", end_time - start_time)

    return raw_text, g2p_text



if __name__ == "__main__":
    infer_asr('vocal_part/xfsg-vocal_01_01.wav', False)