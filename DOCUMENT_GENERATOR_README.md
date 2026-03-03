# 仲裁文书自动生成系统

## 功能概述

根据立案详情数据，自动填充 Word 模板中的变量，生成完整的仲裁文书。

## 支持的变量

### 基础字段
| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `{case_no}` | 案件编号 | 明永劳人仲案字[2026]89号 |
| `{applicant}` | 申请人姓名 | 陈津 |
| `{applicant_str}` | 申请人字符串 | 陈津 |
| `{respondent}` | 被申请人名称 | 某某科技有限公司 |
| `{apply_at}` | 申请日期 | 2025-10-30 |
| `{中文_today}` | 中文日期（今日） | 二〇二六年三月三日 |

### 申请人信息
| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `{registered_permanent_residence}` | 申请人户籍地址 | 福建省永安市燕西新六路999号 |
| `{applicant_arr[0].registered_permanent_residence}` | 第一申请人户籍 | 福建省永安市... |

### 被申请人信息
| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `{respondent_arr[0].name}` | 第一被申请人名称 | 某某科技有限公司 |
| `{respondent_arr[0].company_address}` | 第一被申请人地址 | 福建省永安市燕南街道 |

### 仲裁请求
| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `{request_numbers}` | 请求编号列表 | 1、2、3 |
| `{request_1_intro}` | 第1项请求内容 | 请求裁决... |
| `{request_2_intro}` | 第2项请求内容 | 请求裁决... |
| `{total_money}` | 案件标的总和 | 46466.00 |

## API 接口

### 生成文档

**POST** `/api/doc_templates/generate`

**请求参数:**
```json
{
  "template_path": "1-立案/（受理）立案审批表.docx",
  "case_id": "199966"
}
```

**响应:**
- 成功: 返回生成的 Word 文件（下载）
- 失败: 返回 JSON 错误信息

## 使用方法

### 1. 前端调用示例

```javascript
// 生成文档
async function generateDocument(templatePath, caseId) {
    const response = await fetch('/api/doc_templates/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            template_path: templatePath,
            case_id: caseId
        })
    });
    
    if (response.ok) {
        // 下载文件
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'document.docx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } else {
        const error = await response.json();
        alert('生成失败: ' + error.message);
    }
}
```

### 2. 命令行测试

```bash
# 生成立案审批表
curl -X POST http://localhost:5000/api/doc_templates/generate \
  -H "Content-Type: application/json" \
  -d '{"template_path": "1-立案/（受理）立案审批表.docx", "case_id": "199966"}' \
  --output 立案审批表.docx
```

## 模板制作规范

1. **文件格式**: 仅支持 `.docx` 格式（Word 2007+）
2. **变量格式**: 使用 `{变量名}` 格式，如 `{case_no}`
3. **保留格式**: 系统会保留原文档的字体、对齐、缩进等格式
4. **中文日期**: 使用 `{中文_today}` 自动插入今日中文日期

## 支持的模板位置

所有模板存放在 `文件生成/` 目录下：
- `1-立案/` - 立案相关文书
- `2-开庭通知文书/` - 开庭通知
- `3-调、裁、决文书/` - 调解、裁决文书
- `4-反申请文书/` - 反申请相关
- `5-撤诉文书/` - 撤诉相关

## 注意事项

1. 旧版 `.doc` 格式需先转换为 `.docx` 格式
2. 变量名区分大小写
3. 如果变量值为空，会保留原样或显示为空
4. 生成后的文件保存在 `文件生成/output/` 目录
