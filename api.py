# 从 FastAPI 导入 FastAPI 和 HTTPException
# FastAPI 用来创建 API；HTTPException 用来向客户端返回 HTTP 错误
from fastapi import FastAPI, HTTPException

# 从 Pydantic 导入 BaseModel
# BaseModel 用来定义“客户端传给我们的 JSON 应该长什么样”
from pydantic import BaseModel

# 同时导入旧版 Session AI 和新版 Conversation AI
from main import ask_ai, ask_ai_product


# 从产品数据库导入聊天相关函数
# get_conversation：查询某一个具体聊天
# get_conversations：查询某个用户拥有的全部聊天
# create_conversation：为某个用户创建一个新聊天
from product_database import (
    get_conversation,
    get_conversations,
    create_conversation,
    get_messages,
    update_conversation_title,
)


# 创建 FastAPI 应用对象
app = FastAPI()


# 定义 /chat 接口要求客户端提交的数据结构
class ChatRequest(BaseModel):

    # session_id 用来告诉服务器“这次请求属于哪一段聊天”
    session_id: str

    # question 保存用户这一次真正提出的问题
    question: str


# 定义新版产品聊天接口要求的 JSON 数据结构
class ProductChatRequest(BaseModel):

    # conversation_id 对应 product_chat.db 中 conversations 表的主键
    conversation_id: int

    # question 保存用户当前提出的问题
    question: str


# 定义创建新聊天时客户端需要提交的数据结构
class CreateConversationRequest(BaseModel):

    # title 是用户给这个聊天起的名字
    title: str


# 定义修改聊天标题时客户端需要提交的数据结构
class UpdateConversationTitleRequest(BaseModel):

    # title 是准备更新成的新标题
    title: str


# 注册一个 GET /health 接口，用来检查服务器是否正常运行
@app.get("/health")

# 定义处理 /health 请求的函数
def health():

    # 返回一个 Python 字典，FastAPI 会自动转换成 JSON
    return {"status": "ok"}


# 注册一个 GET 接口，用来查询某个用户拥有的全部聊天
@app.get("/users/{user_id}/conversations")

# user_id 来自 URL 路径，例如 /users/1/conversations 中的 1
def list_conversations(user_id: int):

    # user_id 必须是正整数
    if user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="user_id 必须大于 0"
        )

    # 调用数据库层函数，查询这个用户拥有的全部聊天
    conversations = get_conversations(user_id)

    # 把聊天列表作为 JSON 返回给客户端
    return {
        "conversations": conversations
    }


# 注册一个 POST 接口，用来为某个用户创建新的聊天
@app.post("/users/{user_id}/conversations")

# user_id 来自 URL，request 来自客户端提交的 JSON Body
def create_user_conversation(
    user_id: int,
    request: CreateConversationRequest
):

    # 从请求体中取得聊天标题，并去掉前后多余空格
    title = request.title.strip()

    # user_id 必须是正整数
    if user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="user_id 必须大于 0"
        )

    # 聊天标题不能为空
    if not title:
        raise HTTPException(
            status_code=400,
            detail="聊天标题不能为空"
        )

    # 调用数据库层函数，真正创建聊天
    try:
        conversation_id = create_conversation(
            user_id,
            title
        )

    # 如果数据库创建失败，例如 user_id 不存在
    except RuntimeError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # 创建成功后，把新聊天的信息返回给客户端
    return {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "title": title
    }


# 注册一个 PATCH 接口，用来修改已有聊天的标题
@app.patch("/conversations/{conversation_id}")

# conversation_id 来自 URL，request 来自 JSON Body
def update_conversation(
    conversation_id: int,
    request: UpdateConversationTitleRequest
):

    # 去掉标题前后的多余空格
    title = request.title.strip()

    # conversation_id 必须是正整数
    if conversation_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="conversation_id 必须大于 0"
        )

    # 新标题不能为空
    if not title:
        raise HTTPException(
            status_code=400,
            detail="聊天标题不能为空"
        )

    # 先确认这个 conversation 真实存在
    conversation = get_conversation(conversation_id)

    # 如果不存在，就返回 404
    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="conversation 不存在"
        )

    # 调用数据库层，真正修改标题
    updated_rows = update_conversation_title(
        conversation_id,
        title
    )

    # 理论上如果前面已经确认存在，这里应该更新 1 行
    # 如果是 0，说明没有真正修改到任何记录
    if updated_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="conversation 不存在"
        )

    # 修改成功以后，把新的标题返回给客户端
    return {
        "conversation_id": conversation_id,
        "title": title
    }


# 注册一个 GET 接口，用来查询某个聊天中的全部历史消息
@app.get("/conversations/{conversation_id}/messages")

# conversation_id 来自 URL 路径
def list_messages(conversation_id: int):

    # conversation_id 必须是正整数
    if conversation_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="conversation_id 必须大于 0"
        )

    # 先确认这个聊天真实存在
    conversation = get_conversation(conversation_id)

    # 如果找不到聊天，就返回 404
    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="conversation 不存在"
        )

    # 查询这个聊天中的全部历史消息
    messages = get_messages(conversation_id)

    # 把消息列表返回给客户端
    return {
        "conversation_id": conversation_id,
        "messages": messages
    }


# 注册一个 POST /chat 接口，用来接收用户问题
@app.post("/chat")

# request 会接收客户端传来的 JSON，并按照 ChatRequest 进行验证
def chat(request: ChatRequest):

    # 从客户端提交的数据中取出 session_id，并去掉前后多余空格
    session_id = request.session_id.strip()

    # 从 request 中取出 question，并删除前后的多余空格
    question = request.question.strip()

    # 临时打印 session_id，用来确认客户端确实把它传到了服务器
    print("当前 session_id：", session_id)

    # 如果 session_id 为空，就拒绝请求
    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="session_id 不能为空"
        )


    # 如果用户提交的是空问题，就进入这里
    if not question:

        # 向客户端返回 HTTP 400，并告诉它“问题不能为空”
        raise HTTPException(
            status_code=400,
            detail="问题不能为空"
        )

    # 尝试调用昨天写好的 ask_ai() 函数
    try:

        # 把当前会话编号和用户问题一起交给 ask_ai()
        answer = ask_ai(
            # 告诉 AI 层当前属于哪一段会话
            session_id,

            # 把用户当前问题传进去
            question
        )

    # 如果 ask_ai() 抛出 RuntimeError，就进入这里
    except RuntimeError as error:

        # 返回 HTTP 502，表示我们调用上游 AI 服务失败
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )

    # AI 调用成功以后，把答案作为 JSON 返回给客户端
    return {"answer": answer}



# 注册新版 POST /product-chat 接口
@app.post("/product-chat")

# 接收 conversation_id + question，并按照 ProductChatRequest 自动验证类型
def product_chat(request: ProductChatRequest):

    # conversation_id 是新版 conversations 表中的主键
    conversation_id = request.conversation_id

    # 删除用户问题前后的多余空格
    question = request.question.strip()

    # 开发阶段打印 conversation_id，方便确认 HTTP 请求传递是否正确
    print("当前 conversation_id：", conversation_id)

    # conversation_id 必须是正整数
    if conversation_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="conversation_id 必须大于 0"
        )

    # 根据 conversation_id 查询真实的聊天窗口
    conversation = get_conversation(conversation_id)

    # 如果数据库里没有这个 conversation，就直接返回 404
    # 不继续调用 AI，避免浪费上游 API 请求
    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="conversation 不存在"
        )

    # 空问题不发送给 AI
    if not question:
        raise HTTPException(
            status_code=400,
            detail="问题不能为空"
        )

    # 调用已经验证通过的产品版 AI Memory
    try:
        answer = ask_ai_product(
            conversation_id,
            question
        )

    # 目前先沿用旧接口的错误处理方式
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )

    # AI 成功以后，把回答转换成 JSON 返回给客户端
    return {"answer": answer}
