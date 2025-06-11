import requests
res = requests.get("https://www.tiktok.com",
                   headers={"User-Agent": "Mozilla/5.0"})
print(res.status_code)
