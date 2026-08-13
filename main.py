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


# 定义一个负责“向 AI 提问”的函数
# question 表示调用这个函数时传进来的问题
def ask_ai(question):

    # 设置 Nova AI 的聊天接口地址
    url = "https://us.novaiapi.com/v1/chat/completions"

    # 构造 HTTP 请求头
    # Authorization 用来告诉 Nova AI：“这是我的 API Key，请验证我的身份”
    headers = {
        # 把之前读取到的 api_key 放进 Authorization 请求头
        "Authorization": f"Bearer {api_key}",

        # 告诉服务器：接下来发送的数据格式是 JSON
        "Content-Type": "application/json"
    }

    # 构造真正发送给 AI 的请求内容
    payload = {
        # 指定要调用的模型
        "model": "gemini-3-pro-preview",

        # messages 是发送给聊天模型的消息列表
        "messages": [
            {
                # 表示这条消息来自用户
                "role": "user",

                # 使用 ask_ai 函数收到的 question
                "content": question
            }
        ]
    }



    # 尝试执行网络请求，因为这里可能出现断网、超时、连接失败等异常
    try:

        # 向 Nova AI 发送 POST 请求
        response = requests.post(
            # 请求发送到哪个地址
            url,

            # 带上身份认证和数据格式信息
            headers=headers,

            # 把 payload 转换成 JSON 后发送
            json=payload,

            # 最多等待 60 秒
            timeout=60
        )

    # 捕获 requests 网络请求相关的异常
    except requests.exceptions.RequestException as error:

        # 打印真正发生的网络错误
        print("网络请求失败：", error)

        # 网络请求没有成功，因此直接结束程序
        raise SystemExit

    # 打印 HTTP 状态码，方便判断服务器有没有正常处理请求
    print("HTTP 状态码：", response.status_code)

    # 如果服务器返回的状态码不是 200，就不要继续解析正常 AI 回答
    if response.status_code != 200:

        # 打印服务器真正返回的错误内容
        print("API 请求失败：", response.text)

        # 请求失败，因此结束程序
        raise SystemExit

    # 把服务器返回的 JSON 转换成 Python 数据
    data = response.json()

    # 从返回数据里找到真正的模型回答
    answer = data["choices"][0]["message"]["content"]

    # 把模型回答返回给调用 ask_ai() 的地方
    return answer


# 定义程序的主函数
# main() 负责组织“用户输入 → 调用 AI → 显示结果”这一整条主流程
def main():

    # 等待用户在终端输入问题，并去掉前后的多余空格
    user_input = input("你想问 AI 什么？：").strip()

    # 如果用户没有输入有效内容，就进入这个判断
    if not user_input:

        # 告诉用户问题不能为空
        print("问题不能为空，请输入内容后再试。")

        # 直接结束 main() 函数，不继续调用 AI
        return

    # 把用户的问题交给 ask_ai()，并接收函数返回的模型回答
    answer = ask_ai(user_input)

    # 把模型回答显示给用户
    print("AI：", answer)


# 只有当这个文件被直接运行时，才正式启动 main() 主函数
if __name__ == "__main__":

    # 调用 main()，开始执行程序的主流程
    main()


