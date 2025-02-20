import pandas as pd
import zhipuai  # 导入智谱AI SDK
from IPython.display import Markdown
import time
import json

# **1. 设置您的 API 密钥**
API_KEY = '1'  # 替换为您的实际 API 密钥

# **2. 配置 SDK**
client = zhipuai.ZhipuAI(api_key=API_KEY)

# **3. 定义模型名称**
MODEL_NAME = 'glm-4-plus'  # 替换为您要调用的实际模型名称

# **4. 定义提示模板**
template = '''
判断下列信息是否正确：
"{content}"
请你为我构造一个多轮问答数据，第一轮是用户提供的信息和你认为的标准答案；第二轮是用户提问为什么和你对信息的分析。格式为：
1用户：[]。
2回答：[]。
3用户：
4回答：
请你的回答中去除格式前的数字，并且要空行
'''

# **5. 读取 CSV 文件**
input_csv = '1.csv'  # 替换为您的 CSV 文件路径
output_csv = '5.csv'  # 输出文件路径

try:
    df = pd.read_csv(input_csv, encoding='gbk')
    print("CSV 文件以 'gbk' 编码成功读取。")
except UnicodeDecodeError:
    try:
        df = pd.read_csv(input_csv, encoding='gb18030')
        print("CSV 文件以 'gb18030' 编码成功读取。")
    except Exception as e:
        print(f"读取 CSV 文件时发生错误: {e}")
        exit(1)
except FileNotFoundError:
    print(f"文件未找到: {input_csv}")
    exit(1)
except Exception as e:
    print(f"读取 CSV 文件时发生错误: {e}")
    exit(1)

# **6. 检查 'content' 列是否存在**
if 'content' not in df.columns:
    print("CSV 文件中缺少 'content' 列。请检查文件格式。")
    exit(1)

# **7. 提取问题列表**
questions = df['content'].dropna().astype(str).tolist()
print(f"总共读取到 {len(questions)} 个问题。")

# **8. 定义批次大小**
BATCH_SIZE = 5  # 根据 API 限制调整

# **9. 初始化答案列表**
answers = []

# **10. 处理每个批次**
for i in range(0, len(questions), BATCH_SIZE):
    batch = questions[i:i + BATCH_SIZE]
    batch_answers = []
    for question in batch:
        # 构造提示
        prompt_content = template.replace('{content}', question)

        # 构造消息列表，包含 system 和 user 消息
        messages = [
            {
                "role": "system",
                "content": "你是一个帮助用户生成多轮问答数据的助手。"
            },
            {
                "role": "user",
                "content": prompt_content
            }
        ]

        try:
            # 调用智谱AI的聊天完成接口
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7,  # 可根据需要调整
                max_tokens=500  # 根据需要调整
            )

            # **修正部分：使用属性访问而不是字典访问**
            answer = response.choices[0].message.content.strip()
            batch_answers.append(answer)
            print(f"成功获取回答：{answer[:50]}...")  # 打印部分回答用于调试
        except Exception as e:
            print(f"生成内容时发生错误: {e}")
            batch_answers.append("")

        # 延迟以避免速率限制
        time.sleep(1)  # 根据需要调整延迟时间

    answers.extend(batch_answers)
    print(f"已处理批次 {i // BATCH_SIZE + 1} / {(len(questions) + BATCH_SIZE - 1) // BATCH_SIZE}")

# **11. 检查答案数量是否与问题数量匹配**
if len(answers) != len(questions):
    print("警告：答案数量与问题数量不匹配！")
    while len(answers) < len(questions):
        answers.append("")

# **12. 将答案添加到 DataFrame**
df['answer'] = answers

# **13. 保存到新的 CSV 文件**
try:
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"处理完成，结果已保存到 {output_csv}")
except Exception as e:
    print(f"保存 CSV 文件时发生错误: {e}")
