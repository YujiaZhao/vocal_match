# 使用用户输入的歌曲ds，拿到拼音序列

# 使用拼音序列在大模型中生成对唱歌词

# 获取匹配旋律的歌曲的路径

# 替换该歌曲的歌词

# 推理生成新的歌声

# 播放新的歌声

import json
from replace_lyrics import replace_lyrics

from model.DiffSinger.scripts.infer import acoustic

def lyric_generation(text):
    # 输入：拼音
    # 接入大模型生成歌词

    pass

def create_new_ds(new_lyric,ds):
    with open(ds, 'r') as file:
        data = json.load(file)
    original_ph_seq=data[0]['ph_seq'].split()
    original_phoneme_num=list(map(int, data[0]['ph_num'].split()))
    original_phoneme_dur=list(map(float, data[0]['ph_dur'].split()))

    new_phoneme_seq, new_phoneme_num, new_phoneme_dur = replace_lyrics(new_lyric,original_ph_seq,original_phoneme_num,original_phoneme_dur)

    data[0]['ph_seq']=" ".join(new_phoneme_seq)
    data[0]['ph_num']=" ".join(map(str, new_phoneme_num))
    data[0]['ph_dur']=" ".join(map(str, new_phoneme_dur))

    output_ds='response/response.ds'
    with open(output_ds, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return output_ds




def infer(input_ds,output_wav):
    # 输入：替换过歌词的Ds路径
    acoustic(input_ds,output_wav)
    return output_wav
    


def find_similar_ds(similar_song_ds,record_ds):
    with open(record_ds, 'r') as file:
        data = json.load(file)
    text=data[0]['pinyin_seq']
    new_lyrics=lyric_generation(text)

    new_ds=create_new_ds(new_lyrics,similar_song_ds)
    result=infer(new_ds,'response/response.wav')

    return result
