# 导入 os，用来读取操作系统中的环境变量
import os

# 从 python-dotenv 中导入 load_dotenv，用来加载项目里的 .env 文件
from dotenv import load_dotenv

# 导入 requests，用来发送 HTTP 网络请求
import requests


# 读取当前项目目录中的 .env 文件，
# 并把里面的配置加载到 Python 程序运行时的环境变量中
load_dotenv()


# 从刚刚加载好的环境变量里读取 Nova API Key
api_key = os.getenv("NOVA_API_KEY")


# 从环境变量里读取 Nova API Key
api_key = os.getenv("NOVA_API_KEY")


# 如果没有读取到 Key，就直接停止程序，避免带着空 Key 去请求服务器
if not api_key:
    raise ValueError("没有读取到 NOVA_API_KEY")


# 在终端等待用户输入问题
# .strip() 会删除输入内容前后的空格和换行
user_input = input("你想问 AI 什么？：").strip()


# 如果 user_input 是空字符串，就提示用户不能提交空问题
if not user_input:
    print("问题不能为空，请输入内容后再试。")

    # 立即结束当前 Python 程序，避免继续向 AI API 发送无效请求
    raise SystemExit


# 设置真正的 Nova AI 聊天接口地址
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


# 尝试执行网络请求，因为连接失败、断网、超时等情况都可能让这里报错
try:

    # 向 Nova AI 的服务器发送 POST 请求
    response = requests.post(
        # 请求发送到哪个地址
        url,

        # 带上包含 API Key 的请求头
        headers=headers,

        # 把 payload 这个 Python 字典自动转换成 JSON 并发送
        json=payload,

        # 最多等待服务器 60 秒，防止程序无限卡住
        timeout=60
    )

# 如果 requests 在网络请求阶段抛出异常，就进入这里处理
except requests.exceptions.RequestException as error:

    # 把真正的网络错误打印出来，方便用户知道发生了什么
    print("网络请求失败：", error)

    # 网络请求都没有成功完成，所以直接结束程序
    raise SystemExit


# 打印 HTTP 状态码，帮助判断这次请求是否成功
print("HTTP 状态码：", response.status_code)


# 判断 HTTP 状态码是否不是 200
if response.status_code != 200:

    # 如果请求失败，就把服务器真正返回的错误内容打印出来
    print("API 请求失败：", response.text)

    # 请求已经失败，不应该继续读取 choices，因此直接结束程序
    raise SystemExit


# 只有状态码是 200 时，才把服务器返回的 JSON 转换成 Python 字典
data = response.json()


# 从成功响应里的 choices 第一个结果中取出模型回答
answer = data["choices"][0]["message"]["content"]


# 把真正的模型回答打印出来
print("AI：", answer)


# 只打印模型真正回答的内容
print("模型回答：", answer)


