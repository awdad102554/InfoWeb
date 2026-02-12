-- 劳动仲裁申请书数据库表结构
-- 创建时间: 2026-02-11
-- 说明: 存储劳动仲裁申请书相关数据，支持案件、申请人、被申请人、证据清单的关联查询

-- ============================================
-- 1. 案件主表 (cases)
-- 存储每个仲裁案件的基本信息，以收件编号为唯一标识
-- ============================================
CREATE TABLE IF NOT EXISTS cases (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    receipt_number VARCHAR(50) NOT NULL COMMENT '收件编号',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-删除, 1-正常',
    
    UNIQUE KEY uk_receipt_number (receipt_number),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='案件主表';


-- ============================================
-- 2. 申请人表 (applicants)
-- 存储每个案件的申请人信息，关联 cases 表
-- ============================================
CREATE TABLE IF NOT EXISTS applicants (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    case_id BIGINT UNSIGNED NOT NULL COMMENT '关联案件ID',
    seq_no INT UNSIGNED DEFAULT 1 COMMENT '申请人在本案件中的序号(第几个申请人)',
    
    -- 基本信息
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    gender VARCHAR(10) COMMENT '性别',
    nation VARCHAR(20) COMMENT '民族',
    birth_date VARCHAR(20) COMMENT '出生年月(格式: YYYY年MM月)',
    address TEXT COMMENT '住址',
    phone VARCHAR(20) COMMENT '联系电话',
    id_card VARCHAR(18) COMMENT '身份证号码',
    
    -- 入职信息
    employment_date VARCHAR(20) COMMENT '入职时间(格式: YYYY年MM月)',
    work_location VARCHAR(200) COMMENT '工作地点(公司)',
    monthly_salary VARCHAR(50) COMMENT '月工资',
    
    -- 事实与理由(申请人级别)
    facts_reasons TEXT COMMENT '事实与理由',
    
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    INDEX idx_case_id (case_id),
    INDEX idx_id_card (id_card),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='申请人表';


-- ============================================
-- 3. 仲裁请求表 (arbitration_requests)
-- 存储每个申请人的仲裁请求，关联 applicants 表
-- 一个申请人可以有多个仲裁请求
-- ============================================
CREATE TABLE IF NOT EXISTS arbitration_requests (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    applicant_id BIGINT UNSIGNED NOT NULL COMMENT '关联申请人ID',
    case_id BIGINT UNSIGNED NOT NULL COMMENT '关联案件ID(冗余字段,方便查询)',
    seq_no INT UNSIGNED DEFAULT 1 COMMENT '请求序号(第几个请求)',
    content TEXT NOT NULL COMMENT '仲裁请求内容',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (applicant_id) REFERENCES applicants(id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_case_id (case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='仲裁请求表';


-- ============================================
-- 4. 被申请人表 (respondents)
-- 存储每个案件的被申请人(用人单位)信息
-- ============================================
CREATE TABLE IF NOT EXISTS respondents (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    case_id BIGINT UNSIGNED NOT NULL COMMENT '关联案件ID',
    seq_no INT UNSIGNED DEFAULT 1 COMMENT '被申请人在本案件中的序号',
    
    name VARCHAR(200) NOT NULL COMMENT '单位名称',
    legal_person VARCHAR(50) COMMENT '法定代表人',
    position VARCHAR(50) COMMENT '职务',
    address TEXT COMMENT '住所',
    phone VARCHAR(20) COMMENT '联系电话',
    unified_code VARCHAR(50) COMMENT '统一社会信用代码',
    
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    INDEX idx_case_id (case_id),
    INDEX idx_unified_code (unified_code),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='被申请人表';


-- ============================================
-- 5. 证据清单表 (evidence)
-- 存储每个案件的证据信息
-- ============================================
CREATE TABLE IF NOT EXISTS evidence (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    case_id BIGINT UNSIGNED NOT NULL COMMENT '关联案件ID',
    applicant_id BIGINT UNSIGNED NULL COMMENT '关联申请人ID（谁提供的证据）',
    seq_no INT UNSIGNED DEFAULT 1 COMMENT '证据序号',
    
    name VARCHAR(200) NOT NULL COMMENT '证据名称',
    source VARCHAR(100) COMMENT '证据来源',
    purpose TEXT COMMENT '证明内容',
    page_start VARCHAR(10) COMMENT '起始页码',
    page_end VARCHAR(10) COMMENT '结束页码',
    page_range VARCHAR(50) COMMENT '页码范围(完整显示,如: 1-5)',
    
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (applicant_id) REFERENCES applicants(id) ON DELETE SET NULL,
    INDEX idx_case_id (case_id),
    INDEX idx_applicant_id (applicant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证据清单表';


-- ============================================
-- 常用查询示例
-- ============================================

-- 1. 根据收件编号查询完整案件信息(包括所有申请人、被申请人、证据)
-- SELECT * FROM cases WHERE receipt_number = '2025001';

-- 2. 查询某个案件的所有申请人信息
-- SELECT * FROM applicants WHERE case_id = 1 ORDER BY seq_no;

-- 3. 查询某个案件的所有被申请人信息
-- SELECT * FROM respondents WHERE case_id = 1 ORDER BY seq_no;

-- 4. 查询某个案件的所有证据清单
-- SELECT * FROM evidence WHERE case_id = 1 ORDER BY seq_no;

-- 5. 查询某个申请人的所有仲裁请求
-- SELECT * FROM arbitration_requests WHERE applicant_id = 1 ORDER BY seq_no;

-- 6. 查询某个案件的所有申请人及其仲裁请求(联合查询)
-- SELECT 
--     a.*,
--     GROUP_CONCAT(ar.content ORDER BY ar.seq_no SEPARATOR '; ') AS all_requests
-- FROM applicants a
-- LEFT JOIN arbitration_requests ar ON a.id = ar.applicant_id
-- WHERE a.case_id = 1
-- GROUP BY a.id;

-- 7. 查询完整案件视图(案件+申请人数量+被申请人数量+证据数量)
-- SELECT 
--     c.*,
--     COUNT(DISTINCT a.id) AS applicant_count,
--     COUNT(DISTINCT r.id) AS respondent_count,
--     COUNT(DISTINCT e.id) AS evidence_count
-- FROM cases c
-- LEFT JOIN applicants a ON c.id = a.case_id
-- LEFT JOIN respondents r ON c.id = r.case_id
-- LEFT JOIN evidence e ON c.id = e.case_id
-- WHERE c.receipt_number = '2025001'
-- GROUP BY c.id;
