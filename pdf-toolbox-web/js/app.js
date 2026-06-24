const { PDFDocument } = PDFLib;

let currentFiles = {};
const MAX_FILE_SIZE = 100 * 1024 * 1024;

function showToast(msg, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function parsePages(str, total) {
    if (!str.trim()) return Array.from({ length: total }, (_, i) => i + 1);
    
    const pages = new Set();
    const parts = str.split(',');
    
    for (const part of parts) {
        const trimmed = part.trim();
        if (trimmed.includes('-')) {
            const [start, end] = trimmed.split('-').map(s => parseInt(s.trim()));
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = Math.max(1, start); i <= Math.min(total, end); i++) {
                    pages.add(i);
                }
            }
        } else {
            const page = parseInt(trimmed);
            if (!isNaN(page) && page >= 1 && page <= total) {
                pages.add(page);
            }
        }
    }
    
    return Array.from(pages).sort((a, b) => a - b);
}

function setupUpload(inputId, containerId, multiple = false) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(containerId);
    
    container.addEventListener('click', (e) => {
        if (e.target.tagName === 'LABEL') {
            e.preventDefault();
        }
        input.click();
    });
    
    container.addEventListener('dragover', (e) => {
        e.preventDefault();
        container.classList.add('dragover');
    });
    
    container.addEventListener('dragleave', () => {
        container.classList.remove('dragover');
    });
    
    container.addEventListener('drop', (e) => {
        e.preventDefault();
        container.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files).filter(f => 
            f.name.toLowerCase().endsWith('.pdf') && f.type === 'application/pdf'
        );
        if (files.length) handleFiles(inputId, files, multiple);
    });
    
    input.addEventListener('change', () => {
        if (input.files.length) {
            handleFiles(inputId, Array.from(input.files), multiple);
        }
    });
}

function handleFiles(inputId, files, multiple) {
    const key = inputId.replace('Files', '').replace('File', '');
    
    const oversized = files.find(f => f.size > MAX_FILE_SIZE);
    if (oversized) {
        showToast(t('fileTooLarge'), 'error');
        return;
    }
    
    if (multiple) {
        currentFiles[key] = files;
        const listId = key + 'FileList';
        const list = document.getElementById(listId);
        if (list) {
            list.innerHTML = '';
            files.forEach((f, i) => {
                const item = document.createElement('div');
                item.className = 'file-item';
                
                const nameSpan = document.createElement('span');
                nameSpan.className = 'file-name';
                nameSpan.textContent = f.name;
                
                const sizeSpan = document.createElement('span');
                sizeSpan.className = 'file-size';
                sizeSpan.textContent = formatSize(f.size);
                
                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-btn';
                removeBtn.textContent = '×';
                removeBtn.onclick = () => removeFile(key, i);
                
                item.appendChild(nameSpan);
                item.appendChild(sizeSpan);
                item.appendChild(removeBtn);
                list.appendChild(item);
            });
        }
        updateBtn(key, true);
    } else {
        currentFiles[key] = files[0];
        const infoId = key + 'FileInfo';
        const info = document.getElementById(infoId);
        if (info) {
            info.textContent = `${files[0].name} (${formatSize(files[0].size)})`;
            info.style.display = 'block';
        }
        updateBtn(key, true);
    }
}

function removeFile(key, index) {
    if (currentFiles[key]) {
        currentFiles[key].splice(index, 1);
        if (currentFiles[key].length === 0) {
            delete currentFiles[key];
        }
        handleFiles(key + 'Files', currentFiles[key] || [], true);
    }
}

function updateBtn(key, enabled) {
    const btn = document.getElementById(key + 'Btn');
    if (btn) btn.disabled = !enabled;
}

async function readFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(new Uint8Array(reader.result));
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

function downloadPdf(bytes, filename) {
    const blob = new Blob([bytes], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

async function mergePdfs() {
    const files = currentFiles.merge;
    if (!files || files.length < 2) {
        showToast(t('selectFile'), 'error');
        return;
    }
    
    const btn = document.getElementById('mergeBtn');
    btn.disabled = true;
    btn.textContent = t('processing');
    
    try {
        const merged = await PDFDocument.create();
        
        for (const file of files) {
            const bytes = await readFile(file);
            const doc = await PDFDocument.load(bytes);
            const pages = await merged.copyPages(doc, doc.getPageIndices());
            pages.forEach(page => merged.addPage(page));
        }
        
        const pdfBytes = await merged.save();
        downloadPdf(pdfBytes, 'merged.pdf');
        showToast(t('downloadDone'));
    } catch (e) {
        console.error('Merge error:', e);
        showToast(t('operationFailed'), 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = t('mergeBtn');
    }
}

async function splitPdf() {
    const file = currentFiles.split;
    if (!file) {
        showToast(t('selectFile'), 'error');
        return;
    }
    
    const btn = document.getElementById('splitBtn');
    btn.disabled = true;
    btn.textContent = t('processing');
    
    try {
        const bytes = await readFile(file);
        const doc = await PDFDocument.load(bytes);
        const total = doc.getPageCount();
        const mode = document.getElementById('splitMode').value;
        
        if (mode === 'single') {
            for (let i = 0; i < total; i++) {
                const newDoc = await PDFDocument.create();
                const [page] = await newDoc.copyPages(doc, [i]);
                newDoc.addPage(page);
                const pdfBytes = await newDoc.save();
                downloadPdf(pdfBytes, `page_${i + 1}.pdf`);
            }
        } else {
            const rangeStr = document.getElementById('splitRange').value;
            const ranges = rangeStr.split(',').map(r => r.trim());
            
            for (let ri = 0; ri < ranges.length; ri++) {
                const range = ranges[ri];
                const newDoc = await PDFDocument.create();
                
                if (range.includes('-')) {
                    const [start, end] = range.split('-').map(s => parseInt(s.trim()) - 1);
                    for (let i = start; i <= end && i < total; i++) {
                        const [page] = await newDoc.copyPages(doc, [i]);
                        newDoc.addPage(page);
                    }
                } else {
                    const pageIdx = parseInt(range) - 1;
                    if (pageIdx >= 0 && pageIdx < total) {
                        const [page] = await newDoc.copyPages(doc, [pageIdx]);
                        newDoc.addPage(page);
                    }
                }
                
                const pdfBytes = await newDoc.save();
                downloadPdf(pdfBytes, `split_${ri + 1}.pdf`);
            }
        }
        
        showToast(t('downloadDone'));
    } catch (e) {
        console.error('Split error:', e);
        showToast(t('operationFailed'), 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = t('splitBtn');
    }
}

async function extractPages() {
    const file = currentFiles.extract;
    if (!file) {
        showToast(t('selectFile'), 'error');
        return;
    }
    
    const pagesStr = document.getElementById('extractPages').value;
    if (!pagesStr.trim()) {
        showToast(t('invalidPages'), 'error');
        return;
    }
    
    const btn = document.getElementById('extractBtn');
    btn.disabled = true;
    btn.textContent = t('processing');
    
    try {
        const bytes = await readFile(file);
        const doc = await PDFDocument.load(bytes);
        const total = doc.getPageCount();
        const pages = parsePages(pagesStr, total);
        
        if (pages.length === 0) {
            showToast(t('invalidPages'), 'error');
            return;
        }
        
        const newDoc = await PDFDocument.create();
        const copiedPages = await newDoc.copyPages(doc, pages.map(p => p - 1));
        copiedPages.forEach(page => newDoc.addPage(page));
        
        const pdfBytes = await newDoc.save();
        downloadPdf(pdfBytes, 'extracted.pdf');
        showToast(t('downloadDone'));
    } catch (e) {
        console.error('Extract error:', e);
        showToast(t('operationFailed'), 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = t('extractBtn');
    }
}

async function rotatePages() {
    const file = currentFiles.rotate;
    if (!file) {
        showToast(t('selectFile'), 'error');
        return;
    }
    
    const btn = document.getElementById('rotateBtn');
    btn.disabled = true;
    btn.textContent = t('processing');
    
    try {
        const bytes = await readFile(file);
        const doc = await PDFDocument.load(bytes);
        const total = doc.getPageCount();
        const angle = parseInt(document.getElementById('rotateAngle').value);
        const pagesStr = document.getElementById('rotatePages').value;
        const pages = parsePages(pagesStr, total);
        
        for (const pageNum of pages) {
            const page = doc.getPage(pageNum - 1);
            const currentRotation = page.getRotation().angle;
            page.setRotation((currentRotation + angle) % 360);
        }
        
        const pdfBytes = await doc.save();
        downloadPdf(pdfBytes, 'rotated.pdf');
        showToast(t('downloadDone'));
    } catch (e) {
        console.error('Rotate error:', e);
        showToast(t('operationFailed'), 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = t('rotateBtn');
    }
}

async function addWatermark() {
    const file = currentFiles.watermark;
    if (!file) {
        showToast(t('selectFile'), 'error');
        return;
    }
    
    const btn = document.getElementById('watermarkBtn');
    btn.disabled = true;
    btn.textContent = t('processing');
    
    try {
        const bytes = await readFile(file);
        const doc = await PDFDocument.load(bytes);
        const total = doc.getPageCount();
        const text = document.getElementById('watermarkText').value || '机密';
        
        let fontSize = parseInt(document.getElementById('watermarkSize').value) || 48;
        fontSize = Math.max(10, Math.min(200, fontSize));
        
        let angle = parseInt(document.getElementById('watermarkAngle').value) || 45;
        angle = Math.max(0, Math.min(360, angle));
        
        const pagesStr = document.getElementById('watermarkPages').value;
        const pages = parsePages(pagesStr, total);
        
        const font = await doc.embedFont('Helvetica');
        const hasChinese = /[\u4e00-\u9fa5]/.test(text);
        
        if (hasChinese) {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            for (const pageNum of pages) {
                const page = doc.getPage(pageNum - 1);
                const { width, height } = page.getSize();
                
                canvas.width = width * 2;
                canvas.height = height * 2;
                ctx.scale(2, 2);
                ctx.clearRect(0, 0, width, height);
                
                ctx.font = `${fontSize}px SimSun, Microsoft YaHei, sans-serif`;
                ctx.fillStyle = 'rgba(0, 0, 0, 0.12)';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                
                const xSpacing = width * 0.4;
                const ySpacing = height * 0.4;
                
                for (let x = -width * 0.5; x <= width * 1.5; x += xSpacing) {
                    for (let y = -height * 0.5; y <= height * 1.5; y += ySpacing) {
                        ctx.save();
                        ctx.translate(x, y);
                        ctx.rotate(-angle * Math.PI / 180);
                        ctx.fillText(text, 0, 0);
                        ctx.restore();
                    }
                }
                
                const dataUrl = canvas.toDataURL('image/png');
                const imgBytes = Uint8Array.from(atob(dataUrl.split(',')[1]), c => c.charCodeAt(0));
                const img = await doc.embedPng(imgBytes);
                
                page.drawImage(img, {
                    x: 0, y: 0, width: width, height: height
                });
            }
        } else {
            for (const pageNum of pages) {
                const page = doc.getPage(pageNum - 1);
                const { width, height } = page.getSize();
                
                const xSpacing = width * 0.4;
                const ySpacing = height * 0.4;
                
                for (let x = -width * 0.5; x <= width * 1.5; x += xSpacing) {
                    for (let y = -height * 0.5; y <= height * 1.5; y += ySpacing) {
                        page.drawText(text, {
                            x, y, size: fontSize, font,
                            color: rgb(0.8, 0.8, 0.8),
                            rotate: angle, opacity: 0.15
                        });
                    }
                }
            }
        }
        
        const pdfBytes = await doc.save();
        downloadPdf(pdfBytes, 'watermarked.pdf');
        showToast(t('downloadDone'));
    } catch (e) {
        console.error('Watermark error:', e);
        showToast(t('operationFailed'), 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = t('watermarkBtn');
    }
}

async function imageToPdf() {
    const files = currentFiles.image;
    if (!files || files.length === 0) {
        showToast(t('selectFile'), 'error');
        return;
    }
    
    const btn = document.getElementById('imageBtn');
    btn.disabled = true;
    btn.textContent = t('processing');
    
    try {
        const doc = await PDFDocument.create();
        
        for (const file of files) {
            const imgBytes = await readFile(file);
            const ext = file.name.split('.').pop().toLowerCase();
            let img;
            if (ext === 'png') {
                img = await doc.embedPng(imgBytes);
            } else {
                img = await doc.embedJpg(imgBytes);
            }
            const page = doc.addPage([img.width, img.height]);
            page.drawImage(img, { x: 0, y: 0, width: img.width, height: img.height });
        }
        
        const pdfBytes = await doc.save();
        downloadPdf(pdfBytes, 'images.pdf');
        showToast(t('downloadDone'));
    } catch (e) {
        console.error('ImageToPdf error:', e);
        showToast(t('operationFailed'), 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = t('imageBtn');
    }
}

async function deletePages() {
    const file = currentFiles.delete;
    if (!file) {
        showToast(t('selectFile'), 'error');
        return;
    }
    
    const pagesStr = document.getElementById('deletePages').value;
    if (!pagesStr.trim()) {
        showToast(t('deletePagesHint'), 'error');
        return;
    }
    
    const btn = document.getElementById('deleteBtn');
    btn.disabled = true;
    btn.textContent = t('processing');
    
    try {
        const bytes = await readFile(file);
        const doc = await PDFDocument.load(bytes);
        const total = doc.getPageCount();
        const removePages = parsePages(pagesStr, total);
        
        const newDoc = await PDFDocument.create();
        for (let i = 0; i < total; i++) {
            if (!removePages.includes(i + 1)) {
                const [page] = await newDoc.copyPages(doc, [i]);
                newDoc.addPage(page);
            }
        }
        
        const pdfBytes = await newDoc.save();
        downloadPdf(pdfBytes, 'deleted.pdf');
        showToast(t('downloadDone'));
    } catch (e) {
        console.error('Delete error:', e);
        showToast(t('operationFailed'), 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = t('deleteBtn');
    }
}

async function compressPdf() {
    const file = currentFiles.compress;
    if (!file) {
        showToast(t('selectFile'), 'error');
        return;
    }
    
    const btn = document.getElementById('compressBtn');
    btn.disabled = true;
    btn.textContent = t('processing');
    
    try {
        const bytes = await readFile(file);
        const doc = await PDFDocument.load(bytes);
        const total = doc.getPageCount();
        const quality = parseFloat(document.getElementById('compressQuality').value);
        
        const newDoc = await PDFDocument.create();
        
        for (let i = 0; i < total; i++) {
            const [page] = await newDoc.copyPages(doc, [i]);
            newDoc.addPage(page);
        }
        
        const pdfBytes = await newDoc.save();
        downloadPdf(pdfBytes, 'compressed.pdf');
        showToast(t('downloadDone'));
    } catch (e) {
        console.error('Compress error:', e);
        showToast(t('operationFailed'), 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = t('compressBtn');
    }
}

function init() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });
    
    setupUpload('mergeFiles', 'mergeUpload', true);
    setupUpload('splitFile', 'splitUpload');
    setupUpload('extractFile', 'extractUpload');
    setupUpload('rotateFile', 'rotateUpload');
    setupUpload('imageFiles', 'imageUpload', true);
    setupUpload('deleteFile', 'deleteUpload');
    setupUpload('compressFile', 'compressUpload');
    setupUpload('watermarkFile', 'watermarkUpload');
    
    document.getElementById('splitMode').addEventListener('change', (e) => {
        document.getElementById('splitRangeGroup').classList.toggle('hidden', e.target.value !== 'range');
    });
    
    document.getElementById('mergeBtn').addEventListener('click', mergePdfs);
    document.getElementById('splitBtn').addEventListener('click', splitPdf);
    document.getElementById('extractBtn').addEventListener('click', extractPages);
    document.getElementById('rotateBtn').addEventListener('click', rotatePages);
    document.getElementById('imageBtn').addEventListener('click', imageToPdf);
    document.getElementById('deleteBtn').addEventListener('click', deletePages);
    document.getElementById('compressBtn').addEventListener('click', compressPdf);
    document.getElementById('watermarkBtn').addEventListener('click', addWatermark);
    
    document.getElementById('langBtn').addEventListener('click', switchLang);
    
    applyLang();
}

document.addEventListener('DOMContentLoaded', init);
