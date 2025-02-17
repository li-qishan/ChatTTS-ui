import os
import sys,re
from pathlib import Path


import LangSegment
LangSegment.setfilters(["zh","en","ja"])

def num_to_chinese(num):
    num_str = str(num)
    chinese_digits = "零一二三四五六七八九"
    units = ["", "十", "百", "千"]
    big_units = ["", "万", "亿", "兆"]
    result = ""
    zero_flag = False  # 标记是否需要加'零'
    part = []  # 存储每4位的数字
    
    # 将数字按每4位分组
    while num_str:
        part.append(num_str[-4:])
        num_str = num_str[:-4]
    
    for i in range(len(part)):
        part_str = ""
        part_zero_flag = False
        for j in range(len(part[i])):
            digit = int(part[i][j])
            if digit == 0:
                part_zero_flag = True
            else:
                if part_zero_flag or (zero_flag and i > 0 and not result.startswith(chinese_digits[0])):
                    part_str += chinese_digits[0]
                    zero_flag = False
                    part_zero_flag = False
                part_str += chinese_digits[digit] + units[len(part[i]) - j - 1]
        if part_str.endswith("零"):
            part_str = part_str[:-1]  # 去除尾部的'零'
        if part_str:
            zero_flag = True
        
        if i > 0 and not set(part[i]) <= {'0'}:  # 如果当前部分不全是0，则加上相应的大单位
            result = part_str + big_units[i] + result
        else:
            result = part_str + result
    
    # 处理输入为0的情况或者去掉开头的零
    result = result.lstrip(chinese_digits[0])
    if not result:
        return chinese_digits[0]
    
    return result

def num_to_english(num):
    
    num_str = str(num)
    # English representations for numbers 0-9
    english_digits = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    units = ["", "ten", "hundred", "thousand"]
    big_units = ["", "thousand", "million", "billion", "trillion"]
    result = ""
    need_and = False  # Indicates whether 'and' needs to be added
    part = []  # Stores each group of 4 digits
    is_first_part = True  # Indicates if it is the first part for not adding 'and' at the beginning
    
    # Split the number into 3-digit groups
    while num_str:
        part.append(num_str[-3:])
        num_str = num_str[:-3]
    
    part.reverse()
    
    for i, p in enumerate(part):
        p_str = ""
        digit_len = len(p)
        if int(p) == 0 and i < len(part) - 1:
            continue
        
        hundreds_digit = int(p) // 100 if digit_len == 3 else None
        tens_digit = int(p) % 100 if digit_len >= 2 else int(p[0] if digit_len == 1 else p[1])
        
        # Process hundreds
        if hundreds_digit is not None and hundreds_digit != 0:
            p_str += english_digits[hundreds_digit] + " hundred"
            if tens_digit != 0:
                p_str += " and "
        
        # Process tens and ones
        if 10 < tens_digit < 20:  # Teens exception
            teen_map = {
                11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
                16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen"
            }
            p_str += teen_map[tens_digit]
        else:
            tens_map = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
            tens_val = tens_digit // 10
            ones_val = tens_digit % 10
            if tens_val >= 2:
                p_str += tens_map[tens_val] + (" " + english_digits[ones_val] if ones_val != 0 else "")
            elif tens_digit != 0 and tens_val < 2:  # When tens_digit is in [1, 9]
                p_str += english_digits[tens_digit]
        
        if p_str and not is_first_part and need_and:
            result += " and "
        result += p_str
        if i < len(part) - 1 and int(p) != 0:
            result += " " + big_units[len(part) - i - 1] + ", "
        
        is_first_part = False
        if int(p) != 0:
            need_and = True
    
    return result.capitalize()


def num2text(text,lang="zh"):
    numtext=[' zero ',' one ',' two ',' three ',' four ',' five ',' six ',' seven ',' eight ',' nine ']
    point=' point '
    if lang=='zh':
        numtext=['零','一','二','三','四','五','六','七','八','九']
        point='点'
    # 取出数字 number_list= [('1000200030004000.123', '1000200030004000', '123'), ('23425', '23425', '')]
    number_list=re.findall('((\d+)(?:\.(\d+))?)',text)
    print(number_list)
    if len(number_list)>0:            
        #dc= ('1000200030004000.123', '1000200030004000', '123')
        for m,dc in enumerate(number_list):
            if len(dc[1])>16:
                continue
            int_text=num_to_chinese(dc[1]) if lang=='zh' else num_to_english(dc[1])
            if len(dc)==3:
                int_text+=point+"".join([numtext[int(i)] for i in dc[2]])
            
            text=text.replace(dc[0],int_text)
    if lang=='zh':
        return text.replace('1','一').replace('2','二').replace('3','三').replace('4','四').replace('5','五').replace('6','六').replace('7','七').replace('8','八').replace('9','九').replace('0','零')
        
    return text.replace('1',' one ').replace('2',' two ').replace('3',' three ').replace('4',' four ').replace('5',' five ').replace('6',' six ').replace('7','seven').replace('8',' eight ').replace('9',' nine ').replace('0',' zero ')


print(num2text("asdgas阿萨德噶阿萨德刚12314214.343",'en'))
# 按行区分中英
# 按行区分中英
def split_text(text_list):
    result=[]
    for text in text_list:
        text=text.replace('[uv_break]','<en>[uv_break]</en>').replace('[laugh]','<en>[laugh]</en>')
        langlist=LangSegment.getTexts(text)
        length=len(langlist)
        for i,t in enumerate(langlist):
            # 当前是控制符，则插入到前一个           
            
            if len(result)>0 and re.match(r'^[\s\,\.]*?\[(uv_break|laugh)\][\s\,\.]*$',t['text']) is not None:
                result[-1]+=t['text']
            else:
                result.append(num2text(t['text'],t['lang']))
    return result


#print(split_text(["你好啊,各位123456,[uv_break]我的 english 123456, 朋友[laugh],hello my world","[laugh]你是我的enlish朋友呀,[uv_break],难道不是吗？"]))


exit()

import torch
import torch._dynamo
torch._dynamo.config.suppress_errors = True
torch._dynamo.config.cache_size_limit = 64
torch._dynamo.config.suppress_errors = True
torch.set_float32_matmul_precision('high')
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
VERSION='0.6'

def get_executable_path():
    # 这个函数会返回可执行文件所在的目录
    if getattr(sys, 'frozen', False):
        # 如果程序是被“冻结”打包的，使用这个路径
        return Path(sys.executable).parent.as_posix()
    else:
        return Path.cwd().as_posix()

ROOT_DIR=get_executable_path()

MODEL_DIR_PATH=Path(ROOT_DIR+"/models")
MODEL_DIR_PATH.mkdir(parents=True, exist_ok=True)
MODEL_DIR=MODEL_DIR_PATH.as_posix()

WAVS_DIR_PATH=Path(ROOT_DIR+"/static/wavs")
WAVS_DIR_PATH.mkdir(parents=True, exist_ok=True)
WAVS_DIR=WAVS_DIR_PATH.as_posix()

LOGS_DIR_PATH=Path(ROOT_DIR+"/logs")
LOGS_DIR_PATH.mkdir(parents=True, exist_ok=True)
LOGS_DIR=LOGS_DIR_PATH.as_posix()

import soundfile as sf
import ChatTTS
import datetime
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
load_dotenv()


import hashlib,webbrowser
from modelscope import snapshot_download
import numpy as np
import time
# 读取 .env 变量
WEB_ADDRESS = os.getenv('WEB_ADDRESS', '127.0.0.1:9966')

# 默认从 modelscope 下载模型,如果想从huggingface下载模型，请将以下3行注释掉
CHATTTS_DIR = snapshot_download('pzc163/chatTTS',cache_dir=MODEL_DIR)
chat = ChatTTS.Chat()
chat.load_models(source="local",local_path=CHATTTS_DIR,compile=True if os.getenv('compile','true').lower()!='false' else False)

# 如果希望从 huggingface.co下载模型，将以下注释删掉。将上方3行内容注释掉
#os.environ['HF_HUB_CACHE']=MODEL_DIR
#os.environ['HF_ASSETS_CACHE']=MODEL_DIR
#chat = ChatTTS.Chat()
#chat.load_models(compile=True if os.getenv('compile','true').lower()!='false' else False)




text="你好啊朋友们,听说今天是个好日子,难道不是吗？"
prompt='[oral_2][laugh_0][break_0]'
#
torch.manual_seed(3333)
rand_spk = chat.sample_random_speaker()


wavs = chat.infer([text], use_decoder=True,params_infer_code={'spk_emb': rand_spk,'prompt':'[speed_1]'} ,skip_refine_text=True,params_refine_text= {'prompt': prompt})
# 初始化一个空的numpy数组用于之后的合并
combined_wavdata = np.array([], dtype=wavs[0][0].dtype)  # 确保dtype与你的wav数据类型匹配

for wavdata in wavs:
    combined_wavdata = np.concatenate((combined_wavdata, wavdata[0]))
sf.write('test.wav', combined_wavdata, 24000)

