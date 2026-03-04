#!/usr/bin/env python3
"""
批量文档生成器 - 多选时独立生成每个文件并打包成 zip
文件名格式: [年份]号-模板文件名称.docx
例如: [2026]98-02案卷封面.xlsx
"""
import os
import re
import zipfile
import shutil
from datetime import datetime

# 导入原来的文档生成器
from document_generator import DocumentGenerator


class BatchDocumentGenerator:
    """批量文档生成器 - 独立生成模式"""
    
    def __init__(self, doc_templates_dir):
        self.doc_templates_dir = doc_templates_dir
    
    def generate_batch(self, template_paths, case_data, case_no):
        """
        批量生成文档 - 每个模板独立生成，然后打包成 zip
        
        Args:
            template_paths: 模板路径列表
            case_data: 案件数据（原始API返回数据）
            case_no: 案件编号（用于文件名）
        
        Returns:
            dict: {
                'zip': {'path': str, 'files': list},
            }
        """
        generated_files = []
        
        # 为每个模板生成独立文件
        for template_path in template_paths:
            full_path = os.path.join(self.doc_templates_dir, template_path)
            if not os.path.exists(full_path):
                print(f"模板不存在: {template_path}")
                continue
            
            # 生成输出文件名
            output_filename = self._generate_output_filename(case_no, template_path)
            output_path = os.path.join(self.doc_templates_dir, 'output', output_filename)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 使用 DocumentGenerator 生成
            generator = DocumentGenerator(full_path, output_path)
            generator.generate(case_data)
            
            generated_files.append(output_path)
            print(f"生成: {output_filename}")
        
        if not generated_files:
            raise ValueError("没有成功生成任何文件")
        
        # 打包成 zip
        zip_path = self._create_zip(generated_files, case_no)
        
        return {'zip': {'path': zip_path, 'files': generated_files}}
    
    def _generate_output_filename(self, case_no, template_path):
        """
        生成输出文件名
        格式: [年份]号-模板文件名称.docx
        例如: [2026]98-02案卷封面.xlsx
        """
        # 从案号提取年份和序号
        # 案号格式如: 永劳人仲案字（2026）98号 或 明永劳人仲案字[2026]98号
        year = ""
        number = ""
        
        # 去掉开头的"明"
        clean_case_no = str(case_no)
        if clean_case_no.startswith('明'):
            clean_case_no = clean_case_no[1:]
        
        # 尝试匹配年份和序号
        # 匹配 （2026）或 [2026] 格式
        year_match = re.search(r'[（\[](\d{4})[）\]]', clean_case_no)
        number_match = re.search(r'(\d+)号', clean_case_no)
        
        if year_match:
            year = year_match.group(1)
        if number_match:
            number = number_match.group(1)
        
        # 如果没有匹配到，使用时间戳
        if not year or not number:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            return f"[{timestamp}]-{os.path.basename(template_path)}"
        
        # 获取模板文件名（不含路径和扩展名）
        template_name = os.path.splitext(os.path.basename(template_path))[0]
        
        # 获取扩展名
        ext = os.path.splitext(template_path)[1]
        
        # 生成文件名: [2026]98-模板名称.docx
        filename = f"[{year}]{number}-{template_name}{ext}"
        
        # 清理非法字符
        filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
        
        return filename
    
    def _create_zip(self, file_paths, case_no):
        """
        将生成的文件打包成 zip
        
        Args:
            file_paths: 文件路径列表
            case_no: 案号（用于 zip 文件名）
        
        Returns:
            str: zip 文件路径
        """
        # 生成 zip 文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        clean_case_no = re.sub(r'[\\/:*?"<>|]', '_', str(case_no))
        zip_filename = f"{clean_case_no}-{timestamp}.zip"
        zip_path = os.path.join(self.doc_templates_dir, 'output', zip_filename)
        
        # 创建 zip
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    # 使用文件名作为 zip 内的路径
                    arcname = os.path.basename(file_path)
                    zf.write(file_path, arcname)
        
        print(f"打包完成: {zip_filename}")
        return zip_path


if __name__ == '__main__':
    # 测试代码
    import sys
    if len(sys.argv) > 1:
        generator = BatchDocumentGenerator('文件生成')
        # 测试数据（模拟API返回格式）
        test_data = {
            'case_no': '永劳人仲案字（2026）98号',
            'case_reason': '测试案由',
            'applicant_arr': [{'name': '测试申请人'}],
            'respondent_arr': [{'name': '测试被申请人'}]
        }
        result = generator.generate_batch(sys.argv[1:], test_data, '永劳人仲案字（2026）98号')
        print(f"生成结果: {result}")
