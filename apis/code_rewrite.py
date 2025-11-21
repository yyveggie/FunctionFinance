import os

# 设置您的项目目录路径
project_directory = './apis'

# 指定需要替换的旧代码行和新代码行
old_line = '@handle_large_data\n'  # 确保包含换行符，因为读取的行末尾通常会有它
new_line = '@handle_large_data()\n'

# 遍历项目目录中的所有文件
for root, dirs, files in os.walk(project_directory):
    for file in files:
        print(file)
        if file.endswith('.py'):  # 只处理 Python 文件
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 标记文件是否需要被重写
            rewrite_file = False
            
            # 检查文件中的每一行，以确定是否需要进行替换
            updated_lines = []
            for line in lines:
                # 对比去除尾随空格和换行符后的行
                if line.rstrip('\n') == old_line.rstrip('\n'):
                    updated_lines.append(new_line)
                    rewrite_file = True
                else:
                    updated_lines.append(line)
            
            # 如果需要，重写文件
            if rewrite_file:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)

print("代码更新完成。")
