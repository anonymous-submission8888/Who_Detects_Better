import pandas as pd
import requests
from tqdm import tqdm
import time
import json
import logging

# 配置日志
logging.basicConfig(
    filename='gemini_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 定义提示模板
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


# 读取CSV文件，指定编码格式为 'gbk' 或 'gb18030'
def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path, encoding='gbk')
        logging.info("CSV 文件以 'gbk' 编码成功读取。")
        print("CSV 文件以 'gbk' 编码成功读取。")
        return df
    except UnicodeDecodeError as e:
        try:
            df = pd.read_csv(file_path, encoding='gb18030')
            logging.info("CSV 文件以 'gb18030' 编码成功读取。")
            print("CSV 文件以 'gb18030' 编码成功读取。")
            return df
        except UnicodeDecodeError as e:
            logging.error(f"UnicodeDecodeError: {e}")
            print("请确认文件编码是否为 'gbk' 或 'gb18030'。")
            return None
    except FileNotFoundError:
        logging.error(f"文件未找到: {file_path}")
        print(f"文件未找到: {file_path}")
        return None
    except Exception as e:
        logging.error(f"读取 CSV 文件时发生错误: {e}")
        print(f"读取 CSV 文件时发生错误: {e}")
        return None


# 配置Gemini API
GEMINI_API_KEY = '1'  # 直接在代码中设置您的Gemini API密钥
API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}'

# 定义请求头
headers = {
    'Content-Type': 'application/json'
}


# 定义请求函数
def get_answers_batch(batch_questions, retries=3, backoff_factor=2):
    answers = []
    for idx, question in enumerate(batch_questions, 1):
        logging.info(f"正在处理问题 {idx}/{len(batch_questions)}: {question}")
        print(f"正在处理问题 {idx}/{len(batch_questions)}: {question}")

        # 构造提示模板
        prompt = template.replace('{content}', question)

        payload = {
            'contents': [{
                'parts': [{'text': prompt}]
            }]
        }

        for attempt in range(retries):
            try:
                response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
                response.raise_for_status()
                data = response.json()

                # 处理API响应
                if 'candidates' in data and len(data['candidates']) > 0:
                    content = data['candidates'][0]
                    if 'content' in content and 'parts' in content['content'] and len(content['content']['parts']) > 0:
                        answer = content['content']['parts'][0].get('text', "").strip()
                        if answer:
                            answers.append(answer)
                            logging.info(f"成功获取回答: {answer}")
                            print(f"成功获取回答: {answer}")
                            break  # 成功后跳出重试循环
                        else:
                            logging.warning("回答内容为空，添加空值。")
                            print("警告：回答内容为空，添加空值。")
                            answers.append("")
                            break
                    else:
                        logging.warning("内容格式错误，未找到 'content' 或 'parts'。")
                        print("警告：内容格式错误，未找到 'content' 或 'parts'。")
                        answers.append("")
                        break
                else:
                    logging.warning("未找到有效的回答内容，添加空值。")
                    print("警告：未找到有效的回答内容，添加空值。")
                    answers.append("")
                    break
            except requests.exceptions.HTTPError as errh:
                logging.error(f"HTTP 错误: {errh}, 响应内容: {response.text}")
                print(f"HTTP 错误: {errh}")
                print(f"响应内容: {response.text}")
            except requests.exceptions.ConnectionError as errc:
                logging.error(f"连接错误: {errc}")
                print(f"连接错误: {errc}")
            except requests.exceptions.Timeout as errt:
                logging.error(f"超时错误: {errt}")
                print(f"超时错误: {errt}")
            except requests.exceptions.RequestException as err:
                logging.error(f"其他请求错误: {err}")
                print(f"其他请求错误: {err}")

            # 如果还没达到最大重试次数，等待后再重试
            if attempt < retries - 1:
                wait_time = backoff_factor ** attempt
                logging.info(f"等待 {wait_time} 秒后重试...")
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logging.error("达到最大重试次数，添加空值。")
                print("达到最大重试次数，添加空值。")
                answers.append("")
        # 添加延迟以避免速率限制
        time.sleep(1)
    return answers


# 分割列表为批次
def split_into_batches(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


# 主函数
def main():
    # 配置文件路径
    input_csv = '1.csv'  # 替换为你的CSV文件路径
    output_csv = '5.csv'  # 输出文件路径，去掉外层双引号

    # 读取CSV文件，指定编码格式
    df = read_csv_file(input_csv)
    if df is None:
        print("无法继续，读取 CSV 文件失败。")
        logging.error("无法继续，读取 CSV 文件失败。")
        return

    # 检查是否存在 'content' 列
    if 'content' not in df.columns:
        print("CSV 文件中缺少 'content' 列。请检查文件格式。")
        logging.error("CSV 文件中缺少 'content' 列。")
        return

    # 提取问题列表
    questions = df['content'].dropna().astype(str).tolist()
    print(f"总共读取到 {len(questions)} 个问题。")
    logging.info(f"总共读取到 {len(questions)} 个问题。")

    if not questions:
        print("警告：没有找到任何问题。")
        logging.warning("没有找到任何问题。")
        return

    # 定义批次大小
    BATCH_SIZE = 5  # 根据API限制调整

    # 初始化答案列表
    answers = []

    # 处理每个批次
    for batch_number, batch in enumerate(split_into_batches(questions, BATCH_SIZE), 1):
        print(f"处理第 {batch_number} 批，共 {len(batch)} 个问题。")
        logging.info(f"处理第 {batch_number} 批，共 {len(batch)} 个问题。")
        batch_answers = get_answers_batch(batch)
        answers.extend(batch_answers)

    # 检查是否所有问题都有答案
    if len(answers) != len(questions):
        print("警告：答案数量与问题数量不匹配！")
        logging.warning("答案数量与问题数量不匹配。")
        # 填充空值
        while len(answers) < len(questions):
            answers.append("")

    # 将答案添加到DataFrame
    df['answer'] = answers
    print(f"总共收集到 {len(answers)} 个答案。")
    logging.info(f"总共收集到 {len(answers)} 个答案。")

    # 保存到新的CSV文件
    try:
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"处理完成，结果已保存到 {output_csv}")
        logging.info(f"处理完成，结果已保存到 {output_csv}")
    except Exception as e:
        print(f"保存 CSV 文件时发生错误: {e}")
        logging.error(f"保存 CSV 文件时发生错误: {e}")


# 测试单个请求
def test_single_question():
    test_question = "这是一个测试问题。"
    prompt = template.replace('{content}', test_question)

    payload = {
        'contents': [{
            'parts': [{'text': prompt}]
        }]
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        print("完整响应内容：", json.dumps(data, ensure_ascii=False, indent=2))
        logging.info("完整响应内容：" + json.dumps(data, ensure_ascii=False, indent=2))

        # 处理API响应
        if 'candidates' in data and len(data['candidates']) > 0:
            content = data['candidates'][0]
            if 'content' in content and 'parts' in content['content'] and len(content['content']['parts']) > 0:
                answer = content['content']['parts'][0].get('text', "").strip()
                print("测试回答：", answer)
                logging.info(f"测试回答：{answer}")
            else:
                print("未找到有效的回答内容。")
                logging.warning("未找到有效的回答内容。")
        else:
            print("未找到有效的回答内容。")
            logging.warning("未找到有效的回答内容。")
    except Exception as e:
        print(f"测试请求出错: {e}")
        logging.error(f"测试请求出错: {e}")
        if 'response' in locals():
            print(f"响应内容: {response.text}")
            logging.error(f"响应内容: {response.text}")


if __name__ == "__main__":
    # 首先运行测试函数，确保API响应正常
    print("运行测试单个问题...")
    test_single_question()
    print("\n开始处理CSV文件...")
    main()
