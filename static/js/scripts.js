// API配置 - 使用相对路径，通过Web服务器代理访问
const API_BASE_URL = "/api";

// 全局数据存储
let formData = {
    receiptNumber: '',
    applicants: [],
    respondents: [],
    evidence: []
};

// 页面加载后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载保存的数据
    loadSavedData();

    // 初始化：如果没有数据，添加一个默认的申请人和被申请人
    if (formData.applicants.length === 0) {
        addApplicant();
    }
    if (formData.respondents.length === 0) {
        addRespondent();
    }
    if (formData.evidence.length === 0) {
        addEvidence();
    }

    // 添加申请人按钮
    document.getElementById('addApplicantBtn').addEventListener('click', function() {
        addApplicant();
    });

    // 添加被申请人按钮
    document.getElementById('addRespondentBtn').addEventListener('click', function() {
        addRespondent();
    });

    // 添加证据按钮
    document.getElementById('addEvidenceBtn').addEventListener('click', function() {
        addEvidence();
    });

    // 保存数据
    document.getElementById('saveBtn').addEventListener('click', saveData);

    // 重置表单
    document.getElementById('resetBtn').addEventListener('click', resetForm);

    // 打印功能
    document.getElementById('printBtn').addEventListener('click', printForm);

    // 预览功能
    document.getElementById('previewBtn').addEventListener('click', showPreview);
    document.getElementById('closePreviewBtn').addEventListener('click', closePreview);
    document.getElementById('closePreviewBtn2').addEventListener('click', closePreview);
    document.getElementById('printPreviewBtn').addEventListener('click', printPreview);

    // 委托事件处理
    document.addEventListener('click', function(e) {
        handleDelegatedEvents(e);
    });
});

// 处理委托事件
function handleDelegatedEvents(e) {
    // 删除申请人
    if (e.target.closest('.remove-applicant')) {
        const applicantItem = e.target.closest('.applicant-item');
        if (applicantItem) {
            const index = parseInt(applicantItem.dataset.index);
            removeApplicant(index);
        }
    }

    // 删除被申请人
    if (e.target.closest('.remove-respondent')) {
        const respondentItem = e.target.closest('.respondent-item');
        if (respondentItem) {
            const index = parseInt(respondentItem.dataset.index);
            removeRespondent(index);
        }
    }

    // 删除证据
    if (e.target.closest('.remove-evidence')) {
        const evidenceItem = e.target.closest('.evidence-item');
        if (evidenceItem) {
            const index = parseInt(evidenceItem.dataset.index);
            removeEvidence(index);
        }
    }

    // 添加申请人的仲裁请求
    if (e.target.closest('.add-applicant-request')) {
        const btn = e.target.closest('.add-applicant-request');
        const applicantIndex = parseInt(btn.dataset.applicantIndex);
        addApplicantRequest(applicantIndex);
    }

    // 删除申请人的仲裁请求
    if (e.target.closest('.remove-applicant-request')) {
        const btn = e.target.closest('.remove-applicant-request');
        const applicantIndex = parseInt(btn.dataset.applicantIndex);
        const requestIndex = parseInt(btn.dataset.requestIndex);
        removeApplicantRequest(applicantIndex, requestIndex);
    }

    // 查询个人信息
    if (e.target.closest('.query-id-btn')) {
        const btn = e.target.closest('.query-id-btn');
        const index = parseInt(btn.dataset.applicantIndex);
        queryPersonalInfo(index);
    }

    // 查询企业信息
    if (e.target.closest('.query-company-btn')) {
        const btn = e.target.closest('.query-company-btn');
        const index = parseInt(btn.dataset.respondentIndex);
        queryCompanyInfo(index);
    }
}

// 添加申请人
function addApplicant() {
    const index = formData.applicants.length;
    const applicant = {
        name: '',
        gender: '',
        nation: '',
        birth: '',
        address: '',
        phone: '',
        idCard: '',
        // 入职信息
        employmentDate: '',
        workLocation: '',
        monthlySalary: '',
        // 仲裁请求列表（仅请求内容）
        requests: [''],
        // 事实与理由（申请人级别，只有一个）
        factsReasons: ''
    };
    formData.applicants.push(applicant);
    renderApplicant(index);
}

// 渲染申请人区块
function renderApplicant(index) {
    const container = document.getElementById('applicantsList');
    const applicant = formData.applicants[index];

    const applicantDiv = document.createElement('div');
    applicantDiv.className = 'applicant-item mb-6 p-4 border-2 border-blue-200 rounded-lg bg-blue-50 fade-in';
    applicantDiv.dataset.index = index;

    applicantDiv.innerHTML = `
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-blue-200">
            <h3 class="text-lg font-bold text-blue-800">
                <i class="fas fa-user mr-2"></i>申请人 ${index + 1}
            </h3>
            ${index > 0 ? `
            <button class="remove-applicant text-red-500 hover:text-red-700 no-print" title="删除此申请人">
                <i class="fas fa-trash-alt"></i>
            </button>
            ` : ''}
        </div>

        <!-- 基本信息 -->
        <div class="mb-4">
            <h4 class="text-sm font-bold text-gray-600 mb-2">基本信息</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">姓名</label>
                    <input type="text" class="applicant-name w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入姓名" value="${applicant.name}">
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">性别</label>
                    <select class="applicant-gender w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="" ${!applicant.gender ? 'selected' : ''}>请选择性别</option>
                        <option value="男" ${applicant.gender === '男' ? 'selected' : ''}>男</option>
                        <option value="女" ${applicant.gender === '女' ? 'selected' : ''}>女</option>
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">民族</label>
                    <input type="text" class="applicant-nation w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入民族" value="${applicant.nation}">
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">出生年月</label>
                    <input type="text" class="applicant-birth w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="格式：YYYY年MM月" value="${applicant.birth}">
                </div>
                <div class="md:col-span-2">
                    <label class="block text-gray-700 text-sm font-medium mb-1">住址</label>
                    <input type="text" class="applicant-address w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入详细住址" value="${applicant.address}">
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">联系电话</label>
                    <input type="tel" class="applicant-phone w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入联系电话" value="${applicant.phone}">
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">身份证号码</label>
                    <div class="flex gap-2">
                        <input type="text" class="applicant-idcard flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入身份证号码" value="${applicant.idCard}">
                        <button type="button" class="query-id-btn bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-3 rounded-lg transition duration-300 whitespace-nowrap no-print" data-applicant-index="${index}">
                            <i class="fas fa-search mr-1"></i>查询
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 入职信息 -->
        <div class="mb-4">
            <h4 class="text-sm font-bold text-gray-600 mb-2">入职信息</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">入职时间</label>
                    <input type="text" class="applicant-employment-date w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="格式：YYYY年MM月" value="${applicant.employmentDate}">
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">工作地点（公司）</label>
                    <input type="text" class="applicant-work-location w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入工作地点" value="${applicant.workLocation}">
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-medium mb-1">月工资</label>
                    <input type="text" class="applicant-salary w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入月工资数额" value="${applicant.monthlySalary}">
                </div>
            </div>
        </div>

        <!-- 仲裁请求 -->
        <div class="mb-4">
            <div class="flex justify-between items-center mb-2">
                <h4 class="text-sm font-bold text-gray-600">仲裁请求</h4>
                <button class="add-applicant-request bg-blue-100 hover:bg-blue-200 text-blue-700 text-sm font-medium py-1 px-3 rounded transition duration-300 no-print" data-applicant-index="${index}">
                    <i class="fas fa-plus mr-1"></i>添加请求
                </button>
            </div>
            <div class="applicant-requests-list">
                ${applicant.requests.map((req, reqIndex) => `
                    <div class="request-item mb-2 p-3 border border-gray-300 rounded-lg bg-white" data-request-index="${reqIndex}">
                        <div class="flex justify-between items-center mb-2">
                            <span class="font-medium text-blue-600 text-sm">请求 ${reqIndex + 1}</span>
                            ${reqIndex > 0 ? `
                            <button class="remove-applicant-request text-red-500 hover:text-red-700 text-sm no-print" data-applicant-index="${index}" data-request-index="${reqIndex}">
                                <i class="fas fa-times"></i>
                            </button>
                            ` : ''}
                        </div>
                        <div>
                            <label class="block text-gray-700 text-xs font-medium mb-1">仲裁请求内容</label>
                            <textarea class="request-content w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" rows="2" placeholder="请具体明确地填写仲裁请求，例如：请求裁决被申请人支付拖欠的工资XXXX元。">${req}</textarea>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- 事实与理由（申请人级别，只有一个） -->
        <div class="mb-2">
            <h4 class="text-sm font-bold text-gray-600 mb-2">事实与理由</h4>
            <div class="p-3 border border-gray-300 rounded-lg bg-white">
                <textarea class="applicant-facts-reasons w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" rows="4" placeholder="请简明扼要叙述申请人提出上述仲裁请求的事实依据和法律理由，包括入职时间、工作地点、工资情况、争议经过等。">${applicant.factsReasons}</textarea>
            </div>
        </div>
    `;

    container.appendChild(applicantDiv);
}

// 删除申请人
function removeApplicant(index) {
    if (formData.applicants.length <= 1) {
        alert('至少需要一个申请人！');
        return;
    }
    if (!confirm(`确定要删除申请人 ${index + 1} 吗？`)) {
        return;
    }
    formData.applicants.splice(index, 1);
    refreshApplicantsList();
}

// 刷新申请人列表
function refreshApplicantsList() {
    const container = document.getElementById('applicantsList');
    container.innerHTML = '';
    formData.applicants.forEach((applicant, index) => {
        renderApplicant(index);
    });
}

// 添加申请人的仲裁请求
function addApplicantRequest(applicantIndex) {
    const applicant = formData.applicants[applicantIndex];
    applicant.requests.push('');

    // 重新渲染该申请人的区块
    refreshApplicantsList();
}

// 删除申请人的仲裁请求
function removeApplicantRequest(applicantIndex, requestIndex) {
    const applicant = formData.applicants[applicantIndex];
    if (applicant.requests.length <= 1) {
        alert('每个申请人至少需要一个仲裁请求！');
        return;
    }
    applicant.requests.splice(requestIndex, 1);
    refreshApplicantsList();
}

// 添加被申请人
function addRespondent() {
    const index = formData.respondents.length;
    const respondent = {
        name: '',
        legalPerson: '',
        position: '',
        address: '',
        phone: '',
        code: ''
    };
    formData.respondents.push(respondent);
    renderRespondent(index);
}

// 渲染被申请人区块
function renderRespondent(index) {
    const container = document.getElementById('respondentsList');
    const respondent = formData.respondents[index];

    const respondentDiv = document.createElement('div');
    respondentDiv.className = 'respondent-item mb-4 p-4 border-2 border-orange-200 rounded-lg bg-orange-50 fade-in';
    respondentDiv.dataset.index = index;

    respondentDiv.innerHTML = `
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-orange-200">
            <h3 class="text-lg font-bold text-orange-800">
                <i class="fas fa-building mr-2"></i>被申请人 ${index + 1}
            </h3>
            ${index > 0 ? `
            <button class="remove-respondent text-red-500 hover:text-red-700 no-print" title="删除此被申请人">
                <i class="fas fa-trash-alt"></i>
            </button>
            ` : ''}
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
                <label class="block text-gray-700 text-sm font-medium mb-1">单位名称</label>
                <div class="flex gap-2">
                    <input type="text" class="respondent-name flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入用人单位全称" value="${respondent.name}">
                    <button type="button" class="query-company-btn bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-3 rounded-lg transition duration-300 whitespace-nowrap no-print" data-respondent-index="${index}">
                        <i class="fas fa-search mr-1"></i>查询
                    </button>
                </div>
            </div>
            <div>
                <label class="block text-gray-700 text-sm font-medium mb-1">法定代表人</label>
                <input type="text" class="respondent-legal-person w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入法定代表人姓名" value="${respondent.legalPerson}">
            </div>
            <div>
                <label class="block text-gray-700 text-sm font-medium mb-1">职务</label>
                <input type="text" class="respondent-position w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入法定代表人职务" value="${respondent.position}">
            </div>
            <div class="md:col-span-2">
                <label class="block text-gray-700 text-sm font-medium mb-1">住所</label>
                <input type="text" class="respondent-address w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入用人单位地址" value="${respondent.address}">
            </div>
            <div>
                <label class="block text-gray-700 text-sm font-medium mb-1">联系电话</label>
                <input type="tel" class="respondent-phone w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入用人单位联系电话" value="${respondent.phone}">
            </div>
            <div>
                <label class="block text-gray-700 text-sm font-medium mb-1">统一社会信用代码</label>
                <input type="text" class="respondent-code w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="请输入统一社会信用代码" value="${respondent.code}">
            </div>
        </div>
    `;

    container.appendChild(respondentDiv);
}

// 删除被申请人
function removeRespondent(index) {
    if (formData.respondents.length <= 1) {
        alert('至少需要一个被申请人！');
        return;
    }
    if (!confirm(`确定要删除被申请人 ${index + 1} 吗？`)) {
        return;
    }
    formData.respondents.splice(index, 1);
    refreshRespondentsList();
}

// 刷新被申请人列表
function refreshRespondentsList() {
    const container = document.getElementById('respondentsList');
    container.innerHTML = '';
    formData.respondents.forEach((respondent, index) => {
        renderRespondent(index);
    });
}

// 数字转中文大写
function toChineseNumber(num) {
    const chineseNums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
    if (num <= 10) {
        return chineseNums[num - 1];
    } else if (num < 20) {
        return '十' + (num % 10 === 0 ? '' : chineseNums[num % 10 - 1]);
    } else if (num < 100) {
        const tens = Math.floor(num / 10);
        const ones = num % 10;
        return chineseNums[tens - 1] + '十' + (ones === 0 ? '' : chineseNums[ones - 1]);
    }
    return num.toString();
}

// 添加证据
function addEvidence() {
    const index = formData.evidence.length;
    const evidence = {
        name: '',
        source: '',
        purpose: '',
        pageRange: ''
    };
    formData.evidence.push(evidence);
    renderEvidence(index);
}

// 渲染证据区块
function renderEvidence(index) {
    const container = document.getElementById('evidenceList');
    const evidence = formData.evidence[index];

    // 解析页码
    let pageStart = '';
    let pageEnd = '';
    if (evidence.pageRange) {
        // 兼容旧格式 [1]-[5] 和新格式 1-5
        const cleanRange = evidence.pageRange.replace(/[\[\]]/g, '');
        const parts = cleanRange.split('-');
        if (parts.length >= 1) {
            pageStart = parts[0];
        }
        if (parts.length >= 2) {
            pageEnd = parts[1];
        }
    }

    const evidenceDiv = document.createElement('div');
    evidenceDiv.className = 'evidence-item mb-4 p-4 border border-gray-300 rounded-lg fade-in';
    evidenceDiv.dataset.index = index;

    evidenceDiv.innerHTML = `
        <div class="flex justify-between items-center mb-2">
            <span class="font-medium text-blue-600">证据${toChineseNumber(index + 1)}</span>
            ${index > 0 ? `
            <button class="remove-evidence text-red-500 hover:text-red-700 no-print" title="删除此证据">
                <i class="fas fa-times"></i>
            </button>
            ` : ''}
        </div>
        <div class="flex flex-wrap gap-3 items-end">
            <div style="width: 250px">
                <label class="block text-gray-700 text-sm font-medium mb-1">证据名称</label>
                <input type="text" class="evidence-name w-full px-2 py-2 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm" placeholder="如：劳动合同" value="${evidence.name}">
            </div>
            <div style="width: 250px">
                <label class="block text-gray-700 text-sm font-medium mb-1">证据来源</label>
                <input type="text" class="evidence-source w-full px-2 py-2 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm" placeholder="如：申请人提供" value="${evidence.source}">
            </div>
            <div style="width: 250px">
                <label class="block text-gray-700 text-sm font-medium mb-1">证明内容</label>
                <input type="text" class="evidence-purpose w-full px-2 py-2 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm" placeholder="如：证明劳动关系" value="${evidence.purpose}">
            </div>
            <div class="w-auto">
                <label class="block text-gray-700 text-sm font-medium mb-1">页码</label>
                <div class="flex items-center gap-1">
                    <input type="text" class="evidence-page-start w-10 px-1 py-2 border border-gray-300 rounded text-center focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm" placeholder="1" value="${pageStart}">
                    <span class="text-gray-500">-</span>
                    <input type="text" class="evidence-page-end w-10 px-1 py-2 border border-gray-300 rounded text-center focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm" placeholder="5" value="${pageEnd}">
                </div>
            </div>
        </div>
    `;

    container.appendChild(evidenceDiv);
}

// 删除证据
function removeEvidence(index) {
    if (formData.evidence.length <= 1) {
        alert('至少需要一个证据！');
        return;
    }
    if (!confirm(`确定要删除证据${toChineseNumber(index + 1)}吗？`)) {
        return;
    }
    formData.evidence.splice(index, 1);
    refreshEvidenceList();
}

// 刷新证据列表
function refreshEvidenceList() {
    const container = document.getElementById('evidenceList');
    container.innerHTML = '';
    formData.evidence.forEach((evidence, index) => {
        renderEvidence(index);
    });
}

// 从DOM收集数据
function collectDataFromDOM() {
    // 收集收件编号
    const receiptInput = document.getElementById('receiptNumber');
    if (receiptInput) {
        formData.receiptNumber = receiptInput.value.trim();
    }
    
    // 收集申请人数据
    formData.applicants = [];
    document.querySelectorAll('.applicant-item').forEach((item, index) => {
        const applicant = {
            name: item.querySelector('.applicant-name').value,
            gender: item.querySelector('.applicant-gender').value,
            nation: item.querySelector('.applicant-nation').value,
            birth: item.querySelector('.applicant-birth').value,
            address: item.querySelector('.applicant-address').value,
            phone: item.querySelector('.applicant-phone').value,
            idCard: item.querySelector('.applicant-idcard').value,
            employmentDate: item.querySelector('.applicant-employment-date').value,
            workLocation: item.querySelector('.applicant-work-location').value,
            monthlySalary: item.querySelector('.applicant-salary').value,
            requests: []
        };

        // 收集该申请人的仲裁请求（仅内容）
        item.querySelectorAll('.request-item').forEach(reqItem => {
            applicant.requests.push(reqItem.querySelector('.request-content').value);
        });

        // 收集该申请人的事实与理由（申请人级别）
        applicant.factsReasons = item.querySelector('.applicant-facts-reasons').value;

        formData.applicants.push(applicant);
    });

    // 收集被申请人数据
    formData.respondents = [];
    document.querySelectorAll('.respondent-item').forEach(item => {
        formData.respondents.push({
            name: item.querySelector('.respondent-name').value,
            legalPerson: item.querySelector('.respondent-legal-person').value,
            position: item.querySelector('.respondent-position').value,
            address: item.querySelector('.respondent-address').value,
            phone: item.querySelector('.respondent-phone').value,
            code: item.querySelector('.respondent-code').value
        });
    });

    // 收集证据数据
    formData.evidence = [];
    document.querySelectorAll('.evidence-item').forEach(item => {
        const pageStart = item.querySelector('.evidence-page-start').value.trim();
        const pageEnd = item.querySelector('.evidence-page-end').value.trim();
        let pageRange = '';
        if (pageStart && pageEnd) {
            pageRange = `${pageStart}-${pageEnd}`;
        } else if (pageStart) {
            pageRange = pageStart;
        } else if (pageEnd) {
            pageRange = pageEnd;
        }
        formData.evidence.push({
            name: item.querySelector('.evidence-name').value,
            source: item.querySelector('.evidence-source').value,
            purpose: item.querySelector('.evidence-purpose').value,
            pageRange: pageRange
        });
    });
}

// 保存数据到本地存储和数据库
async function saveData() {
    // 检查收件编号
    const receiptInput = document.getElementById('receiptNumber');
    const receiptNumber = receiptInput ? receiptInput.value.trim() : '';
    
    if (!receiptNumber) {
        alert('请先填写收件编号！');
        receiptInput.focus();
        return;
    }
    
    collectDataFromDOM();
    
    // 1. 保存到本地存储
    localStorage.setItem('laborArbitrationFormData', JSON.stringify(formData));
    
    // 2. 保存到数据库
    try {
        const saveBtn = document.getElementById('saveBtn');
        const originalText = saveBtn.innerHTML;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>保存中...';
        saveBtn.disabled = true;
        
        // 转换数据格式以匹配后端API
        const apiData = {
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
                page_range: evi.pageRange,
                applicant_id: null  // 证据暂时不关联特定申请人
            }))
        };
        
        const response = await fetch(`${API_BASE_URL}/cases/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(apiData)
        });
        
        const result = await response.json();
        
        // 显示当前收件编号
        document.getElementById('currentReceiptNumber').textContent = formData.receiptNumber;
        document.getElementById('receiptNumberDisplay').style.display = 'inline';
        
        if (result.success) {
            alert('数据保存成功！收件编号：' + formData.receiptNumber);
        } else {
            alert('数据保存到数据库失败：' + (result.error || '未知错误') + '\n\n数据已保存到本地浏览器。');
        }
    } catch (error) {
        console.error('保存数据时出错:', error);
        alert('网络错误，数据已保存到本地浏览器，但未能保存到服务器。\n\n请检查网络连接或联系管理员。');
    } finally {
        // 恢复按钮状态
        const saveBtn = document.getElementById('saveBtn');
        saveBtn.innerHTML = '<i class="fas fa-save mr-2"></i>保存数据';
        saveBtn.disabled = false;
    }
}

// 从本地存储加载数据
function loadSavedData() {
    const savedData = localStorage.getItem('laborArbitrationFormData');
    if (!savedData) return;

    try {
        formData = JSON.parse(savedData);

        // 数据格式兼容性处理：将旧格式转换为新格式
        if (formData.applicants) {
            formData.applicants.forEach(applicant => {
                // 处理 requests：如果是对象数组（旧格式），转换为字符串数组
                if (applicant.requests && applicant.requests.length > 0) {
                    if (typeof applicant.requests[0] === 'object' && applicant.requests[0] !== null) {
                        // 旧格式：requests 是 [{content, factsReasons}, ...]
                        const oldRequests = applicant.requests;
                        applicant.requests = oldRequests.map(req => req.content || '');

                        // 如果申请人没有 factsReasons，从第一个旧请求中提取
                        if (!applicant.factsReasons && oldRequests[0] && oldRequests[0].factsReasons) {
                            applicant.factsReasons = oldRequests[0].factsReasons;
                        }
                    }
                }

                // 确保 factsReasons 字段存在
                if (applicant.factsReasons === undefined) {
                    applicant.factsReasons = '';
                }

                // 确保 requests 是数组
                if (!applicant.requests || !Array.isArray(applicant.requests)) {
                    applicant.requests = [''];
                }
            });
        }

        // 证据数据兼容性处理：确保 pageRange 字段存在
        if (formData.evidence) {
            formData.evidence.forEach(evidence => {
                if (evidence.pageRange === undefined) {
                    evidence.pageRange = '';
                }
            });
        }

        // 渲染申请人
        if (formData.applicants && formData.applicants.length > 0) {
            formData.applicants.forEach((applicant, index) => {
                renderApplicant(index);
            });
        }

        // 渲染被申请人
        if (formData.respondents && formData.respondents.length > 0) {
            formData.respondents.forEach((respondent, index) => {
                renderRespondent(index);
            });
        }

        // 渲染证据
        if (formData.evidence && formData.evidence.length > 0) {
            formData.evidence.forEach((evidence, index) => {
                renderEvidence(index);
            });
        }
        
        // 加载收件编号
        if (formData.receiptNumber) {
            const receiptInput = document.getElementById('receiptNumber');
            if (receiptInput) {
                receiptInput.value = formData.receiptNumber;
            }
            document.getElementById('currentReceiptNumber').textContent = formData.receiptNumber;
            document.getElementById('receiptNumberDisplay').style.display = 'inline';
        }
    } catch (e) {
        console.error('加载保存的数据时出错:', e);
    }
}

// 重置表单
function resetForm() {
    if (confirm('确定要重置所有表单数据吗？这将清除所有已填写的内容。')) {
        localStorage.removeItem('laborArbitrationFormData');

        // 清空容器
        document.getElementById('applicantsList').innerHTML = '';
        document.getElementById('respondentsList').innerHTML = '';
        document.getElementById('evidenceList').innerHTML = '';
        
        // 清空收件编号
        const receiptInput = document.getElementById('receiptNumber');
        if (receiptInput) {
            receiptInput.value = '';
        }
        document.getElementById('receiptNumberDisplay').style.display = 'none';

        // 重置数据
        formData = {
            receiptNumber: '',
            applicants: [],
            respondents: [],
            evidence: []
        };

        // 添加默认值
        addApplicant();
        addRespondent();
        addEvidence();

        alert('表单已重置！');
    }
}

// 打印表单
function printForm() {
    collectDataFromDOM();
    populatePrintContent();
    window.print();
}

// 填充打印版内容
function populatePrintContent() {
    // 申请人信息
    const printApplicants = document.getElementById('print-applicants');
    printApplicants.innerHTML = '';

    formData.applicants.forEach((applicant, index) => {
        const applicantDiv = document.createElement('div');
        applicantDiv.className = 'mb-8';

        // 仲裁请求列表
        let requestsHtml = '';
        applicant.requests.forEach((req, reqIndex) => {
            requestsHtml += `
                <div class="mb-2">
                    <p><strong>仲裁请求 ${reqIndex + 1}：</strong>${req || '未填写'}</p>
                </div>
            `;
        });

        applicantDiv.innerHTML = `
            <h2 class="text-xl font-bold border-b border-black pb-2 mb-4">申请人 ${index + 1} 信息</h2>
            <div class="grid grid-cols-2 gap-4 mb-2">
                <div><strong>姓名：</strong>${applicant.name || ''}</div>
                <div><strong>性别：</strong>${applicant.gender || ''}</div>
                <div><strong>民族：</strong>${applicant.nation || ''}</div>
                <div><strong>出生年月：</strong>${applicant.birth || ''}</div>
                <div class="col-span-2"><strong>住址：</strong>${applicant.address || ''}</div>
                <div><strong>联系电话：</strong>${applicant.phone || ''}</div>
                <div><strong>身份证号码：</strong>${applicant.idCard || ''}</div>
            </div>
            <div class="mt-4 mb-4 p-3 bg-gray-50">
                <h3 class="font-bold mb-2">入职信息</h3>
                <div class="grid grid-cols-3 gap-4">
                    <div><strong>入职时间：</strong>${applicant.employmentDate || ''}</div>
                    <div><strong>工作地点：</strong>${applicant.workLocation || ''}</div>
                    <div><strong>月工资：</strong>${applicant.monthlySalary || ''}</div>
                </div>
            </div>
            <div class="mb-4">
                <h3 class="font-bold mb-2">仲裁请求</h3>
                ${requestsHtml}
            </div>
            <div class="mb-4">
                <h3 class="font-bold mb-2">事实与理由</h3>
                <p style="text-indent: 2em;">${applicant.factsReasons || '未填写'}</p>
            </div>
        `;
        printApplicants.appendChild(applicantDiv);
    });

    // 被申请人信息
    const printRespondents = document.getElementById('print-respondents');
    printRespondents.innerHTML = '';

    if (formData.respondents.length > 0) {
        const respondentsTitle = document.createElement('h2');
        respondentsTitle.className = 'text-xl font-bold border-b border-black pb-2 mb-4';
        respondentsTitle.textContent = '被申请人信息';
        printRespondents.appendChild(respondentsTitle);

        formData.respondents.forEach((respondent, index) => {
            const respondentDiv = document.createElement('div');
            respondentDiv.className = 'mb-4';
            respondentDiv.innerHTML = `
                <h3 class="font-bold mb-2">被申请人 ${index + 1}</h3>
                <div class="grid grid-cols-2 gap-4 mb-2">
                    <div class="col-span-2"><strong>单位名称：</strong>${respondent.name || ''}</div>
                    <div><strong>法定代表人：</strong>${respondent.legalPerson || ''}</div>
                    <div><strong>职务：</strong>${respondent.position || ''}</div>
                    <div class="col-span-2"><strong>住所：</strong>${respondent.address || ''}</div>
                    <div><strong>联系电话：</strong>${respondent.phone || ''}</div>
                    <div><strong>统一社会信用代码：</strong>${respondent.code || ''}</div>
                </div>
            `;
            printRespondents.appendChild(respondentDiv);
        });
    }

    // 证据清单
    const printEvidence = document.getElementById('print-evidence');
    printEvidence.innerHTML = '';

    if (formData.evidence.length > 0) {
        const evidenceTitle = document.createElement('h2');
        evidenceTitle.className = 'text-xl font-bold border-b border-black pb-2 mb-4';
        evidenceTitle.textContent = '证据清单';
        printEvidence.appendChild(evidenceTitle);

        const table = document.createElement('table');
        table.className = 'w-full border border-black';
        table.innerHTML = `
            <thead>
                <tr class="bg-gray-100">
                    <th class="border border-black p-2">序号</th>
                    <th class="border border-black p-2">证据名称</th>
                    <th class="border border-black p-2">证据来源</th>
                    <th class="border border-black p-2">证明内容</th>
                    <th class="border border-black p-2">页码</th>
                </tr>
            </thead>
            <tbody>
                ${formData.evidence.map((ev, idx) => `
                    <tr>
                        <td class="border border-black p-2 text-center">${toChineseNumber(idx + 1)}</td>
                        <td class="border border-black p-2">${ev.name || ''}</td>
                        <td class="border border-black p-2">${ev.source || ''}</td>
                        <td class="border border-black p-2">${ev.purpose || ''}</td>
                        <td class="border border-black p-2 text-center">${ev.pageRange || ''}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        printEvidence.appendChild(table);
    }
}

// 显示预览
function showPreview() {
    collectDataFromDOM();
    const previewContent = document.getElementById('previewContent');
    previewContent.innerHTML = '';

    let previewHTML = `
        <div class="mb-8">
            <h2 class="text-2xl font-bold text-center mb-6">劳动仲裁申请书</h2>
    `;

    // 申请人信息
    formData.applicants.forEach((applicant, index) => {
        previewHTML += `
            <div class="mb-6">
                <h3 class="text-lg font-bold border-b border-gray-300 pb-2 mb-4">申请人 ${index + 1} 信息</h3>
                <div class="grid grid-cols-2 gap-4 mb-2">
                    <div><strong>姓名：</strong>${applicant.name || '未填写'}</div>
                    <div><strong>性别：</strong>${applicant.gender || '未填写'}</div>
                    <div><strong>民族：</strong>${applicant.nation || '未填写'}</div>
                    <div><strong>出生年月：</strong>${applicant.birth || '未填写'}</div>
                    <div class="col-span-2"><strong>住址：</strong>${applicant.address || '未填写'}</div>
                    <div><strong>联系电话：</strong>${applicant.phone || '未填写'}</div>
                    <div><strong>身份证号码：</strong>${applicant.idCard || '未填写'}</div>
                </div>
                <div class="mt-4 mb-4 p-3 bg-gray-50 rounded">
                    <h4 class="font-bold mb-2">入职信息</h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div><strong>入职时间：</strong>${applicant.employmentDate || '未填写'}</div>
                        <div><strong>工作地点：</strong>${applicant.workLocation || '未填写'}</div>
                        <div><strong>月工资：</strong>${applicant.monthlySalary || '未填写'}</div>
                    </div>
                </div>
                <div class="mb-4">
                    <h4 class="font-bold mb-2">仲裁请求</h4>
        `;

        applicant.requests.forEach((req, reqIndex) => {
            previewHTML += `
                <div class="mb-2 p-3 bg-gray-50 rounded">
                    <p><strong>请求 ${reqIndex + 1}：</strong>${req || '未填写'}</p>
                </div>
            `;
        });

        previewHTML += `
                </div>
                <div class="mb-4">
                    <h4 class="font-bold mb-2">事实与理由</h4>
                    <div class="p-3 bg-gray-50 rounded">
                        <p style="text-indent: 2em;">${applicant.factsReasons || '未填写'}</p>
                    </div>
                </div>
            </div>
        `;
    });

    // 被申请人信息
    if (formData.respondents.length > 0) {
        previewHTML += `
            <div class="mb-6">
                <h3 class="text-lg font-bold border-b border-gray-300 pb-2 mb-4">被申请人信息</h3>
        `;

        formData.respondents.forEach((respondent, index) => {
            previewHTML += `
                <div class="mb-4 ${index > 0 ? 'border-t border-gray-200 pt-4' : ''}">
                    <h4 class="font-bold mb-2">被申请人 ${index + 1}</h4>
                    <div class="grid grid-cols-2 gap-4 mb-2">
                        <div class="col-span-2"><strong>单位名称：</strong>${respondent.name || '未填写'}</div>
                        <div><strong>法定代表人：</strong>${respondent.legalPerson || '未填写'}</div>
                        <div><strong>职务：</strong>${respondent.position || '未填写'}</div>
                        <div class="col-span-2"><strong>住所：</strong>${respondent.address || '未填写'}</div>
                        <div><strong>联系电话：</strong>${respondent.phone || '未填写'}</div>
                        <div><strong>统一社会信用代码：</strong>${respondent.code || '未填写'}</div>
                    </div>
                </div>
            `;
        });

        previewHTML += `</div>`;
    }

    // 证据清单
    if (formData.evidence.length > 0) {
        previewHTML += `
            <div class="mb-6">
                <h3 class="text-lg font-bold border-b border-gray-300 pb-2 mb-4">证据清单</h3>
                <table class="w-full border border-gray-300">
                    <thead>
                        <tr class="bg-gray-100">
                            <th class="border border-gray-300 p-2">序号</th>
                            <th class="border border-gray-300 p-2">证据名称</th>
                            <th class="border border-gray-300 p-2">证据来源</th>
                            <th class="border border-gray-300 p-2">证明内容</th>
                            <th class="border border-gray-300 p-2">页码</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${formData.evidence.map((ev, idx) => `
                            <tr>
                                <td class="border border-gray-300 p-2 text-center">${toChineseNumber(idx + 1)}</td>
                                <td class="border border-gray-300 p-2">${ev.name || ''}</td>
                                <td class="border border-gray-300 p-2">${ev.source || ''}</td>
                                <td class="border border-gray-300 p-2">${ev.purpose || ''}</td>
                                <td class="border border-gray-300 p-2 text-center">${ev.pageRange || ''}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    previewHTML += `
            <div class="mt-12">
                <div class="text-right mb-8">
                    <p><strong>申请人（签名或盖章）：</strong></p>
                    <p class="mt-10">年&emsp;月&emsp;日</p>
                </div>
                <div class="mt-16">
                    <h3 class="text-xl font-bold text-center">此致</h3>
                    <h3 class="text-xl font-bold text-center mt-6">永安市劳动人事争议仲裁委员会</h3>
                </div>
            </div>
        </div>
    `;

    previewContent.innerHTML = previewHTML;
    document.getElementById('previewModal').classList.remove('hidden');
}

// 关闭预览
function closePreview() {
    document.getElementById('previewModal').classList.add('hidden');
}

// 打印预览版
function printPreview() {
    closePreview();
    setTimeout(() => {
        printForm();
    }, 300);
}

// 查询个人身份信息
async function queryPersonalInfo(applicantIndex) {
    const applicantItem = document.querySelector(`.applicant-item[data-index="${applicantIndex}"]`);
    const idNumber = applicantItem.querySelector('.applicant-idcard').value.trim();

    if (!idNumber) {
        alert('请输入身份证号码');
        return;
    }

    // 验证身份证格式（简单验证）
    if (!/^\d{17}[\dXx]$/.test(idNumber)) {
        alert('身份证号码格式不正确，请输入18位身份证号码');
        return;
    }

    const queryBtn = applicantItem.querySelector('.query-id-btn');
    const originalText = queryBtn.innerHTML;

    try {
        // 显示加载状态
        queryBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>查询中...';
        queryBtn.disabled = true;

        // 调用API
        const response = await fetch(`${API_BASE_URL}/idcard/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                AAC147: idNumber
            })
        });

        const result = await response.json();

        if (result.code === 200 && result.data && result.data.data && result.data.data.length > 0) {
            // 填充个人信息
            fillPersonalInfo(applicantItem, result.data.data[0]);
            alert('个人信息查询成功！');
        } else {
            alert(`查询失败：${result.message || '未找到匹配的个人信息'}`);
        }
    } catch (error) {
        console.error('查询个人身份信息时出错:', error);
        alert('网络错误，请检查API服务是否正常');
    } finally {
        // 恢复按钮状态
        queryBtn.innerHTML = originalText;
        queryBtn.disabled = false;
    }
}

// 填充个人信息
function fillPersonalInfo(applicantItem, personData) {
    if (personData.AAC003) {
        applicantItem.querySelector('.applicant-name').value = personData.AAC003;
    }
    if (personData.AAC004) {
        applicantItem.querySelector('.applicant-gender').value = personData.AAC004;
    }
    if (personData.AAC005) {
        applicantItem.querySelector('.applicant-nation').value = personData.AAC005;
    }
    if (personData.AAC006) {
        // 转换日期格式：YYYY-MM-DD 转换为 YYYY年MM月
        const birthDate = new Date(personData.AAC006);
        if (!isNaN(birthDate.getTime())) {
            const year = birthDate.getFullYear();
            const month = birthDate.getMonth() + 1;
            applicantItem.querySelector('.applicant-birth').value = `${year}年${month.toString().padStart(2, '0')}月`;
        }
    }
    if (personData.AAE006) {
        applicantItem.querySelector('.applicant-address').value = personData.AAE006;
    }
}

// 查询企业信息
async function queryCompanyInfo(respondentIndex) {
    const respondentItem = document.querySelector(`.respondent-item[data-index="${respondentIndex}"]`);
    const companyName = respondentItem.querySelector('.respondent-name').value.trim();

    if (!companyName) {
        alert('请输入企业名称');
        return;
    }

    const queryBtn = respondentItem.querySelector('.query-company-btn');
    const originalText = queryBtn.innerHTML;

    try {
        // 显示加载状态
        queryBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>查询中...';
        queryBtn.disabled = true;

        // 调用API
        const response = await fetch(`${API_BASE_URL}/company/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                company_name: companyName,
                exact_match: true,
                format: true
            })
        });

        const result = await response.json();

        if (result.code === 200 && result.data && result.data.length > 0) {
            // 填充企业信息
            fillCompanyInfo(respondentItem, result.data[0]);
            alert('企业信息查询成功！');
        } else {
            alert(`查询失败：${result.message || '未找到匹配的企业信息'}`);
        }
    } catch (error) {
        console.error('查询企业信息时出错:', error);
        alert('网络错误，请检查API服务是否正常');
    } finally {
        // 恢复按钮状态
        queryBtn.innerHTML = originalText;
        queryBtn.disabled = false;
    }
}

// 填充企业信息
function fillCompanyInfo(respondentItem, companyData) {
    // 企业名称已经存在，不需要填充
    if (companyData['法人姓名']) {
        respondentItem.querySelector('.respondent-legal-person').value = companyData['法人姓名'];
    }
    if (companyData['注册地址']) {
        respondentItem.querySelector('.respondent-address').value = companyData['注册地址'];
    }
    if (companyData['公司电话']) {
        respondentItem.querySelector('.respondent-phone').value = companyData['公司电话'];
    }
    if (companyData['统一社会信用代码']) {
        respondentItem.querySelector('.respondent-code').value = companyData['统一社会信用代码'];
    }
}
