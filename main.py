# 导入 os，用来读取操作系统中的环境变量
import os

# 从 python-dotenv 中导入 load_dotenv，用来读取项目里的 .env 文件
from dotenv import load_dotenv

# 导入 requests，用来发送 HTTP 网络请求
import requests


# 读取当前项目目录里的 .env 文件，并把里面的配置加载到程序环境中
load_dotenv()


# 从环境变量中读取 Nova API Key
api_key = os.getenv("NOVA_API_KEY")


# 如果没有读取到 API Key，就立即报错，避免继续发送无效请求
if not api_key:
    raise ValueError("没有读取到 NOVA_API_KEY")


# 定义一个负责“向 AI 提问”的函数
# question 是调用这个函数时传进来的用户问题
def ask_ai(question):

    # 设置 Nova AI 的聊天接口地址
    url = "https://us.novaiapi.com/v1/chat/completions"

    # 构造 HTTP 请求头
    headers = {
        # 把 API Key 放进 Authorization，用来向 Nova 证明调用者身份
        "Authorization": f"Bearer {api_key}",

        # 告诉服务器，请求正文的数据格式是 JSON
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

                # 把传进 ask_ai() 的 question 放进请求内容
                "content": question
            }
        ]
    }

    # 尝试发送网络请求，因为断网、超时、连接失败等情况都有可能发生
    try:

        # 向 Nova AI 发送 POST 请求
        response = requests.post(
            # 请求发送到哪个 API 地址
            url,

            # 带上身份认证和数据格式信息
            headers=headers,

            # 把 payload 转成 JSON 请求正文发送出去
            json=payload,

            # 最多等待 60 秒，避免网络异常时无限等待
            timeout=60
        )

    # 如果 requests 在网络请求阶段出现异常，就进入这里
    except requests.exceptions.RequestException as error:

        # 把网络错误向上一层抛出，而不是直接关闭整个程序
        raise RuntimeError(f"网络请求失败：{error}")

    # 打印 HTTP 状态码，方便开发阶段观察请求是否成功
    print("HTTP 状态码：", response.status_code)

    # 如果服务器返回的状态码不是 200，说明 AI API 没有正常完成请求
    if response.status_code != 200:

        # 把 API 错误向上一层抛出，让调用 ask_ai() 的代码决定如何处理
        raise RuntimeError(
            f"AI API 请求失败，状态码：{response.status_code}，错误：{response.text}"
        )

    # 把服务器返回的 JSON 转换成 Python 可以操作的数据
    data = response.json()

    # 从返回数据中逐层找到模型真正回答的文字
    answer = data["choices"][0]["message"]["content"]

    # 把模型回答从 ask_ai() 函数内部返回给调用它的地方
    return answer


# 定义程序的主函数
# main() 负责“获取用户输入 → 调用 AI → 显示结果”
def main():

    # 等待用户输入问题，并删除输入前后的多余空格
    user_input = input("你想问 AI 什么？：").strip()

    # 如果用户没有输入有效内容，就不调用 AI
    if not user_input:

        # 给用户显示提示信息
        print("问题不能为空，请输入内容后再试。")

        # 结束当前 main() 函数
        return

    # 尝试调用 ask_ai()，因为底层 AI 服务可能出现错误
    try:

        # 把用户的问题传给 ask_ai()，并接收返回的模型回答
        answer = ask_ai(user_input)

    # 如果 ask_ai() 抛出了 RuntimeError，就进入这里
    except RuntimeError as error:

        # 把错误信息显示给终端用户
        print("AI 调用失败：", error)

        # 出错以后结束 main()，不继续执行下面的正常输出
        return

    # 只有 AI 调用成功以后，才把回答显示给用户
    print("AI：", answer)


# 判断这个文件是不是被直接运行的主程序
if __name__ == "__main__":

    # 如果是直接运行，就正式启动 main() 主流程
    main()

