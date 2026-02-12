/**
 * 数据库 API 客户端
 * 用于将劳动仲裁申请书数据保存到 MySQL 数据库
 */

// API 基础地址
const DB_API_BASE_URL = "/api";

/**
 * 保存完整案件数据到数据库
 * @param {Object} formData 表单数据对象
 * @param {string} formData.receiptNumber 收件编号
 * @param {Array} formData.applicants 申请人数组
 * @param {Array} formData.respondents 被申请人数组
 * @param {Array} formData.evidence 证据数组
 * @returns {Promise<Object>} 保存结果
 */
async function saveCaseToDatabase(formData) {
    try {
        // 构建请求数据
        const requestData = {
            receipt_number: formData.receiptNumber,
            applicants: formData.applicants.map((app, index) => ({
                seq_no: index + 1,
                name: app.name,
                gender: app.gender,
                nation: app.nation,
                birth_date: app.birth,
                address: app.address,
                phone: app.phone,
                id_card: app.idCard,
                employment_date: app.employmentDate,
                work_location: app.workLocation,
                monthly_salary: app.monthlySalary,
                facts_reasons: app.factsReasons,
                requests: app.requests.map((req, reqIndex) => ({
                    seq_no: reqIndex + 1,
                    content: req
                }))
            })),
            respondents: formData.respondents.map((resp, index) => ({
                seq_no: index + 1,
                name: resp.name,
                legal_person: resp.legalPerson,
                position: resp.position,
                address: resp.address,
                phone: resp.phone,
                unified_code: resp.code
            })),
            evidence: formData.evidence.map((evi, index) => ({
                seq_no: index + 1,
                name: evi.name,
                source: evi.source,
                purpose: evi.purpose,
                page_range: evi.pageRange
            }))
        };

        // 发送请求到后端 API
        const response = await fetch(`${DB_API_BASE_URL}/cases/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return {
            success: true,
            caseId: result.case_id,
            message: '数据已保存到数据库'
        };
    } catch (error) {
        console.error('保存到数据库失败:', error);
        return {
            success: false,
            message: error.message || '保存失败'
        };
    }
}

/**
 * 根据收件编号查询案件
 * @param {string} receiptNumber 收件编号
 * @returns {Promise<Object>} 案件数据
 */
async function getCaseByReceiptNumber(receiptNumber) {
    try {
        const response = await fetch(
            `${DB_API_BASE_URL}/cases/query?receipt_number=${encodeURIComponent(receiptNumber)}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return {
            success: true,
            data: result
        };
    } catch (error) {
        console.error('查询案件失败:', error);
        return {
            success: false,
            message: error.message || '查询失败'
        };
    }
}

/**
 * 获取案件列表
 * @param {Object} params 查询参数
 * @param {number} params.page 页码
 * @param {number} params.pageSize 每页数量
 * @returns {Promise<Object>} 案件列表
 */
async function getCaseList(params = {}) {
    const { page = 1, pageSize = 10 } = params;
    
    try {
        const response = await fetch(
            `${DB_API_BASE_URL}/cases/list?page=${page}&page_size=${pageSize}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return {
            success: true,
            data: result
        };
    } catch (error) {
        console.error('获取案件列表失败:', error);
        return {
            success: false,
            message: error.message || '获取列表失败'
        };
    }
}

/**
 * 获取单个申请人的详细信息
 * @param {number} applicantId 申请人ID
 * @returns {Promise<Object>} 申请人详细信息
 */
async function getApplicantDetail(applicantId) {
    try {
        const response = await fetch(
            `${DB_API_BASE_URL}/applicants/${applicantId}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return {
            success: true,
            data: result
        };
    } catch (error) {
        console.error('获取申请人详情失败:', error);
        return {
            success: false,
            message: error.message || '获取详情失败'
        };
    }
}

/**
 * 获取案件的所有申请人
 * @param {number} caseId 案件ID
 * @returns {Promise<Object>} 申请人列表
 */
async function getApplicantsByCaseId(caseId) {
    try {
        const response = await fetch(
            `${DB_API_BASE_URL}/cases/${caseId}/applicants`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return {
            success: true,
            data: result
        };
    } catch (error) {
        console.error('获取申请人列表失败:', error);
        return {
            success: false,
            message: error.message || '获取列表失败'
        };
    }
}

/**
 * 获取案件的所有被申请人
 * @param {number} caseId 案件ID
 * @returns {Promise<Object>} 被申请人列表
 */
async function getRespondentsByCaseId(caseId) {
    try {
        const response = await fetch(
            `${DB_API_BASE_URL}/cases/${caseId}/respondents`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return {
            success: true,
            data: result
        };
    } catch (error) {
        console.error('获取被申请人列表失败:', error);
        return {
            success: false,
            message: error.message || '获取列表失败'
        };
    }
}

/**
 * 获取案件的所有证据
 * @param {number} caseId 案件ID
 * @returns {Promise<Object>} 证据列表
 */
async function getEvidenceByCaseId(caseId) {
    try {
        const response = await fetch(
            `${DB_API_BASE_URL}/cases/${caseId}/evidence`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return {
            success: true,
            data: result
        };
    } catch (error) {
        console.error('获取证据列表失败:', error);
        return {
            success: false,
            message: error.message || '获取列表失败'
        };
    }
}

/**
 * 获取申请人的仲裁请求
 * @param {number} applicantId 申请人ID
 * @returns {Promise<Object>} 仲裁请求列表
 */
async function getRequestsByApplicantId(applicantId) {
    try {
        const response = await fetch(
            `${DB_API_BASE_URL}/applicants/${applicantId}/requests`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return {
            success: true,
            data: result
        };
    } catch (error) {
        console.error('获取仲裁请求失败:', error);
        return {
            success: false,
            message: error.message || '获取请求失败'
        };
    }
}

/**
 * 删除案件
 * @param {number} caseId 案件ID
 * @returns {Promise<Object>} 删除结果
 */
async function deleteCase(caseId) {
    try {
        const response = await fetch(`${DB_API_BASE_URL}/cases/${caseId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return {
            success: true,
            message: '案件已删除'
        };
    } catch (error) {
        console.error('删除案件失败:', error);
        return {
            success: false,
            message: error.message || '删除失败'
        };
    }
}

/**
 * 修改后的保存函数（同时保存到本地和数据库）
 * 可以替换 scripts.js 中的 saveData 函数
 */
async function saveDataWithDatabase() {
    // 检查收件编号
    const receiptInput = document.getElementById('receiptNumber');
    const receiptNumber = receiptInput ? receiptInput.value.trim() : '';
    
    if (!receiptNumber) {
        alert('请先填写收件编号！');
        receiptInput.focus();
        return;
    }
    
    // 收集表单数据
    collectDataFromDOM();
    
    // 1. 保存到本地存储
    localStorage.setItem('laborArbitrationFormData', JSON.stringify(formData));
    
    // 2. 保存到数据库
    const dbResult = await saveCaseToDatabase(formData);
    
    // 显示当前收件编号
    document.getElementById('currentReceiptNumber').textContent = formData.receiptNumber;
    document.getElementById('receiptNumberDisplay').style.display = 'inline';
    
    if (dbResult.success) {
        alert(`数据已保存！\n收件编号：${formData.receiptNumber}\n数据库案件ID：${dbResult.caseId}`);
    } else {
        alert(`本地保存成功！\n收件编号：${formData.receiptNumber}\n数据库保存失败：${dbResult.message}`);
    }
}

// 导出函数供外部使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        saveCaseToDatabase,
        getCaseByReceiptNumber,
        getCaseList,
        getApplicantDetail,
        getApplicantsByCaseId,
        getRespondentsByCaseId,
        getEvidenceByCaseId,
        getRequestsByApplicantId,
        deleteCase,
        saveDataWithDatabase
    };
}
