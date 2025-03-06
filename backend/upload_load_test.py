import requests

# API 端点
url = "http://127.0.0.1:8000/api/user/avatar/upload/"

# 认证令牌
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwNjgwMTkwLCJpYXQiOjE3MzA2NzgzOTAsImp0aSI6IjljNjhhNGY4MmVjNDQ5YzBiMTUwOTY5NjdkMTEzOTdkIiwidXNlcl9pZCI6MjJ9.Qhj9HT_fF9rriMxOZpieYkwWPVKhIbErzGjInmMmBBk",  # 替换为您的 JWT 令牌
}

# 文件上传
files = {
    "avatar": open("C:/Users/wwwph/Pictures/皮帅/微信图片_20221115114304.jpg", "rb"),  # 替换为本地的图片路径
}

response = requests.post(url, headers=headers, files=files)

# 打印响应
print(response.status_code)
print(response.json())
