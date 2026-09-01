# 从 FastAPI 导入 FastAPI 和 HTTPException
# FastAPI 用来创建 API；HTTPException 用来向客户端返回 HTTP 错误
from fastapi import FastAPI, HTTPException

# 从 Pydantic 导入 BaseModel
# BaseModel 用来定义“客户端传给我们的 JSON 应该长什么样”
from pydantic import BaseModel

# 同时导入旧版 Session AI 和新版 Conversation AI
from main import ask_ai, ask_ai_product

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


# 注册一个 GET /health 接口，用来检查服务器是否正常运行
@app.get("/health")

# 定义处理 /health 请求的函数
def health():

    # 返回一个 Python 字典，FastAPI 会自动转换成 JSON
    return {"status": "ok"}


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
