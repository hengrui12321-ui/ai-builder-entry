# 导入 requests，用来发送 HTTP 请求
import requests


# 设置新版产品聊天 API 地址
url = "http://127.0.0.1:8000/product-chat"


# 当前先固定使用数据库中的用户 1
# 后面做登录系统时，再把这里替换成真实登录用户
user_id = 1


# 拼出“查询当前用户全部聊天”的 API 地址
conversations_url = (
    f"http://127.0.0.1:8000/users/{user_id}/conversations"
)


# 向后端请求当前用户已有的聊天列表
try:
    conversations_response = requests.get(
        conversations_url,
        timeout=30
    )

except requests.exceptions.RequestException as error:
    print("无法获取聊天列表：", error)
    raise SystemExit


# 如果聊天列表接口返回的不是 200，就停止程序
if conversations_response.status_code != 200:

    print(
        "获取聊天列表失败：",
        conversations_response.json()
    )

    raise SystemExit


# 把后端返回的 JSON 转成 Python 字典
conversations_data = conversations_response.json()


# 从字典中取出真正的聊天列表
conversations = conversations_data["conversations"]


# 显示当前用户已有的聊天
print("\n已有聊天：")

for conversation in conversations:

    print(
        f"{conversation['id']}. "
        f"{conversation['title']}"
    )


# 0 专门表示“创建一个新的聊天”
print("0. 新建聊天")


# 读取用户的选择
choice = input("\n请选择聊天编号：").strip()


# 只有纯数字才能继续
if not choice.isdigit():

    print("请输入有效的数字编号。")
    raise SystemExit


# 已经确认输入是数字，现在把字符串转换成真正的整数
choice = int(choice)


# 把当前用户已有聊天的 id 收集起来
conversation_ids = [
    conversation["id"]
    for conversation in conversations
]


# 如果用户输入 0，就创建一个新的聊天
if choice == 0:

    # 让用户输入新聊天标题
    title = input("请输入新聊天标题：").strip()

    # 标题不能为空
    if not title:
        print("聊天标题不能为空。")
        raise SystemExit

    # 拼出创建聊天的 API 地址
    create_url = (
        f"http://127.0.0.1:8000/users/{user_id}/conversations"
    )

    # 尝试向后端发送创建聊天请求
    try:
        create_response = requests.post(
            create_url,
            json={"title": title},
            timeout=30
        )

    except requests.exceptions.RequestException as error:
        print("创建聊天失败：", error)
        raise SystemExit

    # 如果后端没有成功创建聊天，就停止程序
    if create_response.status_code != 200:
        print(
            "创建聊天失败：",
            create_response.json()
        )
        raise SystemExit

    # 解析后端返回的新聊天信息
    create_data = create_response.json()

    # 取出数据库刚刚生成的新 conversation_id
    conversation_id = create_data["conversation_id"]

    print("新聊天创建成功，ID：", conversation_id)


# 如果不是 0，就说明用户想进入已有聊天
else:

    # 如果这个编号不属于当前用户已有聊天，就拒绝继续
    if choice not in conversation_ids:
        print("聊天编号不存在，请重新运行后选择。")
        raise SystemExit

    # 编号合法，正式进入这个聊天
    conversation_id = choice


# 显示当前正在使用哪个聊天
print("当前聊天 ID：", conversation_id)


# 在终端等待用户输入问题，并去掉前后的多余空格
user_input = input("请输入你想问 AI 的问题：").strip()


# 如果用户没有输入有效内容，就不要继续发送 API 请求
if not user_input:

    # 提示用户问题不能为空
    print("问题不能为空，请重新运行后输入问题。")

    # 直接结束当前客户端程序
    raise SystemExit


# 构造准备发送给新版 FastAPI 的 JSON 数据
payload = {

    # 告诉后端：这条消息属于哪个 Conversation
    "conversation_id": conversation_id,

    # 用户当前输入的问题
    "question": user_input
}


# 尝试调用我们自己的 FastAPI
# 因为服务器可能没有启动、断开或超时
try:

    # 向新版 /product-chat 接口发送 POST 请求
    response = requests.post(

        # 请求发送到新版产品聊天地址
        url,

        # 把 payload 作为 JSON Request Body 发送
        json=payload,

        # 最多等待 90 秒，避免请求无限等待
        timeout=90
    )

# 如果请求过程中发生连接失败、超时等网络异常，就进入这里
except requests.exceptions.RequestException as error:

    # 给客户端用户显示更容易理解的错误提示
    print("无法连接到 AI 后端：", error)

    # 后端没有连接成功，所以直接结束程序
    raise SystemExit


# 打印 FastAPI 返回的 HTTP 状态码
print("我的 API 状态码：", response.status_code)


# 把 FastAPI 返回的 JSON 转换成 Python 数据
data = response.json()


# 如果 HTTP 状态码不是 200，说明这次请求没有正常成功
if response.status_code != 200:

    # 显示 FastAPI 返回的错误信息
    print("API 请求失败：", data)

    # 错误响应里通常没有 answer，所以直接结束程序
    raise SystemExit


# 只有状态码为 200 时，才读取成功响应中的 answer 字段
answer = data["answer"]


# 把最终 AI 回答显示给用户
print("AI：", answer)


