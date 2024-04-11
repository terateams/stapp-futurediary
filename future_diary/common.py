import json
import os
import jwt
import requests



def check_apptoken_from_apikey(apikey: str):
    if not apikey:
        return None
    apisecret = os.environ.get('APP_SECRET')
    if apikey:
        try:
            payload = jwt.decode(apikey, apisecret, algorithms=['HS256'])
            uid = payload.get('uid')
            if uid :
                return uid
        except Exception as e:
            return None
    return None

def get_global_datadir(subpath: str = None):
    """
    获取全局数据目录。

    Args:
        subpath (str, optional): 子路径。默认为None。

    Returns:
        str: 数据目录路径。
    """
    datadir = os.environ.get("DATA_DIR", "/tmp/teamsgpt")
    if subpath:
        datadir = os.path.join(datadir, subpath)
    if not os.path.exists(datadir):
        os.makedirs(datadir)
    return datadir


def openai_text_generate(sysmsg: str, prompt: str, apikey: str):
    url = os.getenv("TEAMSGPT_APISITE", "https://api.teamsgpt.net") + "/api/generate"
    # Prepare headers and data
    headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {apikey}"}
    data = json.dumps({
        "sysmsg": sysmsg,
        "prompt": prompt,
        "temperature": 0.7,  # Adjust this as needed
    })
    
    with requests.post(url, data=data, headers=headers, stream=True) as response:
        if response.status_code == 200:
            for line in response.iter_lines():
                decoded_line = line.decode('utf-8')               
                if decoded_line.startswith('data:'):
                    try:
                        json_str = decoded_line[len('data: '):]
                        if json_str:  
                            yield json.loads(json_str)
                        else:
                            pass
                    except json.JSONDecodeError as e:
                        print(f"JSON decoding failed: {e}")
                elif "data: [DONE]" in decoded_line:
                    break
        else:
            raise Exception(f"Error: {response.status_code} {response.reason}")

def write_stream_text(placeholder, response):
    """写入流式响应。"""
    full_response = ""
    for tobj in response:
        text = tobj.get("content")
        if text is not None:
            full_response += text
            placeholder.markdown(full_response)
        placeholder.markdown(full_response)
    return full_response