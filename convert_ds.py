from get_pitch import get_pitch
from vocal_asr import infer_asr
import librosa
import numpy as np
import json

def load_audio(file_path):
    audio, sr = librosa.load(file_path,sr=44100,mono=True)
    return audio, sr

DICT_NAME = "dictionary/opencpop-extension.txt"

def load_pinyin_to_phoneme_map(filename):
    """
    从文本文件中读取拼音到音素的映射，并返回一个字典。
    :param filename: 包含拼音到音素映射的文件路径
    :return: 拼音到音素的字典
    """
    pinyin_to_phoneme_map = {}

    # 读取文件
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            # 去掉前后空格和换行符
            line = line.strip()

            # 跳过空行
            if not line:
                continue

            # 解析拼音和音素
            # 假设每行的格式是 "拼音: 音素 音素 ..."
            
            pinyin, phonemes = line.split('\t')
            # 将拼音和音素进行清理
            pinyin = pinyin.strip()
            phonemes = phonemes.strip().split()
            
            # 添加到字典中
            pinyin_to_phoneme_map[pinyin] = phonemes

    return pinyin_to_phoneme_map

def convert_pinyin_to_phonemes(text):
    """
    将输入的拼音文本转换为音素序列。
    :param text: 包含拼音的字符串（例如 'wo ai ni'）
    :param pinyin_to_phoneme_map: 拼音到音素的映射字典
    :return: 对应的音素序列列表（例如 ['w', 'o', 'a', 'i', 'n', 'i']）
    """
    # 将输入的拼音文本按空格分割为列表
    pinyin_list = text.split()
    phoneme_seq = []
    pinyin_to_phoneme_map = load_pinyin_to_phoneme_map(DICT_NAME)
    for pinyin in pinyin_list:
        # 从映射字典中获取对应的音素列表
        phonemes = pinyin_to_phoneme_map.get(pinyin, [pinyin])
        phoneme_seq.extend(phonemes)
        
    return phoneme_seq

def convert_ds(wav_path):
    audio, sr = load_audio(wav_path)
    time_step, f0, uv = get_pitch('parselmouth',audio)
    raw_text, g2p_text = infer_asr(audio,sr)
    
    # g2p_text包含标点符号，传入ph_seq时需要去除
    g2p_text_no_punc = g2p_text.replace(' ,', '').replace(' 。', '')
    # 将音素转换为拼音
    phoneme_seq=convert_pinyin_to_phonemes(g2p_text_no_punc)
    
    ds_content=[
        {
            "pinyin_seq":g2p_text,
            "ph_seq":" ".join(phoneme_seq),
            "f0_seq":" ".join(map("{:.1f}".format, f0)),
        }
    ]

    with open("./record/ds/record.ds", "w", encoding="utf-8") as json_file:
        json.dump(ds_content, json_file, ensure_ascii=False, indent=4)

    ds_file="./record/ds/record.ds"
    return ds_file

if __name__ == '__main__':

    convert_ds('./vocal_part/lsj-vocal_01_01.wav')
