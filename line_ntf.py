import requests
import sys
LINE_URL = "https://notify-api.line.me/api/notify"
LINE_TOKEN = "ziT445xIevP8H8aaI6gMxrluysIVC0EyteYB4OtFYji"
LINE_HEADERS = {
    "Authorization": "Bearer " + LINE_TOKEN
}
params = {
    'message': "{}の接続に失敗しました".format(sys.argv[1])
}
requests.post(LINE_URL, headers=LINE_HEADERS, params=params)