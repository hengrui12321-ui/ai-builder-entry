# 导入 uuid，用来生成唯一会话编号
import uuid


# 保存 session_id 的文件名称
SESSION_FILE = "session_id.txt"


# 定义获取 session_id 的函数
def get_session_id():

    # 尝试读取已经存在的 session_id 文件
    try:

        # 打开 session_id.txt，并读取里面的内容
        with open(SESSION_FILE, "r") as file:

            # 删除前后空格和换行
            session_id = file.read().strip()

        # 如果文件里面有内容，就直接返回旧 session_id
        if session_id:

            return session_id


    # 如果文件不存在，就进入这里
    except FileNotFoundError:

        pass


    # 如果没有旧 session_id，就创建新的 UUID
    session_id = str(uuid.uuid4())


    # 打开文件，把新的 session_id 保存进去
    with open(SESSION_FILE, "w") as file:

        # 写入新的 session_id
        file.write(session_id)


    # 返回新的 session_id
    return session_id


# 只有直接运行 session.py 时才执行测试
if __name__ == "__main__":

    # 获取当前 session_id
    session_id = get_session_id()

    # 打印当前 session_id
    print("当前 session_id:", session_id)
