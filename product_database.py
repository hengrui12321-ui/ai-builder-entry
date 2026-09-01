# 导入 Python 自带的 sqlite3，用来操作 SQLite 数据库
import sqlite3


# 指定新版产品数据库文件
DB_FILE = "product_chat.db"

# 创建并返回一个已经正确配置好的数据库连接
def get_connection():

    # 连接新版产品数据库
    connection = sqlite3.connect(DB_FILE)

    # 为当前这个数据库连接开启外键约束
    connection.execute("PRAGMA foreign_keys = ON")

    # 把配置好的连接交给调用者使用
    return connection


# 创建一个新用户，并返回数据库为这个用户生成的 id
def create_user(username):

    # 通过统一入口获取已经开启外键约束的数据库连接
    connection = get_connection()

    # 创建游标，用来执行 INSERT SQL
    cursor = connection.cursor()

    # 尝试把用户写入数据库
    try:

        # 把用户名写入 users 表
        # 使用 ? 占位符，而不是自己拼接 SQL 字符串
        cursor.execute(
            """
            INSERT INTO users (username)
            VALUES (?)
            """,
            (username,)
        )

        # 保存这次 INSERT
        connection.commit()

        # 获取 SQLite 刚刚自动生成的用户 id
        user_id = cursor.lastrowid

        # 把新用户的 id 返回给调用者
        return user_id

    # 如果违反数据库完整性约束
    except sqlite3.IntegrityError as error:

        # 把数据库底层错误转换成应用层错误
        raise RuntimeError(
            f"创建用户失败，数据库完整性校验未通过：{error}"
        )

    # 无论成功还是失败，都执行资源清理
    finally:

        # 始终关闭数据库连接
        connection.close()


# 创建一个新的聊天窗口，并返回数据库生成的 conversation_id
def create_conversation(user_id, title):

    # 通过统一入口获得已经开启外键约束的数据库连接
    connection = get_connection()

    # 创建游标，用来执行 SQL
    cursor = connection.cursor()

    # 尝试执行真正的数据库写入
    try:

        # 把聊天写进 conversations 表
        # ? 是 SQL 参数占位符，实际值通过第二个参数传入
        cursor.execute(
            """
            INSERT INTO conversations (user_id, title)
            VALUES (?, ?)
            """,
            (user_id, title)
        )

        # INSERT 成功以后，保存这次数据库修改
        connection.commit()

        # 获取 SQLite 自动生成的 conversation id
        conversation_id = cursor.lastrowid

        # 把新聊天 id 返回给调用者
        return conversation_id

    # 如果违反数据库完整性规则，例如 user_id 指向不存在的用户
    except sqlite3.IntegrityError as error:

        # 把底层 SQLite 错误转换成更容易让上层理解的运行时错误
        raise RuntimeError(
            f"创建聊天失败，数据库完整性校验未通过：{error}"
        )

    # 无论上面的 INSERT 成功还是失败，这一块都会执行
    finally:

        # 始终关闭数据库连接，避免异常发生时连接没有被释放
        connection.close()

# 向某一个聊天窗口中保存一条消息，并返回新消息的 id
def add_message(conversation_id, role, content):

    # 通过统一入口获得已经开启外键约束的数据库连接
    connection = get_connection()

    # 创建游标，用来执行 INSERT
    cursor = connection.cursor()

    # 尝试把消息写入数据库
    try:

        # 把消息所属聊天、角色和正文写入 messages 表
        cursor.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content)
        )

        # 保存这次数据库修改
        connection.commit()

        # 获取 SQLite 自动生成的新消息 id
        message_id = cursor.lastrowid

        # 把新消息 id 返回给调用者
        return message_id

    # 如果 conversation_id 不存在等情况违反数据库完整性约束
    except sqlite3.IntegrityError as error:

        # 把 SQLite 底层错误转换成应用层可以理解的 RuntimeError
        raise RuntimeError(
            f"保存消息失败，数据库完整性校验未通过：{error}"
        )

    # 无论成功还是失败，都确保数据库连接被关闭
    finally:

        # 释放数据库连接
        connection.close()


# 查询某一个聊天窗口中的全部消息
def get_messages(conversation_id):

    # 通过统一入口获得数据库连接
    connection = get_connection()

    # 创建游标，用来执行 SELECT
    cursor = connection.cursor()

    # 查询属于指定 conversation_id 的全部消息
    # ORDER BY id ASC 表示按照消息写入顺序，从早到晚排列
    cursor.execute(
        """
        SELECT id, conversation_id, role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        """,
        (conversation_id,)
    )

    # 把数据库查询出的全部行取回 Python
    rows = cursor.fetchall()

    # 创建一个列表，用来保存转换后的消息数据
    messages = []

    # 逐条处理数据库返回的 tuple
    for row in rows:

        # 把一行数据库记录转换成字段含义明确的 dict
        message = {
            "id": row[0],
            "conversation_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": row[4]
        }

        # 把转换后的消息加入结果列表
        messages.append(message)

    # 查询完成后关闭数据库连接
    connection.close()

    # 把完整聊天历史返回给调用者
    return messages


# 把某个聊天的数据库消息转换成 AI API 需要的消息格式
def get_messages_for_ai(conversation_id):

    # 先复用 get_messages()，取得这个聊天的完整历史记录
    messages = get_messages(conversation_id)

    # 创建一个新列表，专门保存发送给 AI 的上下文
    ai_messages = []

    # 逐条处理数据库返回的消息
    for message in messages:

        # AI 只需要 role 和 content，不需要数据库 id、时间等字段
        ai_message = {
            "role": message["role"],
            "content": message["content"]
        }

        # 把转换后的消息加入 AI 上下文列表
        ai_messages.append(ai_message)

    # 把最终可以直接发送给模型的消息列表返回出去
    return ai_messages


# 根据 conversation_id 查询一个具体聊天窗口
def get_conversation(conversation_id):

    # 通过统一入口获得数据库连接
    connection = get_connection()

    # 创建游标，用来执行 SELECT
    cursor = connection.cursor()

    # 根据主键查询指定的 conversation
    cursor.execute(
        """
        SELECT id, user_id, title, created_at
        FROM conversations
        WHERE id = ?
        """,
        (conversation_id,)
    )

    # 主键最多只能匹配一条记录，所以只取一行
    row = cursor.fetchone()

    # 查询完成以后关闭数据库连接
    connection.close()

    # 如果没有找到这个 conversation，就返回 None
    if row is None:
        return None

    # 把数据库 tuple 转成字段含义清楚的 dict
    return {
        "id": row[0],
        "user_id": row[1],
        "title": row[2],
        "created_at": row[3]
    }


# 查询某个用户拥有的全部聊天窗口
def get_conversations(user_id):

    # 通过统一入口获得数据库连接
    connection = get_connection()

    # 创建游标，用来执行 SELECT
    cursor = connection.cursor()

    # 查询 conversations 表中属于指定 user_id 的聊天
    cursor.execute(
        """
        SELECT id, user_id, title, created_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY id ASC
        """,
        (user_id,)
    )

    # 取出查询返回的全部记录
    rows = cursor.fetchall()

    # 创建一个新的列表，用来保存转换后的聊天数据
    conversations = []

    # 逐条处理数据库查询出来的 tuple
    for row in rows:

        # 把数据库的一行 tuple 转换成字段含义清楚的 dict
        conversation = {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "created_at": row[3]
        }

        # 把转换好的聊天加入结果列表
        conversations.append(conversation)

    # 查询完成以后关闭数据库连接
    connection.close()

    # 返回更适合应用程序使用的聊天列表
    return conversations

# 定义新版数据库初始化函数
def init_db():

    # 通过统一入口获得已经开启外键约束的数据库连接
    connection = get_connection()

    # 创建游标，用来执行 SQL
    cursor = connection.cursor()

    # 创建 users 表，用来保存产品里的用户
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL
        )
        """
    )

    # 创建 conversations 表，用来保存每一个独立聊天窗口
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
       """
    )    


    # 创建 messages 表，用来保存每个聊天窗口中的具体消息
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
        """
    )


    # 正式保存刚才的数据库结构修改
    connection.commit()

    # 完成后关闭数据库连接
    connection.close()


# 只有直接运行 product_database.py 时，才执行最小初始化检查
if __name__ == "__main__":

    # 初始化产品数据库，确保 users、conversations、messages 三张表存在
    init_db()

    # 仅提示初始化成功，不再自动插入或读取测试数据
    print("产品数据库初始化完成")
