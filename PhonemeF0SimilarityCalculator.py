import json
import numpy as np
from fastdtw import fastdtw
from difflib import SequenceMatcher

class PhonemeF0SimilarityCalculator:
    def __init__(self, reference_file):
        # 只需初始化一次，加载参考文件
        self.reference_file = reference_file
        self.pho_ref, self.f0_ref = self.load_file(reference_file)

    @staticmethod
    def read_json(path):
        with open(path, 'r', encoding='utf8') as f:
            return json.load(f)

    @staticmethod
    def phoneme_similar(s1, s2):
        return SequenceMatcher(None, s1, s2).ratio()

    @staticmethod
    def process_f0(f0_seq):
        """将 F0 序列转换为浮点数列表"""
        return [float(value) for value in f0_seq.split()]

    def f0_similarity(self, f0_seq):
        f0_ref_flat = np.array(self.f0_ref).ravel()
        f0_seq_flat = np.array(f0_seq).ravel()
        distance, _ = fastdtw(f0_ref_flat, f0_seq_flat, dist=2)

        max_length = max(len(f0_ref_flat), len(f0_seq_flat))
        max_possible_distance = max_length * np.max([np.max(f0_ref_flat), np.max(f0_seq_flat)])
        similarity = max(0, 1 - distance / max_possible_distance)

        return similarity

    def load_file(self, file_path):
        data = self.read_json(file_path)[0]
        pho_seq = data['ph_seq']
        f0_seq = self.process_f0(data['f0_seq'])
        return pho_seq, f0_seq


    def compare_to_file(self, file_path):
        """比较参考文件和另一个文件的相似度"""
        pho_seq, f0_seq = self.load_file(file_path)
        phoneme_sim = self.phoneme_similar(self.pho_ref, pho_seq)
        f0_sim = self.f0_similarity(f0_seq)
        return phoneme_sim, f0_sim

    def compare_to_multiple_files(self, file_list):
        """批量比较参考文件和多个文件，返回相似度最高的文件"""
        similarities = []
        for i, file_path in enumerate(file_list):
            phoneme_sim, f0_sim = self.compare_to_file(file_path)
            similarities.append((phoneme_sim, f0_sim, i, file_path))

        # 按照F0和音素相似度的平均值进行排序
        similarities.sort(reverse=True, key=lambda x: (x[0] + x[1]) / 2)
        return similarities[0]  # 返回最相似的文件的音素相似度、F0相似度、索引和路径


# 使用示例
if __name__ == "__main__":
    # 假设有一个文件库
    song_library = ["file1.json", "file2.json", "file3.json", "file4.json"]
    
    # 初始化相似度计算器，传入参考文件
    calculator = PhonemeF0SimilarityCalculator("reference.json")
    
    # 批量比较，返回最相似的文件
    most_similar_file = calculator.compare_to_multiple_files(song_library)
    
    print(f"Most Similar File: {most_similar_file[1]} with similarity {most_similar_file[0]}")
