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

    # 新聊天刚创建时先使用临时标题
    # 等用户成功发送第一条消息以后，再自动更新标题
    title = "新聊天"

    # 记录这是一个刚刚创建的新 Conversation
    is_new_conversation = True

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

    # 这是用户选择的已有聊天，不需要自动修改标题
    is_new_conversation = False


# 显示当前正在使用哪个聊天
print("当前聊天 ID：", conversation_id)

# 拼出当前聊天历史记录的 API 地址
messages_url = (
    f"http://127.0.0.1:8000/conversations/{conversation_id}/messages"
)


# 尝试向后端请求当前聊天的历史消息
try:
    messages_response = requests.get(
        messages_url,
        timeout=30
    )

# 如果请求历史记录时发生连接失败、超时等网络异常
except requests.exceptions.RequestException as error:
    print("无法获取聊天历史：", error)
    raise SystemExit


# 如果历史消息接口没有正常返回 200，就停止程序
if messages_response.status_code != 200:
    print(
        "获取聊天历史失败：",
        messages_response.json()
    )
    raise SystemExit


# 把后端返回的 JSON 转成 Python 字典
messages_data = messages_response.json()


# 从字典中取出真正的历史消息列表
messages = messages_data["messages"]


# 如果当前聊天里已经有历史消息，就显示出来
if messages:

    print("\n========== 历史记录 ==========")

    # 一条一条读取历史消息
    for message in messages:

        # 用户消息显示成“你”
        if message["role"] == "user":
            print("\n你：", message["content"])

        # AI 消息显示成“AI”
        elif message["role"] == "assistant":
            print("\nAI：", message["content"])

    print("\n==============================")


# 如果这个聊天还没有任何历史消息
else:
    print("\n这是一个新聊天，目前还没有历史消息。")


# 告诉用户如何结束当前聊天
print("输入 exit 可以退出聊天。")


# True 永远成立，所以这里会持续进入聊天循环
while True:

    # 等待用户输入当前这一轮的问题，并去掉前后空格
    user_input = input("\n你：").strip()

    # 如果用户输入 exit，就结束 while 循环
    if user_input.lower() == "exit":
        print("已退出当前聊天。")
        break

    # 如果用户什么都没输入，就不要调用后端
    if not user_input:
        print("问题不能为空，请重新输入。")
        continue


    # 构造这一轮要发送给 /product-chat 的 JSON 数据
    payload = {
        "conversation_id": conversation_id,
        "question": user_input
    }


    # 尝试向自己的 FastAPI 后端发送聊天请求
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=90
        )

    # 如果发生连接失败、超时等网络错误
    except requests.exceptions.RequestException as error:
        print("无法连接到 AI 后端：", error)

        # 这次请求失败，但不结束整个聊天
        # 直接回到 while 顶部，让用户可以继续输入
        continue


    # 如果后端返回的状态码不是 200
    if response.status_code != 200:

        print(
            "API 请求失败：",
            response.json()
        )

        # 这一轮失败，但聊天程序继续运行
        continue


    # 把后端成功响应的 JSON 转成 Python 字典
    data = response.json()

    # 从 JSON 中取出 AI 回答
    answer = data["answer"]

    # 显示 AI 回答
    print("AI：", answer)


    # 如果这是刚刚创建的新聊天，就根据第一条用户消息自动生成标题
    if is_new_conversation:

        # V1 先直接取用户第一句话的前 20 个字符作为标题
        auto_title = user_input[:20]

        # 如果用户的问题超过 20 个字符，就在后面加省略号
        if len(user_input) > 20:
            auto_title += "..."

        # 拼出修改当前聊天标题的 PATCH API 地址
        update_title_url = (
            f"http://127.0.0.1:8000/conversations/{conversation_id}"
        )

        # 尝试请求 PATCH 接口修改标题
        try:
            title_response = requests.patch(
                update_title_url,
                json={"title": auto_title},
                timeout=30
            )

        # 如果连接失败或超时，只提示错误，不影响继续聊天
        except requests.exceptions.RequestException as error:
            print("自动更新聊天标题失败：", error)

        else:

            # PATCH 成功
            if title_response.status_code == 200:
                print("聊天标题已自动更新为：", auto_title)

                # 标题已经生成过一次
                # 后面的聊天不要继续修改标题
                is_new_conversation = False

            # PATCH 接口返回了错误状态码
            else:
                print(
                    "自动更新聊天标题失败：",
                    title_response.json()
                )
