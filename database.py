# 导入 Python 自带的 sqlite3 模块，用来操作 SQLite 数据库
import sqlite3


# 指定 SQLite 数据库文件的名字
DB_FILE = "chat.db"


# 定义数据库初始化函数，负责创建数据库需要的表
def init_db():

    # 连接 SQLite 数据库；如果 chat.db 不存在，SQLite 会自动创建它
    connection = sqlite3.connect(DB_FILE)

    # 创建游标 cursor，用来向数据库发送 SQL 指令
    cursor = connection.cursor()

    # 执行 SQL，创建保存聊天消息的 messages 表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # 正式提交刚才对数据库结构所做的修改
    connection.commit()

    # 操作结束后关闭数据库连接
    connection.close()


# 定义一个函数，负责向 messages 表插入一条新的聊天消息
def add_message(session_id, role, content):

    # 连接 chat.db 数据库
    connection = sqlite3.connect(DB_FILE)

    # 创建游标，用来向 SQLite 发送 SQL 指令
    cursor = connection.cursor()

    # 执行 INSERT SQL，把一条消息写进 messages 表
    cursor.execute(
        """
        INSERT INTO messages (session_id, role, content)
        VALUES (?, ?, ?)
        """,

        # 按顺序把 Python 变量填进上面三个 ? 占位符
        (session_id, role, content)
    )

    # 提交这次 INSERT，让新增的数据真正保存到数据库
    connection.commit()

    # 操作结束后关闭数据库连接
    connection.close()


# 定义一个函数，负责查询某个 session_id 对应的全部聊天消息
def get_messages(session_id):

    # 连接 chat.db 数据库
    connection = sqlite3.connect(DB_FILE)

    # 创建游标，用来向 SQLite 发送查询指令
    cursor = connection.cursor()

    # 从 messages 表中查询属于指定 session_id 的全部消息
    cursor.execute(
        """
        SELECT id, session_id, role, content, created_at
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,

        # 把要查询的 session_id 填进 SQL 中的 ? 占位符
        (session_id,)
    )

    # 把查询返回的所有记录取出来
    rows = cursor.fetchall()

    # 查询完成后关闭数据库连接
    connection.close()

    # 把查询结果返回给调用这个函数的地方
    return rows


# 👇 就加在这里
# 定义一个函数，把数据库中的聊天记录转换成 AI API 需要的消息格式
def get_messages_for_ai(session_id):

    # 先查询这个会话在数据库里的全部消息
    rows = get_messages(session_id)

    # 创建一个空列表，用来保存转换后的 AI 消息
    messages = []

    # 逐条处理数据库查询出来的记录
    for row in rows:

        # 从数据库记录中取出 role
        role = row[2]

        # 从数据库记录中取出 content
        content = row[3]

        # 把数据库记录转换成 Gemini messages 需要的字典格式
        messages.append(
            {
                # 保存消息角色，例如 user 或 assistant
                "role": role,

                # 保存真正的消息内容
                "content": content
            }
        )

    # 把转换完成的完整消息列表返回出去
    return messages


# 只有直接运行 database.py 时，才执行下面的测试代码
if __name__ == "__main__":

    # 确保数据库和 messages 表已经存在
    init_db()

    # 查询 chat-001 的聊天记录，并转换成 AI API 需要的 messages 格式
    messages = get_messages_for_ai("chat-001")

    # 把转换后的结果打印出来，方便我们检查格式
    print(messages)



