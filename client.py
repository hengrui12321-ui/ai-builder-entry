# 导入 requests，让这个 Python 程序能够发送 HTTP 请求
import requests


# 导入 uuid 模块，用来自动生成唯一的会话编号
import uuid


# 设置我们自己刚刚创建的 /chat API 地址
url = "http://127.0.0.1:8000/chat"


# 自动生成一个唯一聊天会话编号
session_id = str(uuid.uuid4())


# 显示当前聊天使用的 session_id，方便观察测试
print("当前会话编号：", session_id)

    
# 在终端等待用户输入问题，并去掉问题前后的多余空格
user_input = input("请输入你想问 AI 的问题：").strip()


# 如果用户没有输入有效内容，就不要继续发送 API 请求
if not user_input:

    # 提示用户问题不能为空
    print("问题不能为空，请重新运行后输入问题。")

    # 直接结束当前客户端程序
    raise SystemExit


# 构造准备发送给自己 FastAPI 的 JSON 数据
payload = {

    # 使用程序自动生成的唯一会话编号
    "session_id": session_id,

    # question 就是 /chat 接口要求客户端提供的字段
    "question": user_input
}


# 尝试调用我们自己的 FastAPI，因为服务器可能没有启动、断开或超时
try:

    # 向我们自己的 FastAPI /chat 接口发送 POST 请求
    response = requests.post(
        # 请求发送到我们自己的 /chat 地址
        url,

        # 把 payload 作为 JSON Request Body 发送
        json=payload,

        # 最多等待 90 秒，避免请求无限等待
        timeout=90
    )

# 如果请求过程中发生连接失败、超时等网络异常，就进入这里
except requests.exceptions.RequestException as error:

    # 给客户端用户显示一个更容易理解的错误提示
    print("无法连接到 AI 后端：", error)

    # 后端都没有连接成功，所以直接结束客户端程序
    raise SystemExit


# 打印我们自己的 FastAPI 返回的 HTTP 状态码
print("我的 API 状态码：", response.status_code)


# 把 FastAPI 返回的 JSON 转换成 Python 数据
data = response.json()


# 如果 HTTP 状态码不是 200，说明这次请求没有正常成功
if response.status_code != 200:

    # 显示 FastAPI 返回的错误信息
    print("API 请求失败：", data)

    # 错误响应里通常没有 answer，所以到这里直接结束程序
    raise SystemExit


# 只有状态码为 200 时，才读取成功响应中的 answer 字段
answer = data["answer"]


# 把最终 AI 回答显示给用户
print("AI：", answer)

