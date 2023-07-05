import ast

# 读取文件
with open('app.py', 'r') as f:
    # 转换为ast对象
    node = ast.parse(f.read())
    # 打印ast对象
    print(ast.dump(node))
