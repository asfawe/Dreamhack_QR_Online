from urllib.parse import urlparse, parse_qs


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
    q = parse_qs(query)
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
    norm_url += normalize_host(p.netloc)       # www.exeam.org
    norm_url += normalize_path(p.path)         # /index.html
    norm_url += normalize_params(p.params)     # ''
    norm_url += normalize_query(p.query)       # examParam1=value1&examParam2=value2
    norm_url += normalize_fragment(p.fragment) # welcome
    return norm_url

print(normalize("../../flag.txt"))