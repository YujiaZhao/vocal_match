import json

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
        
    print(len(adjusted_phoneme_seq))

    return adjusted_phoneme_seq
def is_vowel(ph):
    # 判断音素是否为元音
    vowels = vowels = {
    "a", "o", "e", "i", "u", "v", "ai", "ei", "ao", "ou", "ia", "ie", "ua", "uo", "üe", 
    "iu", "ui", "an", "en", "ang", "eng", "ong","iao", "ian", "in", "iang", "ing", 
    "uan", "un", "uang", "ueng", "van", "vn", "er","AP","SP"}   
    return ph in vowels


                
def group_phonemes(phoneme_seq):
    """
    根据元音/辅音组合规则进行分组，并生成初始 ph_num。
    每个音素组应以元音/AP/SP开头，并包含前导辅音。
    :param phoneme_seq: 音素序列（如 ['w', 'o', 'a', 'i', 'n', 'i']）
    :return: 分组后的音素列表和对应的 ph_num
    """
    ph_groups = []
    addjusted_ph_num = []
    current_group = []

    for i, ph in enumerate(phoneme_seq):
        # 当遇到元音、'AP' 或 'SP' 时，结束当前组并开始新组
        if is_vowel(ph) or ph in {'AP', 'SP'}:
            # 如果当前组不为空，则将其保存为一个音素组
            if current_group:
                ph_groups.append(current_group)
                addjusted_ph_num.append(len(current_group))
                current_group = []

            # 启动新组，以元音、'AP' 或 'SP' 开头
            current_group.append(ph)

        # 如果是辅音，且当前组为空（即尚未开始一个新的元音组），则暂存它
        elif current_group:
            current_group.append(ph)

    # 将最后一个音素组加入
    if current_group:
        ph_groups.append(current_group)
        addjusted_ph_num.append(len(current_group))

    return ph_groups, addjusted_ph_num

def adjust_vowels(new_phoneme_num,original_phoneme_num,original_phoneme_dur):
    """
    调整音素序列中的元音拼音。
    """
    new_phoneme_dur=[]
    for i in range(len(original_phoneme_num)):
        idx_for_dur=sum(original_phoneme_num[:i])
        if original_phoneme_num[i]==1 and new_phoneme_num[i]==2:
            # 原音素组为元音，新音素组为元+辅音，需要拆分时长
            new_dur_group=list(0.7*original_phoneme_dur[idx_for_dur],0.3*original_phoneme_dur[idx_for_dur])
            new_phoneme_dur=original_phoneme_dur[:idx_for_dur]+new_dur_group+original_phoneme_dur[idx_for_dur+1:]
  
            # print(new_phoneme_dur)
        if original_phoneme_num[i]==2 and new_phoneme_num[i]==1:
            # 原音素组为元+辅音，新音素组为元音，需要合并时长
            new_dur=original_phoneme_dur[idx_for_dur]+original_phoneme_dur[idx_for_dur+1]
            new_phoneme_dur=original_phoneme_dur[:idx_for_dur]+[new_dur]+original_phoneme_dur[idx_for_dur+2:]
        else:
            new_phoneme_dur=original_phoneme_dur
            
    return new_phoneme_dur

def replace_lyrics(text,original_phoneme_seq,original_phoneme_num,original_phoneme_dur):
    """
    将拼音文本替换为音素序列。
    :param text: 包含拼音的字符串（例如 'wo ai ni'）
    :return: 对应的音素序列字符串（例如 'w o a i n i'）
    """
    new_phoneme_seq = convert_pinyin_to_phonemes(text)
    print(' '.join(map(str, new_phoneme_seq)))

    adjusted_phoneme_seq = add_sp_ap_to_phonemes(new_phoneme_seq, original_phoneme_seq)
    print(' '.join(map(str, adjusted_phoneme_seq)))

    ph_groups, addjusted_ph_num=group_phonemes(adjusted_phoneme_seq)
    print(' '.join(map(str, addjusted_ph_num)))

    new_phoneme_dur=adjust_vowels(addjusted_ph_num,original_phoneme_num,original_phoneme_dur)
    print(' '.join(map(str, new_phoneme_dur)))


    return adjusted_phoneme_seq,addjusted_ph_num,new_phoneme_dur


