# voice-package

语音包回退：语言回退链、条目缺失回退、体积预算与缺失统计，只用 Python 标准库。

```
python3 -m voice.cli --sample fallback
python3 -m voice.cli --sample budget
python3 -m voice.cli --sample missing
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **回退链**：先找目标语言的语音包，找不到就按 `chain` 里的顺序往后找，
  再找不到用链首语言。
- **条目缺失**：候选包里没有这个 key 时继续找下一个候选。
- **体积预算**：累计加载的语音包体积不超过 `budget_kb`；超出预算的包不加载，
  继续试下一个候选；全部超预算时返回 None。
- **缺失统计**：所有候选都没有这个条目时 `missing` 加一。
- **不变量**：同一个包不会被重复计费；同一串解析请求重复执行结果相同。
- **代价**：解析不许遍历全部语音包，`scanned_count` 不随包数线性增长。
- **规模**：1 万个语音包、每秒 10 万次解析，单次摊还 O(回退链长度)。

## 输出契约（不改格式）

```
pack=..
pack=.. used=..
missing=.. pack=..
```

## 目录

```
voice/core.py   回退链、预算与缺失统计
voice/cli.py    命令行入口
tests/          unittest 用例
```
