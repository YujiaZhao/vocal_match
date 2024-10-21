import os
import pyaudio
import wave
import time
from PhonemeF0SimilarityCalculator import PhonemeF0SimilarityCalculator
import pygame
from convert_ds import convert_ds
from vocal_generation import vocal_generation

# 基本方案
# 1. 识别旋律(pitch)和歌词
# 1). 提取用户F0和歌词
# 2). 从曲库中找到最相似的旋律和歌词,存放到一个list里
#     如果旋律相同,歌词相同.就返回其下一句旋律和歌词给DiffSinger合成（为提高实时性，可以提前合成好）.
#     如果旋律相同,歌词不同.就返回其下一句旋律,歌词由LLM生成,最终DiffSinger合成.

# ds 库的数据结构
# [
#     '山歌好比春江水':
#     {
#         '1':  
#           {
#               'phone':['shan','ge','hao','bi','chun','jiang','shui'],
#               'f0':   [...]
#           }
#         '2': 
#         '3': 
#         ...
#     },
# ]

# 旋律相似度:DTW算法,计算用户的旋律和DS库的旋律相似性
# 文本相似度:计算音素的相似性

# 曲库中的歌曲A段路径列表

# 设置路径
base_path = 'E:/01-STUDY/02_master/06_project/20240809_liusanjie/vocal-match/'
songA_library = [
    os.path.join(base_path, 'vocal_part/lsj-vocal_01_01.wav'),
    os.path.join(base_path, 'vocal_part/xfsg-vocal_01_01.wav')
]

songA_ds_library = [
    os.path.join(base_path, 'database/songA/lsj-vocal_01_01.ds'),
    os.path.join(base_path, 'database/songA/xfsg-vocal_01_01.ds')
]

songB_library = [
    os.path.join(base_path, 'vocal_respond_test/lsj-vocal_01_02.wav'),
    os.path.join(base_path, 'vocal_respond_test/xfsg-vocal_01_02.wav')
]

songB_ds_library = [
    os.path.join(base_path, 'database/songB/lsj-vocal_01_02.ds'),
    os.path.join(base_path, 'database/songB/xfsg-vocal_01_02.ds')
]

def find_similar_songs(new_song_ds_path):
    
    # Initialize calculator for new song
    calculator = PhonemeF0SimilarityCalculator(new_song_ds_path)

    # Find most similar songs from the songA_ds_library
    return calculator.compare_to_multiple_files(songA_ds_library)

def match_songs(new_song_ds_path):
    """
    根据 new_song_path 的音高特征向量，
    在 songA_ds_library 中找到最相似的歌曲的索引,
    并返回最相似歌曲的路径和相似度

    参数:
    new_song_ds_path: 新录制的歌曲的路径

    返回:
    tuple: (最相似歌曲路径, 对唱歌曲路径, 相似度) if similarity > 80%
    None: 未找到相似歌曲
    """
    # Get the most similar song's index, similarity score, and path
    phoneme_sim, f0_sim, most_similar_index, similar_song_path = find_similar_songs(new_song_ds_path)
    
    
    print(f"最相似歌曲的索引: {most_similar_index}")
    print(f"最相似歌曲的路径: {similar_song_path}")
    print(f"音素相似度: {phoneme_sim}")
    print(f"F0 相似度: {f0_sim}")

    if f0_sim > 0.8 and phoneme_sim > 0.8:
        # 如果 F0 和音素相似度都大于 80%
        similar_songs_paths = songA_ds_library[most_similar_index]
        respond_song_path = songB_library[most_similar_index]
        return {"status": "found", "similar_song": similar_songs_paths, "respond_song": respond_song_path, "f0_sim": f0_sim, "phoneme_sim": phoneme_sim}

    elif f0_sim > 0.8 and phoneme_sim <= 0.8:
        # 如果 F0 相似度 > 80% 但音素相似度 <= 80%
        similar_songs_paths = songA_ds_library[most_similar_index]
        respond_song_path = songB_library[most_similar_index]
        respond_ds_path=songB_ds_library[most_similar_index]
        return {"status": "melody_only", "similar_song": similar_songs_paths, "similar_song_ds": respond_ds_path, "f0_sim": f0_sim, "phoneme_sim": phoneme_sim, "message": "待使用该旋律生成对唱"}

    else:
        # 如果 F0 和音素相似度都小于 80%
        return {"status": "not_found", "message": "未找到对应旋律，请重新演唱"}


def play_music(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

if __name__ == "__main__":
    # Record new audio and convert it to DS format
    new_song_path = os.path.join(base_path, "record/wavs/lsj_A1_b4_MixDown.wav")
    new_song_ds_path = convert_ds(new_song_path)

    # Find and handle the results based on conditions
    result = match_songs(new_song_ds_path)

    if result["status"] == "found":
        print(f"找到相似歌曲: {result['similar_song']} 和对唱歌曲: {result['respond_song']}")
        play_music(result["respond_song"])

    elif result["status"] == "not_found":
        similar_song_ds=result["similar_song_ds"]
        print(similar_song_ds)
        print(result["message"])
        response= vocal_generation(similar_song_ds,'response/response.wav')
        play_music(response)

    elif result["status"] == "melody_only":
        print(f"{result['message']}: {result['similar_song']}")







