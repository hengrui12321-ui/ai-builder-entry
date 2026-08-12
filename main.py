# 导入 os，用来读取环境变量里的 Nova API Key
import os

# 导入 requests，用来发送 HTTP 网络请求
import requests


# 从环境变量里读取 Nova API Key
api_key = os.getenv("NOVA_API_KEY")


# 如果没有读取到 Key，就直接停止程序，避免带着空 Key 去请求服务器
if not api_key:
    raise ValueError("没有读取到 NOVA_API_KEY")


# 在终端等待用户输入问题
# Python 执行到这里时会暂停，直到你输入内容并按 Enter
user_input = input("你想问 AI 什么？：")


# 设置 Nova AI 的 Chat Completions API 地址
url = "https://us.novaiapi.com/v1/chat/completions"


# 构造 HTTP 请求头
# Authorization 用来告诉 Nova AI：“这是我的 API Key，请验证我的身份”
headers = {
    "Authorization": f"Bearer {api_key}",

    # 告诉服务器：我接下来发送的数据格式是 JSON
    "Content-Type": "application/json"
}


# 构造真正要发送给 AI 的内容
payload = {
    # 指定要调用的模型；这个模型名必须和 Nova AI 模型广场里的 ID 一致
    "model": "gemini-3-pro-preview",

    # messages 表示这次对话的消息列表
    "messages": [
        {
            # role=user 表示这句话是用户说的
            "role": "user",

            # content 是我们真正想问模型的问题
            "content": user_input
        }
    ]
}


# 向 Nova AI 发送 POST 请求
response = requests.post(
    # 请求发送到哪个地址
    url,

    # 带上身份信息
    headers=headers,

    # 把 payload 这个 Python 字典转换成 JSON 后发送给服务器
    json=payload,

    # 最多等待服务器 60 秒，避免程序无限等待
    timeout=60
)


# 打印服务器返回的 HTTP 状态码
print("HTTP 状态码：", response.status_code)


# 把 Nova AI 返回的 JSON 数据转换成 Python 字典
data = response.json()


# 从返回数据的 choices 列表中取第 0 个结果，
# 再进入 message，
# 最后取出 content，也就是真正的模型回答文本
answer = data["choices"][0]["message"]["content"]

# 只打印模型真正回答的内容
print("模型回答：", answer)


