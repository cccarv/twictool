import requests

r = requests.get("https://theweekinchess.com/twic")
print(r.status_code)
