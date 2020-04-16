from function import get_config
import requests
import base64


if __name__ == '__main__':
    url = get_config('akc_package_url')[0] + '/verifCode'
    response = requests.get(url=url)
    res = response.content
    img = base64.b64decode(res)
    file = open('./static/verif_code.jpeg', 'wb')
    file.write(img)
    file.close()
