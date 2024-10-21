import pyaudio
import wave
import numpy as np
import librosa
from scipy.spatial import distance
import time
import json


# print(ph_num)
# new_seq_data="SP AP r e sh u o g u ang x i h ao f eng g u ang AP sh an q ing sh ui x iu h ao d i f ang o h ao d i f ang SP "
# new_seq_data=new_seq_data.split()
# print(new_seq_data)

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

# 示例：读取名为 "pinyin_phoneme_map.txt" 的文件
filename = "dictionary/opencpop-extension.txt"

# TODO:添加sp
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

def add_sp_ap_to_phonemes(new_phoneme_seq, original_phoneme_seq):
    """
    根据原有音素序列为新的音素序列添加 'SP' 和 'AP'。
    :param new_phoneme_seq: 新生成的音素序列（不包含 'SP' 和 'AP'）
    :param original_phoneme_seq: 原有的音素序列（包含 'SP' 和 'AP'）
    :return: 调整后的新音素序列（包含 'SP' 和 'AP'）
    """
    adjusted_phoneme_seq = []
    new_index = 0

    for original_ph in original_phoneme_seq:
        if original_ph in {'SP', 'AP'}:
            # 如果原音素是 'SP' 或 'AP'，在新的音素序列中同样插入
            adjusted_phoneme_seq.append(original_ph)
        else:
            # 如果是其他音素，则从新的音素序列中取出一个音素加入
            if new_index < len(new_phoneme_seq):
                adjusted_phoneme_seq.append(new_phoneme_seq[new_index])
                new_index += 1

    # 添加剩余的新音素（如果有的话）
    while new_index < len(new_phoneme_seq):
        adjusted_phoneme_seq.append(new_phoneme_seq[new_index])
        new_index += 1
    print(adjusted_phoneme_seq)

    return adjusted_phoneme_seq


def is_vowel(ph):
    # 简单判断音素是否为元音
    vowels = {"a", "e", "i", "o", "u", "er", "ai", "ei", "ou", "an", "ang", "en", "eng", "ong","AP","SP"}
    return ph in vowels

def group_phonemes(phoneme_seq):
    """
    根据元音/辅音组合规则进行分组，并生成初始 ph_num。
    :param phoneme_seq: 音素序列（如 ['w', 'o', 'a', 'i', 'n', 'i']）
    :return: 分组后的音素列表和对应的 ph_num
    """
    ph_groups = []
    ph_num = []
    current_group = []

    for ph in phoneme_seq:
        current_group.append(ph)
        if is_vowel(ph):  # 当遇到元音时，将当前音素组作为一个整体
            ph_groups.append(current_group)
            ph_num.append(len(current_group))
            current_group = []

    # 处理剩余的音素
    if current_group:
        ph_groups.append(current_group)
        ph_num.append(len(current_group))
    
    return ph_groups, ph_num


def adjust_phoneme_groups(ph_groups, target_count):
    """
    调整音素组的数量，使其与目标数量 target_count 对齐。
    :param ph_groups: 原始的音素组列表（如 [['w', 'o'], ['a', 'i'], ['n', 'i']])
    :param target_count: 目标音素组数量，与原始音素组数量一致
    :return: 调整后的音素组列表
    """
    adjusted_groups = ph_groups.copy()

    # 如果音素组数量少于目标数量，进行拆分
    while len(adjusted_groups) < target_count:
        for i in range(len(adjusted_groups)):
            if len(adjusted_groups[i]) > 1:
                split_group = adjusted_groups[i]
                adjusted_groups[i] = split_group[:1]
                adjusted_groups.insert(i + 1, split_group[1:])
                break
    
    # 如果音素组数量多于目标数量，进行合并
    while len(adjusted_groups) > target_count:
        for i in range(len(adjusted_groups) - 1):
            merged_group = adjusted_groups[i] + adjusted_groups[i + 1]
            adjusted_groups[i] = merged_group
            del adjusted_groups[i + 1]
            break

    return adjusted_groups

def calculate_ph_dur_with_adjustment(adjusted_groups, note_dur):
    """
    重新计算每个音素组的时长，使其与音符时长匹配。
    :param adjusted_groups: 调整后的音素组列表
    :param note_dur: 音符时长列表
    :return: 新的 ph_dur 列表
    """
    ph_dur = []
    note_idx = 0

    for group in adjusted_groups:
        duration = note_dur[note_idx] if note_idx < len(note_dur) else note_dur[-1]
        num_phonemes = len(group)
        per_ph_duration = duration / num_phonemes
        ph_dur.extend([per_ph_duration] * num_phonemes)
        note_idx += 1
    
    return ph_dur

def replace_lyrics_with_adjustment(text, original_ph_seq,original_ph_num, note_seq, note_dur):
    # 1. 生成音素序列
    ph_seq = convert_pinyin_to_phonemes(text,)

    ph_seq=add_sp_ap_to_phonemes(ph_seq, original_ph_seq)
    ph_str=" ".join(ph_seq)
    print(ph_str)
    
    # 2. 根据元音对齐规则生成初始 ph_num
    ph_groups, initial_ph_num = group_phonemes(ph_seq)
    
    # 3. 调整音素组数量
    adjusted_groups = adjust_phoneme_groups(ph_groups, len(original_ph_num))
    
    # 4. 生成新的 ph_num（基于调整后的音素组）
    adjusted_ph_num = [len(group) for group in adjusted_groups]
    
    # 5. 计算新的 ph_dur
    ph_dur = calculate_ph_dur_with_adjustment(adjusted_groups, note_dur)
    
    # 6. 生成最终的音素序列
    ph_seq_str = " ".join([" ".join(group) for group in adjusted_groups])
    
    return {
        "ph_seq": ph_seq_str,
        "ph_num": " ".join(map(str, adjusted_ph_num)),
        "ph_dur": " ".join(map(str, ph_dur)),
        "note_seq": " ".join(note_seq),
        "note_dur": " ".join(map(str, note_dur))
    }

# 示例输入
text = "ren shuo shan xi hao feng guang shan qing shui xiu hao di fang lo hao di fang"  # 新的拼音输入

with open('test_vocal.ds', 'r') as file:
    data = json.load(file)

print(data[0]['ph_seq'])

ph_seq=data[0]['ph_seq'].split()
ph_num=data[0]['ph_num'].split()
note_dur=data[0]['note_dur'].split()
note_seq=data[0]['note_seq'].split()

ph_num = list(map(int, ph_num))
note_dur = list(map(float, note_dur))

# 替换歌词并生成结果
result = replace_lyrics_with_adjustment(text, ph_seq,ph_num, note_seq, note_dur)
# print(result)
