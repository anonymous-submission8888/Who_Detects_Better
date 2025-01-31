import csv
import os
import re

def convert_markdown_to_csv_four_columns(txt_file, csv_file, encoding='utf-8'):
    """
    将包含“用户：[]”、“回答：[]”等格式的Markdown对话文本文件转换为 CSV 文件，
    每两组对话作为一行，包含四列：User1、Answer1、User2、Answer2。

    参数:
        txt_file (str): 输入的Markdown文本文件路径。
        csv_file (str): 输出的 CSV 文件路径。
        encoding (str): 文件的编码格式，默认为 'utf-8'。
    """
    # 检查输入文件是否存在
    if not os.path.exists(txt_file):
        print(f"错误：输入文件 {txt_file} 不存在。")
        return

    # 存储所有用户和回答的列表
    conversations = []
    current_user = None
    current_answer = None

    # 定义正则表达式以提取“用户”和“回答”内容，并去除引号和标点
    # 适应不带数字前缀且可能带有中文引号或无引号的情况
    user_pattern = re.compile(r'^用户：\s*[“"]?(.*?)[”"]?$')
    answer_pattern = re.compile(r'^回答：\s*[“"]?(.*?)[”"]?$')

    try:
        with open(txt_file, 'r', encoding=encoding) as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue  # 跳过空行

                # 检查是否为用户提问
                user_match = user_pattern.match(line)
                if user_match:
                    # 如果之前有未保存的用户和回答，先保存
                    if current_user and current_answer:
                        conversations.append((current_user, current_answer))
                        current_user = None
                        current_answer = None
                    # 提取用户内容
                    current_user = user_match.group(1).strip()
                    continue

                # 检查是否为回答
                answer_match = answer_pattern.match(line)
                if answer_match:
                    if not current_user:
                        print(f"警告：在第 {line_number} 行发现回答但没有对应的用户问题。")
                        continue
                    # 提取回答内容
                    current_answer = answer_match.group(1).strip()
                    continue

                # 检查是否为分隔符
                if line.startswith('---'):
                    continue  # 分隔符，跳过

                # 如果行不符合以上格式，可以选择忽略或进行其他处理
                print(f"警告：未识别的行格式（第 {line_number} 行）：{line}")

        # 保存最后一组用户和回答
        if current_user and current_answer:
            conversations.append((current_user, current_answer))
    except Exception as e:
        print(f"错误：无法读取文件 {txt_file}。{e}")
        return

    if not conversations:
        print("警告：未找到任何有效的用户和回答对。")
        return

    # 将对话列表每两组分为一行
    grouped_conversations = []
    for i in range(0, len(conversations), 2):
        row = {
            'User1': conversations[i][0],
            'Answer1': conversations[i][1],
            'User2': '',
            'Answer2': ''
        }
        if i + 1 < len(conversations):
            row['User2'] = conversations[i + 1][0]
            row['Answer2'] = conversations[i + 1][1]
        grouped_conversations.append(row)

    # 写入 CSV 文件
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["User1", "Answer1", "User2", "Answer2"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(grouped_conversations)
        print(f"转换完成，已将Markdown文件 {txt_file} 转换为 CSV 文件 {csv_file}。")
    except Exception as e:
        print(f"错误：无法写入 CSV 文件。{e}")

if __name__ == "__main__":
    txt_file = r"Conversation with ChatGPT.md"  # 输入的文本文件路径
    csv_file = r"5.csv"  # 输出的 CSV 文件路径
    encoding = 'utf-8'  # 根据实际文件编码修改

    convert_markdown_to_csv_four_columns(txt_file, csv_file, encoding)
