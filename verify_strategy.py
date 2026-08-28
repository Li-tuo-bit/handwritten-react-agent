"""验证生成的策略代码是否可执行"""

import backtrader as bt

with open('strategies/600519_strategy.py', 'r', encoding='utf-8') as f:
    code = f.read()

print("代码内容:")
print(code[:300])
print("\n" + "="*50)

namespace = {}
exec(code, {'bt': bt}, namespace)

cls = namespace['Strategy_600519']
print(f"✅ 代码可执行！")
print(f"✅ 类名: {cls.__name__}")
print(f"✅ 继承: {cls.__bases__}")
