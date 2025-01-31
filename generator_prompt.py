import pyautogui
import pyperclip
from time import sleep
import platform
import pandas as pd

'''
从 csv 表中读取要输入到 chatgpt 的查询文本，问题的提示模板在下面构造，支持多提示。
'''

# 简化后的模板，去除了重复的“秦始皇”部分
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


def read_csv_file(file_path, start_row=1):
    """
    读取 CSV 文件并从指定行开始处理 'content' 列中的数据。

    :param file_path: CSV 文件路径
    :param start_row: 开始处理的行数（1-based）
    """
    try:
        # 使用 GB2312 编码读取 CSV 文件
        df = pd.read_csv(file_path, encoding='gb2312')
        print("CSV 文件成功读取。")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        print("请确认文件编码是否为 GB2312。")
        return
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return
    except Exception as e:
        print(f"读取 CSV 文件时发生错误: {e}")
        return

    # 检查是否存在 'content' 列
    if 'content' not in df.columns:
        print("CSV 文件中缺少 'content' 列。请检查文件格式。")
        return

    total_rows = len(df)
    if start_row < 1 or start_row > total_rows:
        print(f"start_row 参数 {start_row} 超出范围。CSV 文件共有 {total_rows} 行。")
        return

    # 使用 iloc 从指定行开始遍历（pandas 是 0-based）
    for index, part in enumerate(df['content'].iloc[start_row - 1:], start=start_row):
        # 打印当前处理的行号和内容类型
        print(f"正在处理第 {index} 条内容，类型: {type(part)}")

        # 检查分段是否为非空字符串
        if isinstance(part, str):
            stripped_part = part.strip()
            if stripped_part:
                print(f"处理第 {index} 条内容：{stripped_part}")
                prompt = template.replace('{content}', stripped_part)

                # 打印生成的 prompt 以进行调试
                print(f"生成的提示：\n{prompt}\n{'-' * 50}")

                # 复制提示到剪贴板
                pyperclip.copy(prompt + '\n')  # 添加换行符以确保格式正确

                # 判断当前操作系统是Windows还是Mac，然后执行相应的粘贴操作
                try:
                    if platform.system() == 'Windows':
                        pyautogui.hotkey('ctrl', 'v')  # 更简洁的粘贴方法
                    elif platform.system() == 'Darwin':  # 'Darwin' 是 Mac OS X 的内核名称
                        pyautogui.hotkey('command', 'v')
                    else:
                        print("不支持的操作系统。请手动粘贴。")
                        continue  # 跳过当前循环

                    pyautogui.press('enter')  # 模拟 'enter' 键，发送文本
                    print("已发送提示。等待 5 秒后处理下一条。")
                    sleep(5)  # 等待 5 秒
                except Exception as e:
                    print(f"自动化操作时发生错误: {e}")
                    print("跳过当前行。")
            else:
                print(f"跳过第 {index} 条空或仅包含空白字符的内容。")
        else:
            # 如果 'part' 不是字符串，尝试转换为字符串
            try:
                part_str = str(part).strip()
                if part_str:
                    print(f"处理第 {index} 条内容（转换后）：{part_str}")
                    prompt = template.replace('{content}', part_str)

                    # 打印生成的 prompt 以进行调试
                    print(f"生成的提示：\n{prompt}\n{'-' * 50}")

                    # 复制提示到剪贴板
                    pyperclip.copy(prompt + '\n')  # 添加换行符以确保格式正确

                    pyautogui.hotkey('ctrl', 'v')  # 更简洁的粘贴方法

                    pyautogui.press('enter')  # 模拟 'enter' 键，发送文本
                    print("已发送提示。等待 5 秒后处理下一条。")
                    sleep(15)  # 等待 5 秒

                else:
                    print(f"跳过第 {index} 条空或仅包含空白字符的内容（转换后为空）。")
            except Exception as e:
                print(f"无法将第 {index} 条内容转换为字符串: {e}")
                print("跳过当前行。")


if __name__ == "__main__":
    sleep(5)  # 延迟 5 秒执行，请在 5 秒内打开活动窗口！
    # 读取文件
    csv_file_path = '1.csv'
    start_row = 1  # 设置从第 1 行开始处理，可以根据需要修改
    read_csv_file(csv_file_path, start_row)

