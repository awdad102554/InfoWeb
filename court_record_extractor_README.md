# 劳动仲裁庭审笔录信息提取脚本

## 文件说明

| 文件 | 说明 |
|------|------|
| `court_record_extractor.py` | 主提取脚本 |
| `batch_test.py` | 批量测试脚本 |
| `court_record_extractor_README.md` | 本文档 |

## 提取逻辑

### 参数来源（与生成Word保持一致）

```
textPart1: 取第一份同时满足以下条件的笔录的 part1
  - title 包含 "开庭笔录" 或 "庭审笔录"
  - save_path 包含 "开庭笔录" 或 "庭审笔录"

textPart2: 取第一份同时满足以下条件的笔录的 part2
  - title 包含 "开庭笔录" 或 "庭审笔录"
  - save_path 包含 "开庭笔录" 或 "庭审笔录"

textPart3: 收集所有满足以下条件的笔录的 part3，以title为键组成JSON对象
  - title 包含 "开庭笔录" 或 "庭审笔录"
  （注意：part3不需要检查save_path）
```

### 提取字段

| 字段 | 来源 | 说明 |
|------|------|------|
| 委员会 | textPart1 | 提取"XX劳动人事争议仲裁委员会" |
| 案号 | textPart1 | 提取案号，去除"明"前缀，括号统一为〔〕 |
| 案由 | textPart1 | 从"关于...争议"提取，格式化为"支付+类型" |
| 开庭时间 | textPart1 | 提取并简化为"上午/下午" |
| 当事人和委托代理人信息 | textPart2 | 提取申请人、被申请人、代理人、法定代表人 |
| 首席仲裁员 | textPart3 | 提取"本案由"后的第1个姓名 |
| 仲裁员1 | textPart3 | 提取"本案由"后的第2个姓名 |
| 仲裁员2 | textPart3 | 提取"本案由"后的第3个姓名 |
| 书记员 | textPart3 | 提取"担任书记员"前的姓名 |

## 使用方法

### 方式1：命令行参数

```bash
python3 court_record_extractor.py \
  -p1 "textPart1内容" \
  -p2 "textPart2内容" \
  -p3 "textPart3内容"
```

### 方式2：JSON标准输入

```bash
echo '{"textPart1":"...","textPart2":"...","textPart3":"..."}' | \
  python3 court_record_extractor.py
```

### 方式3：JSON文件

```bash
python3 court_record_extractor.py -j input.json
```

input.json 格式：
```json
{
  "textPart1": "开庭信息...",
  "textPart2": "当事人信息...",
  "textPart3": "笔录内容..."
}
```

### 方式4：运行内置测试

```bash
python3 court_record_extractor.py -t
```

### 批量测试

```bash
python3 batch_test.py
```

## 输出格式

```json
{
  "委员会": "永安市劳动人事争议仲裁委员会",
  "案号": "永劳人仲案字〔2025〕427号",
  "案由": "支付劳动报酬等",
  "开庭时间": "2026年03月04日上午",
  "当事人和委托代理人信息": "申请人：李上梅...\n委托代理人：范文秀...",
  "首席仲裁员": "胡海亮",
  "仲裁员1": "黄燕黎",
  "仲裁员2": "吴&nbsp;洁",
  "书记员": "陈文婷"
}
```

## 特殊处理

1. **姓名格式化**：2字姓名自动添加 `&nbsp;`（如"吴洁"→"吴&nbsp;洁"）
2. **案号处理**：自动去除"明"前缀，括号统一转换为〔〕
3. **案由处理**：多个争议类型用"等"简化（如"工资、加班费"→"支付工资等"）
4. **时间处理**：具体时间简化为"上午/下午"
5. **数据清洗**：自动删除"委托权限"等冗余内容

## 错误处理

脚本对以下情况做了容错处理：

- 空输入：返回空字符串的JSON结构
- 部分缺失：提取成功的字段，缺失的字段返回空字符串
- JSON解析错误：尝试作为普通字符串处理
- 正则匹配失败：返回空字符串

## 调试

查看详细错误信息：

```python
import traceback
from court_record_extractor import extract_court_record

try:
    result = extract_court_record(text1, text2, text3)
except Exception as e:
    print(f"错误: {e}")
    traceback.print_exc()
```

## 与Dify Workflow集成

在Dify Workflow中调用：

1. 使用HTTP请求节点调用 `http://127.0.0.1:5000/api/handle/detail?id={case_id}`
2. 从返回的 `writing_json` 中提取 textPart1、textPart2、textPart3
3. 调用本脚本进行信息提取
4. 将提取结果用于生成裁决书
