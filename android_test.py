import os
from numpy.core.records import array
from numpy.lib.function_base import average
from PIL import Image
import sys
import json
import base64
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.parse import quote_plus
import ssl

IS_PY3 = sys.version_info.major == 3
os.chdir('C://Program Files/Android/tools')

# 需要有线连接手机，想无线连接需要自己改
# os.system('adb shell screencap /sdcard/screen.png')
# os.system('adb pull /sdcard/screen.png D:\\test')

# 百度的ocr技术，需要自己免费注册获取密钥填在下面
ssl._create_default_https_context = ssl._create_unverified_context
API_KEY = ''
SECRET_KEY = ''
OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()

def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)

def say_color(cor_list):
    col_R = []
    col_G = []
    col_B = []
    for i in cor_list:
        col_R.append(i[0])
        col_G.append(i[1])
        col_B.append(i[2])
    if min(col_R)<130: return 'Blue'
    elif max(col_R)>230 and average(col_G) < average(col_B): return 'Red'
    elif min(col_B)<70: return 'Coffee'
    else: return 'Skin'

# 读取图像，去掉上下多余部分
im = Image.open("D:\\test\screen.png")
img = im.crop((220, 655, 220+5*127, 655+7*127))
img.save("D:\\test\screen_1.png")
file_content = read_file("D:\\test\screen_1.png")

token = fetch_token()
image_url = OCR_URL + "?access_token=" + token
text = []

# 确定格子颜色
s_cor = []
s_text = []
for j in range(7):
    box = []
    cor = []
    text = []
    for i in range(5):
        box.append((230+i*127, 700+j*127, 340+i*127, 770+j*127))
        tem_img = im.crop(box[i])
        cor_list = [tem_img.getpixel((1,49)),tem_img.getpixel((89,49))]
        cor.append(say_color(cor_list))
        img2 = array(img)

    s_cor.append(cor)

result = request(image_url, urlencode({'image': base64.b64encode(file_content)}))
result_json = json.loads(result)

for words_result in result_json["words_result"]:
    text.append(words_result["words"])
text.insert(2,'0')
text.insert(32,'0')

s_text = []
temp = []
for i in range(len(text)):
    temp.append(int(text[i]))
    if (i+1)%5 == 0: 
        s_text.append(temp)
        temp = []
    
# 计数
s = l = r = c = 0
for i in range(7):
    for j in range(5):
        if s_text[i][j] == '': continue
        elif s_cor[i][j] == 'Blue': l += int(s_text[i][j])
        elif s_cor[i][j] == 'Red': r += int(s_text[i][j])
        elif s_cor[i][j] == 'Skin': s += int(s_text[i][j])
        elif s_cor[i][j] == 'Coffee': c += int(s_text[i][j])

print(s_cor,s_text)  
print('skin={},blue={},red={},coffee={}'.format(s,l,r,c))
