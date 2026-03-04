#!/usr/bin/env python3
"""
仲裁文书生成器 - 根据案件数据填充模板
支持 Word (.docx) 和 Excel (.xls, .xlsx) 格式
"""
import os
import re
import shutil
from datetime import datetime
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class DocumentGenerator:
    """文书生成器"""
    
    def __init__(self, template_path, output_path):
        self.template_path = template_path
        self.output_path = output_path
        self.file_ext = os.path.splitext(template_path)[1].lower()
        
    def generate(self, data):
        """
        根据数据填充模板
        data: 立案详情API返回的数据
        """
        # 预处理数据 - 将复杂表达式转换为简单变量
        processed_data = self._preprocess_data(data)
        
        print(f"预处理后的数据: {processed_data}")
        
        # 根据文件类型选择不同的处理方式
        if self.file_ext == '.docx':
            self._generate_word(processed_data)
        elif self.file_ext in ['.xls', '.xlsx']:
            self._generate_excel(processed_data)
        else:
            raise ValueError(f"不支持的文件格式: {self.file_ext}")
        
        return self.output_path
    
    def _generate_word(self, data):
        """生成 Word 文档"""
        doc = Document(self.template_path)
        
        # 替换所有段落中的变量
        for para in doc.paragraphs:
            self._replace_in_paragraph(para, data)
        
        # 替换表格中的变量
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._replace_in_paragraph(para, data)
        
        doc.save(self.output_path)
    
    def _generate_excel(self, data):
        """生成 Excel 文档 - 保留格式"""
        if self.file_ext == '.xlsx':
            self._generate_excel_xlsx(data)
        elif self.file_ext == '.xls':
            self._generate_excel_xls(data)
    
    def _generate_excel_xlsx(self, data):
        """生成 .xlsx 格式，严格保留格式"""
        from openpyxl import load_workbook
        
        # 加载工作簿，保留所有格式
        # data_only=False: 保留公式而不是计算值
        # keep_vba=False: 不保留VBA（一般模板没有VBA代码）
        wb = load_workbook(self.template_path, data_only=False, keep_vba=False)
        
        # 遍历所有工作表
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            # 遍历所有单元格
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        original_value = cell.value
                        new_value = self._replace_text(original_value, data)
                        if new_value != original_value:
                            # 关键：只修改value，保留所有其他格式属性
                            cell.value = new_value
        
        # 保存时使用相同的文件格式
        wb.save(self.output_path)
    
    def _generate_excel_xls(self, data):
        """生成 .xls 格式，严格保留格式 - 使用低级API完整复制格式"""
        import xlrd
        import xlwt
        from xlutils.copy import copy
        
        # 打开原工作簿，保留格式信息
        rb = xlrd.open_workbook(self.template_path, formatting_info=True)
        
        # 创建一个新的工作簿，手动复制所有格式
        wb = xlwt.Workbook(style_compression=2)
        
        # 复制样式表
        def get_xf_style(xf_index, rdbook):
            """将xlrd的XF转换为xlwt的XFStyle"""
            xf = rdbook.xf_list[xf_index]
            font = rdbook.font_list[xf.font_index]
            
            # 创建字体
            wt_font = xlwt.Font()
            wt_font.name = font.name
            wt_font.height = font.height
            wt_font.bold = font.bold
            wt_font.italic = font.italic
            wt_font.underline = font.underline_type
            wt_font.colour_index = font.colour_index
            
            # 创建对齐
            wt_align = xlwt.Alignment()
            wt_align.horz = xf.alignment.hor_align
            wt_align.vert = xf.alignment.vert_align
            wt_align.wrap = xf.alignment.text_wrapped
            
            # 创建边框
            wt_borders = xlwt.Borders()
            wt_borders.left = xf.border.left_line_style
            wt_borders.right = xf.border.right_line_style
            wt_borders.top = xf.border.top_line_style
            wt_borders.bottom = xf.border.bottom_line_style
            wt_borders.left_colour = xf.border.left_colour_index
            wt_borders.right_colour = xf.border.right_colour_index
            wt_borders.top_colour = xf.border.top_colour_index
            wt_borders.bottom_colour = xf.border.bottom_colour_index
            
            # 创建图案（背景）
            wt_pattern = xlwt.Pattern()
            wt_pattern.pattern = xf.background.fill_pattern
            wt_pattern.pattern_fore_colour = xf.background.pattern_colour_index
            wt_pattern.pattern_back_colour = xf.background.background_colour_index
            
            # 创建保护
            wt_protection = xlwt.Protection()
            wt_protection.cell_locked = xf.protection.cell_locked
            wt_protection.formula_hidden = xf.protection.formula_hidden
            
            # 创建XFStyle
            style = xlwt.XFStyle()
            style.font = wt_font
            style.alignment = wt_align
            style.borders = wt_borders
            style.pattern = wt_pattern
            style.protection = wt_protection
            style.num_format_str = rdbook.format_map[xf.format_key].format_str if xf.format_key in rdbook.format_map else 'General'
            
            return style
        
        # 复制每个工作表
        for sheet_idx in range(rb.nsheets):
            rs = rb.sheet_by_index(sheet_idx)
            
            # 添加工作表
            ws = wb.add_sheet(rs.name, cell_overwrite_ok=True)
            
            # 复制列宽
            for col_idx in range(rs.ncols):
                try:
                    width = rb.sheet_by_index(sheet_idx).colinfo_map[col_idx].width
                    ws.col(col_idx).width = width
                except KeyError:
                    pass
            
            # 复制行高和单元格内容
            for row_idx in range(rs.nrows):
                try:
                    height = rb.sheet_by_index(sheet_idx).rowinfo_map[row_idx].height
                    ws.row(row_idx).height = height
                except KeyError:
                    pass
                
                for col_idx in range(rs.ncols):
                    cell = rs.cell(row_idx, col_idx)
                    cell_value = cell.value
                    xf_index = cell.xf_index
                    
                    # 替换变量
                    if cell_value and isinstance(cell_value, str):
                        new_value = self._replace_text(cell_value, data)
                    else:
                        new_value = cell_value
                    
                    # 获取样式
                    if xf_index < len(rb.xf_list):
                        style = get_xf_style(xf_index, rb)
                    else:
                        style = xlwt.Style.default_style
                    
                    # 写入单元格
                    ws.write(row_idx, col_idx, new_value, style)
        
        wb.save(self.output_path)
    
    def _extract_variables(self, text):
        """提取文本中的所有变量，支持嵌套的{}"""
        variables = []
        i = 0
        while i < len(text):
            if text[i] == '{':
                # 找到匹配的}
                count = 1
                j = i + 1
                while j < len(text) and count > 0:
                    if text[j] == '{':
                        count += 1
                    elif text[j] == '}':
                        count -= 1
                    j += 1
                
                if count == 0:
                    # 找到完整的变量
                    var_content = text[i+1:j-1]
                    variables.append((i, j, var_content))
                    i = j
                else:
                    i += 1
            else:
                i += 1
        
        return variables
    
    def _replace_text(self, text, data):
        """替换文本中的变量 - 支持嵌套的JavaScript模板字符串"""
        if not text or not isinstance(text, str):
            return text
        
        original_text = text
        
        # 提取所有变量（支持嵌套）
        variables = self._extract_variables(text)
        
        # 从后向前替换，避免位置变化
        for start, end, var_content in reversed(variables):
            var_clean = var_content.strip()
            if var_clean in data:
                value = str(data[var_clean])
                text = text[:start] + value + text[end:]
                print(f"替换: {{{var_clean[:50]}...}} -> {value[:50]}...")
        
        return text
    
    def _replace_in_paragraph(self, para, data):
        """替换段落中的变量（Word）"""
        if not para.text:
            return
        
        text = para.text
        original_text = text
        
        # 使用完整的替换逻辑
        text = self._replace_text(text, data)
        
        # 如果有替换，更新段落文本（保留格式）
        if text != original_text:
            if para.runs:
                # 分析段落中包含变量内容的 runs（包含 { 或 } 的 runs）
                runs_with_vars = []
                
                for run in para.runs:
                    run_text = run.text
                    if run_text.strip():  # 忽略纯空白 runs
                        if '{' in run_text or '}' in run_text:
                            runs_with_vars.append(run)
                
                # 判断是否应该加粗：
                # 只有当变量所在的 runs 明确设置为加粗时才加粗
                # 否则（包括 None 或 False）都不加粗
                if runs_with_vars:
                    # 检查是否有任何变量 run 明确设置为加粗
                    any_var_bold_true = any(run.font.bold is True for run in runs_with_vars)
                    # 检查是否所有变量 runs 都明确设置为非加粗
                    all_var_bold_false = all(run.font.bold is False for run in runs_with_vars)
                    
                    if any_var_bold_true:
                        target_bold = True
                    elif all_var_bold_false:
                        target_bold = False
                    else:
                        # 有 None 的情况（未明确设置），默认不加粗
                        target_bold = False
                else:
                    # 没有识别到变量 runs，使用第一个 run 的格式（向后兼容）
                    first_run = para.runs[0]
                    target_bold = first_run.font.bold if first_run.font.bold is not None else False
                
                # 获取其他格式属性（使用第一个 run）
                first_run = para.runs[0]
                font_name = first_run.font.name
                font_size = first_run.font.size
                italic = first_run.font.italic
                underline = first_run.font.underline
                
                # 清除所有 runs
                for run in para.runs[1:]:
                    run._element.getparent().remove(run._element)
                
                # 设置新文本
                para.runs[0].text = text
                
                # 恢复格式
                if font_name:
                    para.runs[0].font.name = font_name
                if font_size:
                    para.runs[0].font.size = font_size
                # 明确设置加粗或不加粗
                para.runs[0].font.bold = target_bold
                if italic is not None:
                    para.runs[0].font.italic = italic
                if underline is not None:
                    para.runs[0].font.underline = underline
    
    def _get_field(self, data, primary_key, fallback_keys=None, default=''):
        """
        从字典中获取字段值，支持多个备选键名
        
        Args:
            data: 字典数据
            primary_key: 主键名
            fallback_keys: 备选键名列表
            default: 默认值
        
        Returns:
            字段值或默认值
        """
        if not isinstance(data, dict):
            return default
        
        # 尝试主键
        if primary_key in data:
            value = data[primary_key]
            return value if value is not None else default
        
        # 尝试备选键
        if fallback_keys:
            for key in fallback_keys:
                if key in data:
                    value = data[key]
                    return value if value is not None else default
        
        return default
    
    def _preprocess_data(self, data):
        """预处理数据，计算所有变量值"""
        result = {}
        
        # 获取案件数据（处理嵌套结构）
        # 尝试多种可能的数据结构
        case_data = data
        if 'data' in data:
            case_data = data['data']
            if isinstance(case_data, dict) and 'data' in case_data:
                case_data = case_data['data']
        
        print(f"案件数据 keys: {case_data.keys() if hasattr(case_data, 'keys') else 'N/A'}")
        
        # 1. 基础字段
        case_no = case_data.get('case_no', '')
        # 如果 case_no 以"明"开头，则去掉"明"字
        if case_no and case_no.startswith('明'):
            case_no = case_no[1:]
        # 将方括号 [] 替换为圆括号 ()
        case_no = case_no.replace('[', '（').replace(']', '）')
        result['case_no'] = case_no
        result['applicant'] = case_data.get('applicant', '')
        # 处理带空格的变量 { applicant}
        result[' applicant'] = case_data.get('applicant', '')
        result['applicant_str'] = case_data.get('applicant_str', '')
        result['respondent'] = case_data.get('respondent', '')
        result['apply_at'] = case_data.get('apply_at', '')
        result['handle_at'] = case_data.get('handle_at', '')
        result['case_reason'] = case_data.get('case_reason', '')
        
        # 2. 申请人信息
        applicant_arr = case_data.get('applicant_arr', [])
        print(f"申请人数量: {len(applicant_arr)}")
        
        if applicant_arr and len(applicant_arr) > 0:
            first_applicant = applicant_arr[0]
            print(f"第一个申请人 keys: {list(first_applicant.keys()) if isinstance(first_applicant, dict) else 'N/A'}")
            
            result['registered_permanent_residence'] = self._get_field(first_applicant, 'registered_permanent_residence')
            result['applicant_name'] = self._get_field(first_applicant, 'name')
            result['applicant_mobile'] = self._get_field(first_applicant, 'mobile', ['phone', 'tel', 'telephone'])
            result['applicant_id_number'] = self._get_field(first_applicant, 'id_number')
            # 数组形式访问
            result['applicant_arr[0].name'] = self._get_field(first_applicant, 'name')
            result['applicant_arr[0].mobile'] = self._get_field(first_applicant, 'mobile', ['phone', 'tel', 'telephone'])
            result['applicant_arr[0].id_number'] = self._get_field(first_applicant, 'id_number')
            result['applicant_arr[0].address'] = self._get_field(first_applicant, 'registered_permanent_residence', ['address'])
            result['applicant_arr[0].registered_permanent_residence'] = self._get_field(first_applicant, 'registered_permanent_residence')
            
            # 申请人代理人信息
            agents = first_applicant.get('agents', [])
            print(f"第一个申请人代理人数量: {len(agents)}")
            
            if agents and len(agents) > 0:
                first_agent = agents[0]
                print(f"第一个申请人第一个代理人 keys: {list(first_agent.keys()) if isinstance(first_agent, dict) else 'N/A'}")
                
                result['applicant_arr[0].agents[0].name'] = self._get_field(first_agent, 'name')
                result['applicant_arr[0].agents[0].mobile'] = self._get_field(first_agent, 'mobile', ['phone', 'tel', 'telephone'])
                result['applicant_agent_name'] = self._get_field(first_agent, 'name')
                result['applicant_agent_mobile'] = self._get_field(first_agent, 'mobile', ['phone', 'tel', 'telephone'])
                
                print(f"applicant_arr[0].agents[0].mobile 赋值: '{result['applicant_arr[0].agents[0].mobile']}'")
            else:
                result['applicant_arr[0].agents[0].name'] = ''
                result['applicant_arr[0].agents[0].mobile'] = ''
                result['applicant_agent_name'] = ''
                result['applicant_agent_mobile'] = ''
                print("applicant_arr[0].agents[0].mobile 赋值为空字符串（无代理人）")
        else:
            result['registered_permanent_residence'] = ''
            result['applicant_name'] = ''
            result['applicant_mobile'] = ''
            result['applicant_id_number'] = ''
            result['applicant_arr[0].name'] = ''
            result['applicant_arr[0].mobile'] = ''
            result['applicant_arr[0].id_number'] = ''
            result['applicant_arr[0].address'] = ''
            result['applicant_arr[0].registered_permanent_residence'] = ''
            result['applicant_arr[0].agents[0].name'] = ''
            result['applicant_arr[0].agents[0].mobile'] = ''
            result['applicant_agent_name'] = ''
            result['applicant_agent_mobile'] = ''
            print("applicant_arr[0].agents[0].mobile 赋值为空字符串（无申请人）")
        
        # 3. 被申请人信息（支持多个）
        respondent_arr = case_data.get('respondent_arr', [])
        print(f"被申请人数量: {len(respondent_arr)}")
        
        # 第一个被申请人
        if respondent_arr and len(respondent_arr) > 0:
            first_respondent = respondent_arr[0]
            print(f"第一个被申请人 keys: {list(first_respondent.keys()) if isinstance(first_respondent, dict) else 'N/A'}")
            
            result['respondent_arr[0].name'] = self._get_field(first_respondent, 'name')
            result['respondent_arr[0].company_address'] = self._get_field(first_respondent, 'company_address', ['address'])
            result['respondent_name'] = self._get_field(first_respondent, 'name')
            result['respondent_address'] = self._get_field(first_respondent, 'company_address', ['address'])
            result['respondent_social_code'] = self._get_field(first_respondent, 'social_code')
            result['respondent_legal_name'] = self._get_field(first_respondent, 'legal_name')
            result['respondent_arr[0].legal_name'] = self._get_field(first_respondent, 'legal_name')
            # 支持多种可能的字段名：legal_mobile, legal_phone, legal_tel, phone, mobile
            result['respondent_arr[0].legal_mobile'] = self._get_field(
                first_respondent, 'legal_mobile', 
                ['legal_phone', 'legal_tel', 'phone', 'mobile', 'tel', 'telephone']
            )
            
            print(f"respondent_arr[0].legal_mobile 赋值: '{result['respondent_arr[0].legal_mobile']}'")
            
            # 被申请人代理人信息
            agents = first_respondent.get('agents', [])
            print(f"第一个被申请人代理人数量: {len(agents)}")
            
            if agents and len(agents) > 0:
                first_agent = agents[0]
                print(f"第一个被申请人第一个代理人 keys: {list(first_agent.keys()) if isinstance(first_agent, dict) else 'N/A'}")
                
                result['respondent_arr[0].agents[0].name'] = self._get_field(first_agent, 'name')
                result['respondent_arr[0].agents[0].mobile'] = self._get_field(
                    first_agent, 'mobile', 
                    ['phone', 'tel', 'telephone']
                )
                result['respondent_agent_name'] = self._get_field(first_agent, 'name')
                result['respondent_agent_mobile'] = self._get_field(
                    first_agent, 'mobile', 
                    ['phone', 'tel', 'telephone']
                )
                
                print(f"respondent_arr[0].agents[0].mobile 赋值: '{result['respondent_arr[0].agents[0].mobile']}'")
            else:
                result['respondent_arr[0].agents[0].name'] = ''
                result['respondent_arr[0].agents[0].mobile'] = ''
                result['respondent_agent_name'] = ''
                result['respondent_agent_mobile'] = ''
                print("respondent_arr[0].agents[0].mobile 赋值为空字符串（无代理人）")
        else:
            result['respondent_arr[0].name'] = ''
            result['respondent_arr[0].company_address'] = ''
            result['respondent_name'] = ''
            result['respondent_address'] = ''
            result['respondent_social_code'] = ''
            result['respondent_legal_name'] = ''
            result['respondent_arr[0].legal_name'] = ''
            result['respondent_arr[0].legal_mobile'] = ''
            result['respondent_arr[0].agents[0].name'] = ''
            result['respondent_arr[0].agents[0].mobile'] = ''
            result['respondent_agent_name'] = ''
            result['respondent_agent_mobile'] = ''
            print("respondent_arr[0].legal_mobile 和 respondent_arr[0].agents[0].mobile 赋值为空字符串（无被申请人）")
        
        # 第二个被申请人（如果存在）
        if respondent_arr and len(respondent_arr) > 1:
            second_respondent = respondent_arr[1]
            result['respondent_arr[1].name'] = self._get_field(second_respondent, 'name')
            result['respondent_arr[1].legal_name'] = self._get_field(second_respondent, 'legal_name')
            result['respondent_arr[1].legal_mobile'] = self._get_field(
                second_respondent, 'legal_mobile',
                ['legal_phone', 'legal_tel', 'phone', 'mobile', 'tel', 'telephone']
            )
            
            agents = second_respondent.get('agents', [])
            if agents and len(agents) > 0:
                first_agent = agents[0]
                result['respondent_arr[1].agents[0].name'] = self._get_field(first_agent, 'name')
                result['respondent_arr[1].agents[0].mobile'] = self._get_field(
                    first_agent, 'mobile',
                    ['phone', 'tel', 'telephone']
                )
            else:
                result['respondent_arr[1].agents[0].name'] = ''
                result['respondent_arr[1].agents[0].mobile'] = ''
        else:
            # 确保第二个被申请人的变量也有默认值
            result['respondent_arr[1].name'] = ''
            result['respondent_arr[1].legal_name'] = ''
            result['respondent_arr[1].legal_mobile'] = ''
            result['respondent_arr[1].agents[0].name'] = ''
            result['respondent_arr[1].agents[0].mobile'] = ''
        
        # 4. 仲裁请求列表
        case_arb_request = case_data.get('case_arb_request', [])
        
        # 请求数量
        result['request_count'] = str(len(case_arb_request))
        
        if case_arb_request:
            # 生成请求编号列表 "1、2、3"
            request_numbers = '、'.join([str(i + 1) for i in range(len(case_arb_request))])
            result['request_numbers'] = request_numbers
            
            # 每个请求的 intro 和 object
            for i, req in enumerate(case_arb_request):
                result[f'request_{i+1}_intro'] = req.get('intro', '')
                result[f'request_{i+1}_object'] = req.get('object', '')
                # 支持 {item.intro} 形式的变量（在表格循环中）
                if i == 0:
                    result['item.intro'] = req.get('intro', '')
            
            # 生成请求列表文本（用于显示）
            request_list = []
            for i, req in enumerate(case_arb_request):
                intro = req.get('intro', '')
                if intro:
                    request_list.append(f"{i+1}. {intro}")
            result['request_list'] = '\n'.join(request_list)
            
            # 生成JavaScript风格的表格循环内容
            # 完整的表达式: data.case_arb_request.map((item, idx) => `${idx + 1}. ${item.intro}`).join('\n')
            request_lines = []
            for i, req in enumerate(case_arb_request):
                intro = req.get('intro', '')
                request_lines.append(f"{i+1}. {intro}")
            request_text = '\n'.join(request_lines)
            
            # 支持这种复杂的模板表达式 - 注意转义字符的处理
            result["data.case_arb_request.map((item, idx) => `${idx + 1}. ${item.intro}`).join('\\n')"] = request_text
        else:
            result['request_numbers'] = ''
            result['request_list'] = ''
            result['item.intro'] = ''
            result["data.case_arb_request.map((item, idx) => `${idx + 1}. ${item.intro}`).join('\\n')"] = ''
        
        # 5. 案件标的总和
        total_money = sum(
            float(req.get('object', 0) or 0) 
            for req in case_arb_request
        )
        result['total_money'] = f"{total_money:.2f}"
        # 支持 JavaScript 表达式形式的变量名
        result['case_arb_request.reduce((sum, item) => sum + parseFloat(item.object || 0), 0).toFixed(2)'] = f"{total_money:.2f}"
        
        # 6. 第三人信息
        thirdpartys = case_data.get('thirdpartys', '')
        result['thirdpartys'] = thirdpartys if thirdpartys else ''
        
        # 7. 中文日期（今日）
        result['中文_today'] = self._get_chinese_date()
        result['today'] = datetime.now().strftime('%Y-%m-%d')
        
        # 8. 立案日期格式化（中文）
        handle_at = case_data.get('handle_at', '')
        if handle_at:
            try:
                dt = datetime.strptime(handle_at.split()[0], '%Y-%m-%d')
                result['handle_at_chinese'] = self._get_chinese_date(dt)
                result['中文_handle_at'] = self._get_chinese_date(dt)
            except:
                result['handle_at_chinese'] = handle_at
                result['中文_handle_at'] = handle_at
        else:
            result['handle_at_chinese'] = ''
            result['中文_handle_at'] = ''
        
        return result
    
    def _get_chinese_date(self, date=None):
        """获取中文日期格式：二〇二六年一月一日"""
        if date is None:
            date = datetime.now()
        elif isinstance(date, str):
            date = datetime.strptime(date.split()[0], '%Y-%m-%d')
        
        chinese_nums = {
            '0': '〇', '1': '一', '2': '二', '3': '三', '4': '四',
            '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
        }
        
        # 年份：直接替换数字
        year_str = ''.join(chinese_nums.get(c, c) for c in str(date.year))
        
        # 月份转换
        month = date.month
        month_map = {
            1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
            6: '六', 7: '七', 8: '八', 9: '九', 10: '十',
            11: '十一', 12: '十二'
        }
        month_str = month_map.get(month, str(month))
        
        # 日期转换
        day = date.day
        if day <= 10:
            day_map = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
                      6: '六', 7: '七', 8: '八', 9: '九', 10: '十'}
            day_str = day_map.get(day, str(day))
        elif day < 20:
            # 11-19: 十一、十二...
            day_map = {11: '十一', 12: '十二', 13: '十三', 14: '十四', 15: '十五',
                      16: '十六', 17: '十七', 18: '十八', 19: '十九'}
            day_str = day_map.get(day, f'十{day - 10}')
        elif day == 20:
            day_str = '二十'
        elif day < 30:
            # 21-29
            day_map = {21: '二十一', 22: '二十二', 23: '二十三', 24: '二十四', 
                      25: '二十五', 26: '二十六', 27: '二十七', 28: '二十八', 
                      29: '二十九'}
            day_str = day_map.get(day, f'二十{day - 20}')
        elif day == 30:
            day_str = '三十'
        else:
            day_str = '三十一'
        
        return f"{year_str}年{month_str}月{day_str}日"


def generate_document(template_name, output_name, case_id):
    """
    生成单个文档
    """
    import requests
    
    # 获取案件详情
    response = requests.get(f'http://localhost:5000/api/handle/detail?id={case_id}')
    data = response.json()
    
    # 生成文档
    template_path = f'文件生成/1-立案/{template_name}'
    output_path = f'文件生成/1-立案/output/{output_name}'
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    generator = DocumentGenerator(template_path, output_path)
    generator.generate(data)
    
    print(f"文档已生成: {output_path}")
    return output_path


if __name__ == '__main__':
    # 测试生成
    # generate_document('（受理）立案审批表.docx', '测试输出.docx', '199966')
    
    # 测试中文日期
    gen = DocumentGenerator('文件生成/1-立案/变更仲裁申请受理通知书（申请人）.docx', '/tmp/test.docx')
    print("中文日期测试:", gen._get_chinese_date())
