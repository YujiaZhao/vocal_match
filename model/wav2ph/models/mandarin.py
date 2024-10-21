"""from https://github.com/Plachtaa/VALL-E-X/g2p"""
import re
import cn2an
import jieba
from pypinyin import Style, lazy_pinyin, pinyin

# Convert numbers to Chinese pronunciation
def number_to_chinese(text):
    numbers = re.findall(r'\d+(?:\.?\d+)?', text)
    for number in numbers:
        text = text.replace(number, cn2an.an2cn(number), 1)
    return text

def add_spaces_around_chinese(text):
    # 定义正则表达式模式，用于匹配中文字符
    pattern = re.compile(r'([\u4e00-\u9fff])')
    
    # 使用正则表达式，在匹配到的中文字符前后插入空格
    modified_text = pattern.sub(r' \1 ', text)
    
    # 去除多余的空格，将连续的多个空格替换为一个空格，并去除两端的空格
    modified_text = re.sub(r'\s+', ' ', modified_text).strip()
    
    return modified_text

# Word Segmentation, and convert Chinese pronunciation to pinyin (bopomofo)
def chinese_to_pinyin(text, with_tone=True):
    #text = text.replace('、', '，').replace('；', '，').replace('：', '，')
    words = jieba.lcut(text, cut_all=False)
    raw_text = []
    g2p_text = []
    for word in words:
        word = word.strip()
        if word=="":
            continue
        if with_tone:
            pinyins = lazy_pinyin(word, style = Style.TONE3, neutral_tone_with_five=True)
        else:
            pinyins = lazy_pinyin(word, style = Style.NORMAL)
        if len(pinyins)==1:
            raw_text.append(word)
            g2p_text.append(pinyins[0])
        else:
            word = add_spaces_around_chinese(word).split(' ')
            assert len(pinyins)==len(word), print(word, pinyins)
            for _pinyins, _word in zip(pinyins, word):
                raw_text.append(_word)
                g2p_text.append(_pinyins)
    return raw_text, g2p_text

# Convert Chinese to IPA
def chinese_to_ipa(text, with_tone = True):
    r"""
    如果with_tone是True，返回带有音调，如果是False返回不带音调
    """
    try:
        text = number_to_chinese(text)
    except:
        text = ''
    raw_text, g2p_text = chinese_to_pinyin(text, with_tone)
    return raw_text, g2p_text

