const translations = {
    zh: {
        title: 'PDF 工具箱',
        langBtn: 'English',
        tabMerge: '合并',
        tabSplit: '拆分',
        tabExtract: '提取',
        tabRotate: '旋转',
        tabEncrypt: '加密',
        tabDecrypt: '解密',
        tabWatermark: '水印',
        mergeTitle: '合并 PDF',
        splitTitle: '拆分 PDF',
        extractTitle: '提取页面',
        rotateTitle: '旋转页面',
        encryptTitle: '加密 PDF',
        decryptTitle: '解密 PDF',
        watermarkTitle: '添加水印',
        uploadHint: '拖放文件到此处或 ',
        clickSelect: '点击选择',
        mergeBtn: '开始合并',
        splitBtn: '开始拆分',
        extractBtn: '开始提取',
        rotateBtn: '开始旋转',
        encryptBtn: '开始加密',
        decryptBtn: '开始解密',
        watermarkBtn: '添加水印',
        splitMode: '拆分方式：',
        splitSingle: '每页拆分',
        splitRange: '按范围拆分',
        splitRangeLabel: '页码范围（如：1-3,5,7-10）：',
        extractPagesLabel: '页码范围（如：1,3-5）：',
        rotateAngle: '旋转角度：',
        rotatePagesLabel: '页码范围（留空则全部旋转）：',
        encryptPassword: '设置密码：',
        encryptPasswordConfirm: '确认密码：',
        decryptPassword: '输入密码：',
        watermarkText: '水印文本：',
        watermarkSize: '字体大小：',
        watermarkAngle: '旋转角度：',
        watermarkPagesLabel: '页码范围（留空则全部添加）：',
        success: '操作成功！',
        error: '操作失败：',
        selectFile: '请先选择文件',
        selectOutput: '请选择输出路径',
        passwordMismatch: '两次密码不一致',
        passwordRequired: '请输入密码',
        passwordMinLength: '密码长度至少6位',
        invalidPages: '页码格式无效',
        filesSelected: '已选择 {count} 个文件',
        fileSelected: '已选择文件',
        processing: '处理中...',
        done: '完成！',
        downloadDone: '下载完成！',
        fileTooLarge: '文件过大，超过100MB限制',
        operationFailed: '操作失败，请重试'
    },
    en: {
        title: 'PDF Toolbox',
        langBtn: '中文',
        tabMerge: 'Merge',
        tabSplit: 'Split',
        tabExtract: 'Extract',
        tabRotate: 'Rotate',
        tabEncrypt: 'Encrypt',
        tabDecrypt: 'Decrypt',
        tabWatermark: 'Watermark',
        mergeTitle: 'Merge PDF',
        splitTitle: 'Split PDF',
        extractTitle: 'Extract Pages',
        rotateTitle: 'Rotate Pages',
        encryptTitle: 'Encrypt PDF',
        decryptTitle: 'Decrypt PDF',
        watermarkTitle: 'Add Watermark',
        uploadHint: 'Drag and drop files here or ',
        clickSelect: 'click to select',
        mergeBtn: 'Merge',
        splitBtn: 'Split',
        extractBtn: 'Extract',
        rotateBtn: 'Rotate',
        encryptBtn: 'Encrypt',
        decryptBtn: 'Decrypt',
        watermarkBtn: 'Add Watermark',
        splitMode: 'Split mode:',
        splitSingle: 'Single page',
        splitRange: 'Page range',
        splitRangeLabel: 'Page range (e.g. 1-3,5,7-10):',
        extractPagesLabel: 'Page range (e.g. 1,3-5):',
        rotateAngle: 'Rotation angle:',
        rotatePagesLabel: 'Page range (empty for all):',
        encryptPassword: 'Set password:',
        encryptPasswordConfirm: 'Confirm password:',
        decryptPassword: 'Enter password:',
        watermarkText: 'Watermark text:',
        watermarkSize: 'Font size:',
        watermarkAngle: 'Rotation angle:',
        watermarkPagesLabel: 'Page range (empty for all):',
        success: 'Success!',
        error: 'Error: ',
        selectFile: 'Please select a file first',
        selectOutput: 'Please select output path',
        passwordMismatch: 'Passwords do not match',
        passwordRequired: 'Please enter password',
        passwordMinLength: 'Password must be at least 6 characters',
        invalidPages: 'Invalid page format',
        filesSelected: '{count} file(s) selected',
        fileSelected: 'File selected',
        processing: 'Processing...',
        done: 'Done!',
        downloadDone: 'Download complete!',
        fileTooLarge: 'File too large, exceeds 100MB limit',
        operationFailed: 'Operation failed, please try again'
    }
};

let currentLang = localStorage.getItem('pdf_toolbox_lang') || 'zh';

function getSystemLang() {
    const lang = navigator.language || navigator.userLanguage;
    return lang.toLowerCase().startsWith('zh') ? 'zh' : 'en';
}

function initLang() {
    const saved = localStorage.getItem('pdf_toolbox_lang');
    if (saved) {
        currentLang = saved;
    } else {
        currentLang = getSystemLang();
    }
}

function t(key, params = {}) {
    let text = translations[currentLang][key] || translations['zh'][key] || key;
    Object.keys(params).forEach(name => {
        text = text.replace(`{${name}}`, params[name]);
    });
    return text;
}

function switchLang() {
    currentLang = currentLang === 'zh' ? 'en' : 'zh';
    localStorage.setItem('pdf_toolbox_lang', currentLang);
    applyLang();
}

function applyLang() {
    document.title = t('title');
    document.querySelector('header h1').textContent = t('title');
    document.getElementById('langBtn').textContent = t('langBtn');
    
    const tabs = document.querySelectorAll('.tab');
    const tabKeys = ['tabMerge', 'tabSplit', 'tabExtract', 'tabRotate', 'tabEncrypt', 'tabDecrypt', 'tabWatermark'];
    tabs.forEach((tab, i) => {
        tab.textContent = t(tabKeys[i]);
    });
    
    const panels = {
        merge: { title: 'mergeTitle', btn: 'mergeBtn' },
        split: { title: 'splitTitle', btn: 'splitBtn' },
        extract: { title: 'extractTitle', btn: 'extractBtn' },
        rotate: { title: 'rotateTitle', btn: 'rotateBtn' },
        encrypt: { title: 'encryptTitle', btn: 'encryptBtn' },
        decrypt: { title: 'decryptTitle', btn: 'decryptBtn' },
        watermark: { title: 'watermarkTitle', btn: 'watermarkBtn' }
    };
    
    Object.keys(panels).forEach(key => {
        const panel = document.getElementById(key);
        if (panel) {
            const h2 = panel.querySelector('h2');
            if (h2) h2.textContent = t(panels[key].title);
            const btn = panel.querySelector('.btn');
            if (btn) btn.textContent = t(panels[key].btn);
        }
    });
    
    document.querySelectorAll('.upload-area p').forEach(p => {
        p.innerHTML = t('uploadHint') + `<label class="link">${t('clickSelect')}</label>`;
    });
}

initLang();
