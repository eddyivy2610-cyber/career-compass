document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const chooseFileLink = document.getElementById('choose-file-link');
    const tbody = document.getElementById('uploaded-files-tbody');
    
    // Preview Modal Elements
    const previewModal = document.getElementById('preview-modal');
    const closePreviewBtn = document.getElementById('close-modal-btn');
    const cancelPreviewBtn = document.getElementById('cancel-modal-btn');
    const confirmImportBtn = document.getElementById('confirm-import-btn');
    const previewThead = document.getElementById('preview-thead');
    const previewTbody = document.getElementById('preview-tbody');

    // Engine Modal Elements
    const openEngineBtn = document.getElementById('open-engine-btn');
    const engineModal = document.getElementById('engine-modal');
    const closeEngineBtn = document.getElementById('close-engine-btn');
    const cancelEngineBtn = document.getElementById('cancel-engine-btn');
    const startEngineBtn = document.getElementById('start-engine-btn');
    
    const sourceAllRadio = document.getElementById('source-all');
    const sourceCustomRadio = document.getElementById('source-custom');
    const customFilesSection = document.getElementById('custom-files-section');
    const fileCheckboxList = document.getElementById('file-checkbox-list');

    const requiredSystemFields = ['StudentID', 'Name', 'Class', 'Term', 'Subject', 'Score'];

    let uploadedFiles = []; // State array
    let currentPreviewFileId = null;

    // --- UPLOAD LOGIC ---
    if (dropzone && fileInput) {
        dropzone.addEventListener('click', (e) => {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        dropzone.addEventListener('drop', handleDrop, false);
        
        // Handle selected files
        fileInput.addEventListener('change', handleFiles, false);
    }

    function preventDefaults (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropzone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropzone.classList.remove('dragover');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files: files } });
    }

    async function handleFiles(e) {
        const files = e.target.files;
        if (!files || files.length === 0) return;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const validExts = ['.csv', '.xlsx', '.xls', '.xml'];
            const fileName = file.name;
            const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
            
            if (validExts.includes(ext)) {
                await processFileUpload(file);
            } else {
                alert(`Invalid file type: ${fileName}. Please upload .csv, .xls, .xlsx, or .xml`);
            }
        }
        
        fileInput.value = "";
    }

    async function processFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload_preview', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                const now = new Date();
                const dateStr = now.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
                const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }).toLowerCase();
                
                const newFileObj = {
                    id: Date.now() + Math.random().toString(36).substr(2, 9),
                    name: file.name,
                    serverFilepath: data.filepath,
                    headers: data.headers,
                    sample: data.sample,
                    recordCount: data.sample.length ? "Unknown" : 0,
                    status: 'Pending',
                    processedOn: `${dateStr}, ${timeStr}`
                };
                
                uploadedFiles.push(newFileObj);
                renderTable();
            } else {
                alert(`Error uploading ${file.name}: ${data.error}`);
            }
        } catch (error) {
            alert(`Error uploading ${file.name}: ${error.message}`);
        }
    }

    function removeFile(id) {
        uploadedFiles = uploadedFiles.filter(f => f.id !== id);
        renderTable();
    }

    function renderTable() {
        if (!tbody) return;
        tbody.innerHTML = '';
        
        if (uploadedFiles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No files uploaded yet.</td></tr>';
            return;
        }

        uploadedFiles.forEach(file => {
            const tr = document.createElement('tr');
            
            const tdName = document.createElement('td');
            tdName.innerHTML = `<svg style="color:#94a3b8; vertical-align:middle; margin-right:8px;" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 256 256"><path fill="currentColor" d="M216 40v176a16 16 0 0 1-16 16H56a16 16 0 0 1-16-16V40a16 16 0 0 1 16-16h144a16 16 0 0 1 16 16Zm-64 88L112 88H88l28 40l-28 40h24l40-40ZM152 24v56h64V40a16 16 0 0 0-16-16Z"/></svg> ${file.name}`;
            
            const tdCount = document.createElement('td');
            tdCount.textContent = file.recordCount;
            
            const tdStatus = document.createElement('td');
            let statusClass = 'pending';
            if (file.status === 'Imported') statusClass = 'complete';
            else if (file.status === 'Failed') statusClass = 'partial';
            
            tdStatus.innerHTML = `<div class="status-circle ${statusClass}" title="${file.status}">
                ${statusClass === 'complete' ? '✓' : (statusClass === 'pending' ? '...' : '!')}
            </div>`;
            
            const tdDate = document.createElement('td');
            tdDate.textContent = file.processedOn;
            
            const tdActions = document.createElement('td');
            tdActions.className = 'action-icons';
            
            const btnPreview = document.createElement('button');
            btnPreview.className = 'icon-btn preview';
            btnPreview.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 256 256"><path fill="currentColor" d="M224 48H32a8 8 0 0 0-8 8v144a8 8 0 0 0 8 8h192a8 8 0 0 0 8-8V56a8 8 0 0 0-8-8Zm-8 144H40V64h176Z"/></svg>';
            btnPreview.title = "Preview & Map";
            btnPreview.onclick = (e) => { e.stopPropagation(); openPreviewMapping(file.id); };
            
            const btnDelete = document.createElement('button');
            btnDelete.className = 'icon-btn delete';
            btnDelete.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 256 256"><path fill="currentColor" d="M216 48h-40v-8a24 24 0 0 0-24-24h-48a24 24 0 0 0-24 24v8H40a8 8 0 0 0 0 16h8v144a16 16 0 0 0 16 16h128a16 16 0 0 0 16-16V64h8a8 8 0 0 0 0-16ZM96 40a8 8 0 0 1 8-8h48a8 8 0 0 1 8 8v8H96Zm96 168H64V64h128Zm-80-104v64a8 8 0 0 1-16 0v-64a8 8 0 0 1 16 0Zm48 0v64a8 8 0 0 1-16 0v-64a8 8 0 0 1 16 0Z"/></svg>';
            btnDelete.title = "Delete";
            btnDelete.onclick = (e) => { e.stopPropagation(); removeFile(file.id); };
            
            tdActions.appendChild(btnPreview);
            tdActions.appendChild(btnDelete);
            
            tr.appendChild(tdName);
            tr.appendChild(tdCount);
            tr.appendChild(tdStatus);
            tr.appendChild(tdDate);
            tr.appendChild(tdActions);
            
            tbody.appendChild(tr);
        });
    }

    // --- PREVIEW MODAL LOGIC ---
    function openPreviewMapping(fileId) {
        const fileObj = uploadedFiles.find(f => f.id === fileId);
        if (!fileObj) return;
        
        currentPreviewFileId = fileId;
        
        const trHead = document.createElement('tr');
        fileObj.headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            
            const select = document.createElement('select');
            select.className = "mapping-select-inline";
            select.dataset.fileHeader = header;
            
            const defaultOpt = document.createElement('option');
            defaultOpt.value = "";
            defaultOpt.textContent = "Map to...";
            select.appendChild(defaultOpt);
            
            requiredSystemFields.forEach(sysField => {
                const opt = document.createElement('option');
                opt.value = sysField;
                opt.textContent = sysField;
                if (sysField.toLowerCase() === header.toLowerCase().replace(/\s/g, '')) {
                    opt.selected = true;
                }
                select.appendChild(opt);
            });
            
            th.appendChild(select);
            trHead.appendChild(th);
        });
        
        previewThead.innerHTML = '';
        previewThead.appendChild(trHead);
        
        previewTbody.innerHTML = '';
        fileObj.sample.forEach(row => {
            const trBody = document.createElement('tr');
            fileObj.headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header] !== null ? row[header] : '';
                trBody.appendChild(td);
            });
            previewTbody.appendChild(trBody);
        });
        
        if (fileObj.status === 'Imported') {
            confirmImportBtn.style.display = 'none';
        } else {
            confirmImportBtn.style.display = 'inline-block';
            confirmImportBtn.innerHTML = 'Confirm Import';
            confirmImportBtn.disabled = false;
        }

        if(previewModal) previewModal.classList.remove('hidden');
    }

    if (confirmImportBtn) {
        confirmImportBtn.addEventListener('click', async () => {
            const fileObj = uploadedFiles.find(f => f.id === currentPreviewFileId);
            if (!fileObj) return;

            const selects = document.querySelectorAll('.mapping-select-inline');
            const mapping = {};
            
            selects.forEach(sel => {
                if (sel.value) {
                    mapping[sel.value] = sel.dataset.fileHeader;
                }
            });
            
            confirmImportBtn.disabled = true;
            confirmImportBtn.innerHTML = 'Processing...';

            try {
                const response = await fetch('/upload_confirm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        filepath: fileObj.serverFilepath,
                        mapping: mapping
                    })
                });
                const data = await response.json();

                if (response.ok) {
                    fileObj.status = 'Imported';
                    fileObj.recordCount = data.students ? data.students.length : 'Unknown';
                    renderTable();
                    alert("Import successful!");
                    if(previewModal) previewModal.classList.add('hidden');
                } else {
                    alert(`Error: ${data.error}`);
                    confirmImportBtn.disabled = false;
                    confirmImportBtn.innerHTML = 'Confirm Import';
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
                confirmImportBtn.disabled = false;
                confirmImportBtn.innerHTML = 'Confirm Import';
            }
        });
    }

    if(closePreviewBtn) closePreviewBtn.addEventListener('click', () => previewModal.classList.add('hidden'));
    if(cancelPreviewBtn) cancelPreviewBtn.addEventListener('click', () => previewModal.classList.add('hidden'));
    
    // --- ENGINE MODAL LOGIC ---
    if (openEngineBtn) {
        openEngineBtn.addEventListener('click', () => {
            // Populate file checkboxes
            if (fileCheckboxList) {
                fileCheckboxList.innerHTML = '';
                const importedFiles = uploadedFiles.filter(f => f.status === 'Imported');
                
                if (importedFiles.length === 0) {
                    fileCheckboxList.innerHTML = '<p style="margin:0; color: #ef4444;">No files have been fully imported yet.</p>';
                    sourceCustomRadio.disabled = true;
                    sourceAllRadio.checked = true;
                } else {
                    sourceCustomRadio.disabled = false;
                    importedFiles.forEach(file => {
                        const div = document.createElement('div');
                        div.style.marginBottom = '4px';
                        div.innerHTML = `
                            <input type="checkbox" id="file-${file.id}" value="${file.id}" class="custom-file-checkbox">
                            <label for="file-${file.id}" style="font-weight: normal; cursor: pointer; margin-left: 4px;">${file.name}</label>
                        `;
                        fileCheckboxList.appendChild(div);
                    });
                }
            }
            
            // Show modal
            if(engineModal) engineModal.classList.remove('hidden');
        });
    }

    if (sourceAllRadio && sourceCustomRadio) {
        sourceAllRadio.addEventListener('change', () => {
            if (sourceAllRadio.checked) customFilesSection.classList.add('hidden');
        });
        sourceCustomRadio.addEventListener('change', () => {
            if (sourceCustomRadio.checked) customFilesSection.classList.remove('hidden');
        });
    }

    if (startEngineBtn) {
        startEngineBtn.addEventListener('click', async () => {
            const isAll = sourceAllRadio.checked;
            const customFiles = [];
            
            if (!isAll) {
                const checkboxes = document.querySelectorAll('.custom-file-checkbox:checked');
                checkboxes.forEach(cb => customFiles.push(cb.value));
                if (customFiles.length === 0) {
                    alert("Please select at least one file to process.");
                    return;
                }
            }
            
            const studentFilterInput = document.getElementById('engine-student-filter');
            const studentIds = studentFilterInput.value.split(',').map(s => s.trim()).filter(s => s);

            // Real backend request
            startEngineBtn.disabled = true;
            startEngineBtn.innerHTML = '<svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 4V2C6.477 2 2 6.477 2 12h2c0-4.418 3.582-8 8-8z" fill="currentColor"></path></svg> Running...';
            
            try {
                const response = await fetch('/run_engine', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        runOnAll: isAll,
                        customFiles: customFiles,
                        specificStudents: studentIds
                    })
                });
                const data = await response.json();

                if (response.ok) {
                    // Redirect to reports
                    window.location.href = '/reports';
                } else {
                    alert(`Error: ${data.error}`);
                    startEngineBtn.disabled = false;
                    startEngineBtn.innerHTML = 'Start Engine';
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
                startEngineBtn.disabled = false;
                startEngineBtn.innerHTML = 'Start Engine';
            }
        });
    }

    if(closeEngineBtn) closeEngineBtn.addEventListener('click', () => engineModal.classList.add('hidden'));
    if(cancelEngineBtn) cancelEngineBtn.addEventListener('click', () => engineModal.classList.add('hidden'));

    // Global Modal Click Outside
    window.addEventListener('click', (e) => {
        if (e.target === previewModal) previewModal.classList.add('hidden');
        if (e.target === engineModal) engineModal.classList.add('hidden');
    });

    // --- NAVIGATION INDICATOR LOGIC ---
    const navLinksContainer = document.querySelector('.nav-links');
    const navItems = document.querySelectorAll('.nav-item');
    const indicator = document.querySelector('.nav-indicator');

    if (navLinksContainer && indicator) {
        const activeItem = document.querySelector('.nav-item.active');
        
        function setIndicator(item) {
            if (!item) return;
            const itemRect = item.getBoundingClientRect();
            const containerRect = navLinksContainer.getBoundingClientRect();
            indicator.style.width = `${item.offsetWidth}px`;
            indicator.style.left = `${itemRect.left - containerRect.left}px`;
        }

        if (activeItem) {
            setIndicator(activeItem);
            indicator.style.opacity = '1';
        }

        navItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                indicator.style.opacity = '1';
                setIndicator(item);
            });
        });

        navLinksContainer.addEventListener('mouseleave', () => {
            if (activeItem) {
                setIndicator(activeItem);
            } else {
                indicator.style.opacity = '0';
            }
        });
    }
    
    // Initial Render
    renderTable();
});
