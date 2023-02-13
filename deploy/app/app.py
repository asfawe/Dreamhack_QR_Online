#!/usr/bin/env python3
import base64
import glob
import os
import shutil
from urllib.parse import urlparse, parse_qs

import qrcode
from flask import Flask, abort, render_template, request, session

with open(os.getcwd()+'/deploy/app/flag.txt', 'r') as f:
    FLAG = f.read()

# with open('flag.txt', 'r') as f:
#     FLAG = f.read()

app = Flask(__name__)
app.secret_key = os.urandom(32)

class CacheMiss(Exception):
    pass

def normalize_scheme(scheme):
    return scheme + '.'

def normalize_host(host):
    return host

def normalize_path(path):
    return path.replace('/', '.')

def normalize_params(params):
    return '.' + params

def normalize_query(query):
    q = parse_qs(query.replace('/', '.'))
    qs = ''
    for k, v in q.items():
        qs += k + '=' + v[-1] + '&'
    if len(qs) != 0:
        qs = qs[:-1]
    return qs

def normalize_fragment(fragment):
    return fragment

def normalize(url):
    p = urlparse(url) 
    # https://www.exeam.org/index.html?examParam1=value1&examParam2=value2#welcome
    # 이런 식으로 오는 url을 밑에 처럼 ~~~
    # ParseResult(scheme='https', netloc='www.exeam.org', path='/index.html', params='', query='examParam1=value1&examParam2=value2', fragment='welcome') 

    norm_url = normalize_scheme(p.scheme)      # https
    print("1"+norm_url)
    norm_url += normalize_host(p.netloc)       # www.exeam.org
    print("2"+norm_url)
    norm_url += normalize_path(p.path)         # /index.html
    print("3"+norm_url)
    norm_url += normalize_params(p.params)     # ''
    print(p.params)
    print("4"+norm_url)
    norm_url += normalize_query(p.query)       # examParam1=value1&examParam2=value2
    print("5"+norm_url)
    norm_url += normalize_fragment(p.fragment) # welcome
    print("6"+norm_url)
    return norm_url

def get_cache(norm_url):
    cache = glob.glob(os.getcwd()+'/deploy/app/static/cache/' + norm_url) # 만약 norm_url이 ../../flag.txt라면??
    # glob은 어떤 파일을 가져오는 거다. 정규식을 붙여서 내가 원하는 파일을 가져올 수 있다.
    # 만약 1파일 초과나 미만으로 가져온다면 에러!!
    print(len(cache))
    print(cache)
    if len(cache) != 1:
        print("hahahhahahahahahha"  )
        raise CacheMiss('Cache Miss!')
    print("hello")
    
    return cache[0]

@app.before_request
def init_session():
    if session:
        return
    session['id'] = os.urandom(32).hex()
    os.mkdir('static/users/' + session['id'])

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/qr_generator', methods=['GET', 'POST'])
def qr_generator():
    global dst
    if request.method == 'GET':
        return render_template('qr_generator.html')

    # POST
    url = request.form.get('url')
    if not isinstance(url, str):
        abort(400)

    # 애플리케이션은 "static/cache" 디렉토리에 정규화된 URL에 대한 캐시된 QR 코드가 있는지 확인합니다. 
    # 캐시된 QR 코드가 발견되면 응용 프로그램은 이를 현재 사용자의 "static/users/[session_id]" 디렉토리에 복사합니다.

    # 여기는 우리가 입력한 주소(url)가 static/cache/에 존재할 때 실행되는 곳임.
    try:
        norm_url = normalize(url) # 그냥 QR을 만드는 웹사이트 같음...
        cache = get_cache(norm_url) 
        # 이거가 check하는 곳임.
        # 만약 static/cache/의 내가 입력한 url이 없으면 여기서 오류가 나서 끝난다.

        # Cache Hit

        # .\..\flag*
        
        dst = 'static/users/' + session['id'] + '/qr_code.png'
        print("lalallalalallallalallaallalalalalal")    
        shutil.copyfile(cache, dst)
        print("lalallalalallallalallaallalalalalal")
        # 결국에는 여기서 flag가 찍힌다.    

    # 여기는 우리가 입력한 주소(url)가 static/cache/에 존재하지 않을 때 실행되는 곳임.
    except CacheMiss:
        img = qrcode.make(url) # 우리가 굳이 flag.txt를 읽어는 이유는 바로 sqcode로 만들려고 하는 것 이다.
        src = f'static/cache/{norm_url}' # http:///../../../flag.txt
        img.save(os.getcwd()+'/deploy/app/' + src) # qrcode를 만들기 위해서 위에서 만들었던 주소를 넣어준다.
        dst = 'static/users/' + session['id'] + '/qr_code.png' # 저장공간을 만들어 주는듯 
        shutil.copyfile(src, dst)

        # 관리자의 session id를 알아내야 'static/users/' + session['id'] + '/qr_code.png' 이폴더를 이용해서 flag를 얻을 수 있다.
        # 그러니깐 hash 폴더의 이름을 찾는 방법이 바로 이 방법이다.
        # 그러면 우리는 어떻게 관리자 session id를 찾을까??
        # 방법은 path traversal로 어떤어떤 과정을 거쳐서 해결하면 될것 같다.
        
        # session id를 알아내려고 glob의 있는 정규표현식을 사용해라???
        
        # 어떻게?? 
        
    except:
        abort(500)

    # 여기 부분을 잘 우회해야 내가 원하는 flag를 얻을 수 있음....
    # 여기를 이용하지 않고 flag를 얻을 수 있다!!!
    finally:
        if url.startswith('http://') or url.startswith('https://'):
            with open(dst, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{img_data}">'

        return 'url must starts with "http://" or "https://"    .'

# 읽지도 못하는 데 왜 있는거지....
@app.route('/qr_reader', methods=['GET', 'POST'])
def qr_reader():
    if request.method == 'GET':
        return render_template('qr_reader.html')

    # POST
    return 'in maintenance.. 👷'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
