# 导入 requests 库，让 Python 具备向互联网服务器发送 HTTP 请求的能力
import requests


# 保存我们准备访问的 API 地址；这里访问的是 GitHub 上 FastAPI 项目的公开信息接口
url = "https://api.github.com/repos/fastapi/fastapi"


# 向上面的 URL 发送一个 GET 请求，并把服务器返回的结果保存到 response 变量里
response = requests.get(url, timeout=10)


# 打印 HTTP 状态码，用来判断这次请求是否成功
print("HTTP 状态码：", response.status_code)


# 把服务器返回的 JSON 数据转换成 Python 可以操作的数据
data = response.json()

# 从返回的数据中取出项目名称并打印
print("项目名称：", data["name"])




# 从返回的数据中取出项目描述并打印
print("项目描述：", data["description"])

