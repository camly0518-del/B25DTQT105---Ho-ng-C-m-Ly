/**
 * DataMind AI Agent - Client Application Logic
 */

let currentTab = 1;
let currentDiagnosis = null;
let currentProposals = [];
let hasCleanedData = false;

document.addEventListener("DOMContentLoaded", () => {
    initSampleDatasets();
    initDragAndDrop();
    checkInitialState();
});

// ================= STEPPER & TABS =================
function switchTab(tabIndex) {
    if (tabIndex === currentTab) return;

    // Ẩn tất cả tabs
    document.querySelectorAll(".tab-pane").forEach(el => el.classList.add("hidden"));
    document.querySelectorAll(".step-btn").forEach(el => el.classList.remove("active"));

    // Hiển thị tab được chọn
    const targetTab = document.getElementById(`tab-content-${tabIndex}`);
    const targetBtn = document.getElementById(`step-btn-${tabIndex}`);

    if (targetTab) targetTab.classList.remove("hidden");
    if (targetBtn) targetBtn.classList.add("active");

    currentTab = tabIndex;

    // Logic đặc thù theo từng tab
    if (tabIndex === 2) {
        if (!currentDiagnosis) {
            fetchDiagnosis();
        }
    } else if (tabIndex === 3) {
        // Tự động chạy hoặc render phân tích nếu có dữ liệu
        runDeepAnalysis();
    } else if (tabIndex === 4) {
        reloadReport();
    }
}

// ================= BƯỚC 1: NẠP & MẪU DỮ LIỆU =================
async function initSampleDatasets() {
    try {
        const res = await fetch("/api/samples");
        const samples = await res.json();
        const container = document.getElementById("sample-dataset-cards");
        if (!container) return;

        container.innerHTML = samples.map(s => `
            <div onclick="loadSampleDataset('${s.id}')" class="bg-slate-50 hover:bg-brand-50/60 p-4 rounded-2xl border border-slate-200 hover:border-brand-300 transition cursor-pointer flex flex-col justify-between group">
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <div class="w-8 h-8 rounded-xl bg-white text-brand-600 shadow-2xs flex items-center justify-center text-sm group-hover:scale-110 transition">
                            <i class="fas ${s.icon}"></i>
                        </div>
                        <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-brand-100 text-brand-700">${s.badge}</span>
                    </div>
                    <h4 class="font-bold text-slate-800 text-xs mb-1 group-hover:text-brand-700">${s.name}</h4>
                    <p class="text-[11px] text-slate-500 leading-relaxed">${s.desc}</p>
                </div>
                <div class="mt-3 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] font-semibold text-brand-600">
                    <span>Nạp bộ mẫu này</span>
                    <i class="fas fa-arrow-right text-[10px] group-hover:translate-x-1 transition"></i>
                </div>
            </div>
        `).join("");
    } catch (err) {
        console.error("Lỗi khi tải danh sách mẫu:", err);
    }
}

async function loadSampleDataset(sampleId) {
    showUploadSpinner(true);
    try {
        const res = await fetch(`/api/load-sample/${sampleId}`, { method: "POST" });
        const data = await res.json();
        if (data.status === "success") {
            handleDataLoaded(data);
            showToast(`Đã nạp thành công bộ dữ liệu: ${data.dataset_name}`, "success");
        } else {
            showToast(data.detail || "Không thể tải bộ mẫu", "error");
        }
    } catch (err) {
        showToast("Lỗi kết nối máy chủ: " + err.message, "error");
    } finally {
        showUploadSpinner(false);
    }
}

function initDragAndDrop() {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");

    if (!dropZone || !fileInput) return;

    ['dragenter', 'dragover'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            dropZone.classList.add("border-brand-500", "bg-brand-50/50");
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            dropZone.classList.remove("border-brand-500", "bg-brand-50/50");
        });
    });

    dropZone.addEventListener("drop", (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) uploadFile(files[0]);
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) uploadFile(e.target.files[0]);
    });
}

async function uploadFile(file) {
    showUploadSpinner(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (res.ok && data.status === "success") {
            handleDataLoaded(data);
            showToast(`Đã tải lên tệp: ${file.name}`, "success");
        } else {
            showToast(data.detail || "Lỗi khi xử lý file tải lên", "error");
        }
    } catch (err) {
        showToast("Lỗi tải tệp: " + err.message, "error");
    } finally {
        showUploadSpinner(false);
    }
}

function handleDataLoaded(data) {
    // Cập nhật nhãn bộ dữ liệu
    document.getElementById("current-dataset-label").innerText = data.dataset_name;
    document.getElementById("dataset-badge").classList.remove("hidden");

    // Đánh dấu bước 1 hoàn thành
    document.getElementById("step-btn-1").classList.add("completed");

    // Hiển thị bảng xem trước dữ liệu thô
    renderRawTable(data.columns, data.preview, data.rows, data.cols);

    // Lưu chẩn đoán và chuyển tiếp dữ liệu sẵn sàng cho Bước 2
    if (data.diagnosis) {
        currentDiagnosis = data.diagnosis;
        renderDiagnosis(data.diagnosis);
    }
}

function renderRawTable(columns, previewData, rows, cols) {
    const container = document.getElementById("raw-preview-container");
    const countTag = document.getElementById("raw-count-tag");
    const table = document.getElementById("raw-preview-table");

    container.classList.remove("hidden");
    countTag.innerText = `${rows.toLocaleString()} dòng x ${cols} cột`;

    // Render thead
    const ths = columns.map(c => `<th class="py-2.5 px-3 bg-slate-50 font-bold text-slate-700 border-b border-slate-200">${c}</th>`).join("");
    
    // Render tbody
    const trs = previewData.map(row => {
        const tds = columns.map(col => `<td class="py-2 px-3 border-b border-slate-100 text-slate-600">${row[col] !== null ? row[col] : '<span class="text-rose-400 italic">null</span>'}</td>`).join("");
        return `<tr class="hover:bg-slate-50/50">${tds}</tr>`;
    }).join("");

    table.innerHTML = `<thead><tr>${ths}</tr></thead><tbody>${trs}</tbody>`;
}

// ================= BƯỚC 2: CHẨN ĐOÁN & DUYỆT LÀM SẠCH (HUMAN-IN-THE-LOOP) =================
async function fetchDiagnosis() {
    try {
        const res = await fetch("/api/diagnose");
        const data = await res.json();
        if (data.status === "success") {
            currentDiagnosis = data.diagnosis;
            renderDiagnosis(data.diagnosis);
        }
    } catch (err) {
        console.error("Lỗi lấy chẩn đoán:", err);
    }
}

function renderDiagnosis(diag) {
    const summary = diag.summary;
    currentProposals = diag.proposals || [];

    // Health Score Circle
    const scoreVal = document.getElementById("health-score-val");
    const scoreCircle = document.getElementById("health-score-circle");
    const gradeText = document.getElementById("health-grade-text");

    scoreVal.innerText = `${summary.health_score}%`;
    scoreCircle.setAttribute("stroke-dasharray", `${summary.health_score}, 100`);
    
    if (summary.health_score >= 80) {
        scoreCircle.className = "text-emerald-500";
        gradeText.innerText = "Chất Lượng Tốt";
        gradeText.className = "text-base font-extrabold text-emerald-600";
    } else if (summary.health_score >= 60) {
        scoreCircle.className = "text-amber-500";
        gradeText.innerText = "Chất Lượng Trung Bình";
        gradeText.className = "text-base font-extrabold text-amber-600";
    } else {
        scoreCircle.className = "text-rose-500";
        gradeText.innerText = "Chất Lượng Kém (Cần duyệt làm sạch)";
        gradeText.className = "text-base font-extrabold text-rose-600";
    }

    // 4 Thống kê
    document.getElementById("diag-dup-count").innerText = `${summary.duplicate_rows} dòng`;
    document.getElementById("diag-null-count").innerText = `${summary.missing_cells.toLocaleString()} ô`;
    document.getElementById("diag-null-pct").innerText = `${summary.missing_percentage}% tổng ô`;
    document.getElementById("diag-outlier-count").innerText = `${summary.outlier_count} giá trị`;
    
    const textIssuesCount = currentProposals.filter(p => p.category.includes("chuỗi") || p.category.includes("kiểu")).length;
    document.getElementById("diag-format-count").innerText = `${textIssuesCount} vấn đề`;

    // Render danh sách đề xuất để người dùng duyệt (Proposal Checklist)
    renderProposalChecklist(currentProposals);
}

function renderProposalChecklist(proposals) {
    const container = document.getElementById("proposals-list");
    if (!proposals || proposals.length === 0) {
        container.innerHTML = `
            <div class="p-6 rounded-2xl bg-emerald-50 text-emerald-800 text-center text-xs font-semibold">
                <i class="fas fa-check-circle text-base mb-1 block text-emerald-600"></i>
                Dữ liệu hoàn hảo! Không phát hiện lỗi cần làm sạch.
            </div>
        `;
        return;
    }

    container.innerHTML = proposals.map((p, idx) => {
        // Badges màu theo danh mục
        let badgeColor = "bg-slate-100 text-slate-700";
        if (p.category.includes("Trùng lặp")) badgeColor = "bg-rose-100 text-rose-800";
        else if (p.category.includes("khuyết")) badgeColor = "bg-amber-100 text-amber-800";
        else if (p.category.includes("ngoại lai")) badgeColor = "bg-indigo-100 text-indigo-800";
        else if (p.category.includes("chuỗi") || p.category.includes("kiểu")) badgeColor = "bg-teal-100 text-teal-800";

        // Render options select dropdown
        const optionsHtml = p.options.map(opt => `
            <option value="${opt.id}" ${opt.id === p.selected_option ? 'selected' : ''}>${opt.label}</option>
        `).join("");

        return `
            <div class="proposal-card bg-slate-50/80 hover:bg-slate-100/70 p-4 rounded-2xl border border-slate-200 transition space-y-3" id="prop-card-${p.action_id}">
                <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div class="flex items-start gap-3">
                        <input type="checkbox" id="check-${p.action_id}" ${p.approved ? 'checked' : ''} onchange="onProposalToggle('${p.action_id}', this.checked)" class="mt-1 w-4 h-4 text-brand-600 rounded border-slate-300 focus:ring-brand-500 cursor-pointer">
                        <div>
                            <div class="flex items-center gap-2 mb-1">
                                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${badgeColor}">${p.category}</span>
                                <h4 class="font-bold text-xs text-slate-900">${p.target_col ? `Cột [${p.target_col}]` : 'Toàn tập dữ liệu'}</h4>
                            </div>
                            <p class="text-xs text-slate-600">${p.issue_desc}</p>
                            <p class="text-xs text-brand-700 font-medium mt-0.5"><i class="fas fa-robot text-brand-500 mr-1"></i>Đề xuất AI: ${p.proposed_action}</p>
                        </div>
                    </div>
                    <div class="text-right shrink-0">
                        <span class="inline-block px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[11px] font-mono font-semibold text-slate-700 shadow-2xs">
                            ${p.impact_estimate}
                        </span>
                    </div>
                </div>

                <!-- Tùy chỉnh tham số duyệt -->
                <div class="pt-2 border-t border-slate-200/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                    <label class="text-slate-500 font-medium flex items-center gap-1.5">
                        <i class="fas fa-sliders text-slate-400"></i> Phương pháp thực thi phê duyệt:
                    </label>
                    <select onchange="onProposalOptionChange('${p.action_id}', this.value)" class="px-3 py-1.5 rounded-xl border border-slate-300 bg-white text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500">
                        ${optionsHtml}
                    </select>
                </div>
            </div>
        `;
    }).join("");
}

function onProposalToggle(actionId, checked) {
    const item = currentProposals.find(p => p.action_id === actionId);
    if (item) item.approved = checked;
}

function onProposalOptionChange(actionId, newOption) {
    const item = currentProposals.find(p => p.action_id === actionId);
    if (item) item.selected_option = newOption;
}

function toggleAllProposals(state) {
    currentProposals.forEach(p => {
        p.approved = state;
        const cb = document.getElementById(`check-${p.action_id}`);
        if (cb) cb.checked = state;
    });
}

// NGƯỜI DÙNG DUYỆT VÀ ÁP DỤNG LÀM SẠCH (Human-in-the-Loop Execution)
async function executeApprovedCleaning() {
    const btn = document.getElementById("btn-approve-clean");
    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-1"></i> Đang áp dụng các hành động đã duyệt...`;

    try {
        const payload = { actions: currentProposals };
        const res = await fetch("/api/clean/approve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.status === "success") {
            hasCleanedData = true;
            document.getElementById("step-btn-2").classList.add("completed");
            showToast("Đã duyệt và áp dụng làm sạch thành công!", "success");

            // Hiển thị phần kết quả so sánh trước vs sau
            renderCleaningComparison(data.comparison, data.preview, data.columns);
            
            // Cuộn xuống phần kết quả
            document.getElementById("cleaning-result-container").scrollIntoView({ behavior: 'smooth' });
        } else {
            showToast(data.detail || "Lỗi khi áp dụng làm sạch", "error");
        }
    } catch (err) {
        showToast("Lỗi: " + err.message, "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fas fa-check-circle"></i> Duyệt & Áp Dụng Làm Sạch Ngay`;
    }
}

function renderCleaningComparison(comp, previewData, columns) {
    const container = document.getElementById("cleaning-result-container");
    container.classList.remove("hidden");

    const before = comp.before;
    const after = comp.after;

    const cardsContainer = document.getElementById("before-after-cards");
    cardsContainer.innerHTML = `
        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
            <div class="text-[11px] text-slate-500 font-semibold mb-1">Số Dòng Dữ Liệu</div>
            <div class="text-lg font-bold text-slate-900">${after.rows.toLocaleString()}</div>
            <div class="text-[11px] text-slate-400 mt-0.5">Trước: ${before.rows.toLocaleString()} dòng</div>
        </div>
        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
            <div class="text-[11px] text-slate-500 font-semibold mb-1">Trùng Lặp Đã Xóa</div>
            <div class="text-lg font-bold text-emerald-600">${before.duplicates} &rarr; ${after.duplicates}</div>
            <div class="text-[11px] text-emerald-700 mt-0.5"><i class="fas fa-check mr-1"></i>Sạch 100%</div>
        </div>
        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
            <div class="text-[11px] text-slate-500 font-semibold mb-1">Ô Khuyết Đã Xử Lý</div>
            <div class="text-lg font-bold text-emerald-600">${before.null_cells} &rarr; ${after.null_cells}</div>
            <div class="text-[11px] text-emerald-700 mt-0.5"><i class="fas fa-check mr-1"></i>Đã điền đại diện</div>
        </div>
        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
            <div class="text-[11px] text-slate-500 font-semibold mb-1">Điểm Sức Khỏe Mới</div>
            <div class="text-lg font-bold text-emerald-600">${after.health_score}/100</div>
            <div class="text-[11px] text-brand-600 font-semibold mt-0.5">+${Math.round((after.health_score - before.health_score) * 10) / 10}đ so với ban đầu</div>
        </div>
    `;

    // Render bảng xem trước dữ liệu sạch
    const table = document.getElementById("cleaned-preview-table");
    const ths = columns.map(c => `<th class="py-2.5 px-3 bg-slate-50 font-bold text-slate-700 border-b border-slate-200">${c}</th>`).join("");
    const trs = previewData.map(row => {
        const tds = columns.map(col => `<td class="py-2 px-3 border-b border-slate-100 text-slate-600">${row[col]}</td>`).join("");
        return `<tr class="hover:bg-slate-50/50">${tds}</tr>`;
    }).join("");
    table.innerHTML = `<thead><tr>${ths}</tr></thead><tbody>${trs}</tbody>`;
}

// ================= BƯỚC 3: PHÂN TÍCH CHUYÊN SÂU & AI AGENT =================
async function runDeepAnalysis() {
    const btn = document.getElementById("btn-re-analyze");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-1"></i> Đang phân tích...`;
    }

    try {
        const res = await fetch("/api/analyze", { method: "POST" });
        const data = await res.json();

        if (res.ok && data.status === "success") {
            document.getElementById("step-btn-3").classList.add("completed");
            renderKpiCards(data.kpi_cards);
            renderCharts(data.charts);
        } else {
            showToast(data.detail || "Không thể thực hiện phân tích", "error");
        }
    } catch (err) {
        console.error("Lỗi phân tích sâu:", err);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-sync-alt"></i> Phân Tích Lại`;
        }
    }
}

function renderKpiCards(kpis) {
    const container = document.getElementById("kpi-cards-container");
    if (!container || !kpis) return;

    container.innerHTML = kpis.map(k => `
        <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center text-xl shrink-0">
                <i class="fas ${k.icon}"></i>
            </div>
            <div>
                <div class="text-xs text-slate-500 font-medium">${k.title}</div>
                <div class="text-xl sm:text-2xl font-black text-slate-900 mt-0.5">${k.value}</div>
                <div class="text-[11px] text-slate-400 mt-0.5">${k.sub}</div>
            </div>
        </div>
    `).join("");
}

function renderCharts(charts) {
    const chartMap = {
        "correlation_heatmap": "chart-tab3-corr",
        "distribution": "chart-tab3-dist",
        "categorical_breakdown": "chart-tab3-cat",
        "scatter_relation": "chart-tab3-scatter"
    };

    Object.entries(chartMap).forEach(([chartKey, elId]) => {
        const el = document.getElementById(elId);
        if (!el) return;

        if (charts[chartKey]) {
            const data = charts[chartKey].data;
            const layout = charts[chartKey].layout;
            layout.autosize = true;
            layout.height = 300;
            layout.margin = { l: 30, r: 20, t: 30, b: 30 };
            Plotly.newPlot(el, data, layout, { responsive: true, displayModeBar: false });
        } else {
            el.innerHTML = `<div class="h-full flex items-center justify-center text-xs text-slate-400 italic">Không đủ dữ liệu cho biểu đồ này</div>`;
        }
    });
}

// ================= AI CHAT Q&A =================
async function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const msg = input.value.trim();
    if (!msg) return;

    appendChatMessage("user", msg);
    input.value = "";

    const btn = document.getElementById("btn-chat-send");
    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i>`;

    try {
        const res = await fetch("/api/agent/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        appendChatMessage("agent", data.reply || "Xin lỗi, không có phản hồi.");
    } catch (err) {
        appendChatMessage("agent", "Lỗi kết nối: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>Gửi</span> <i class="fas fa-paper-plane text-[10px]"></i>`;
    }
}

function sendQuickPrompt(promptText) {
    document.getElementById("chat-input").value = promptText;
    document.getElementById("chat-input").focus();
}

function appendChatMessage(sender, text) {
    const chatContainer = document.getElementById("chat-messages");
    if (!chatContainer) return;

    // Convert newlines to breaks and simple bolding
    const formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');

    const bubble = document.createElement("div");
    bubble.className = "flex items-start gap-3 " + (sender === "user" ? "flex-row-reverse" : "");

    if (sender === "user") {
        bubble.innerHTML = `
            <div class="w-7 h-7 rounded-lg bg-slate-800 text-white flex items-center justify-center text-xs shrink-0 mt-0.5">
                <i class="fas fa-user"></i>
            </div>
            <div class="bg-brand-600 text-white p-3 rounded-2xl rounded-tr-none text-xs shadow-2xs max-w-xl leading-relaxed">
                ${formatted}
            </div>
        `;
    } else {
        bubble.innerHTML = `
            <div class="w-7 h-7 rounded-lg bg-brand-600 text-white flex items-center justify-center text-xs shrink-0 mt-0.5">
                <i class="fas fa-robot"></i>
            </div>
            <div class="bg-white p-3.5 rounded-2xl rounded-tl-none border border-slate-200 text-xs text-slate-700 shadow-2xs max-w-xl leading-relaxed">
                ${formatted}
            </div>
        `;
    }

    chatContainer.appendChild(bubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ================= BƯỚC 4: BÁO CÁO HTML TRỰC TIẾP =================
function reloadReport() {
    const iframe = document.getElementById("report-iframe");
    const spinner = document.getElementById("iframe-spinner");
    if (!iframe) return;

    if (spinner) spinner.classList.remove("hidden");
    iframe.src = "/api/report/html?t=" + new Date().getTime();

    iframe.onload = () => {
        if (spinner) spinner.classList.add("hidden");
        document.getElementById("step-btn-4").classList.add("completed");
    };
}

function printReportIframe() {
    const iframe = document.getElementById("report-iframe");
    if (iframe && iframe.contentWindow) {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
    }
}

// ================= MODAL API KEY =================
function openApiKeyModal() {
    document.getElementById("apikey-modal").classList.remove("hidden");
}

function closeApiKeyModal() {
    document.getElementById("apikey-modal").classList.add("hidden");
}

async function saveApiKey() {
    const input = document.getElementById("modal-api-key-input");
    const key = input.value.trim();

    try {
        const res = await fetch("/api/settings/apikey", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ api_key: key })
        });
        const data = await res.json();
        if (res.ok) {
            showToast("Đã lưu API Key thành công!", "success");
            closeApiKeyModal();
            updateApiKeyBadge(data.has_api_key);
        }
    } catch (err) {
        showToast("Lỗi lưu API Key: " + err.message, "error");
    }
}

function updateApiKeyBadge(hasKey) {
    const badge = document.getElementById("api-status-text");
    if (hasKey) {
        badge.innerHTML = `<span class="text-emerald-600 font-bold">Gemini Đang Bật</span>`;
    } else {
        badge.innerText = "Cài đặt Gemini";
    }
}

// ================= UTILITIES =================
function showUploadSpinner(show) {
    const spinner = document.getElementById("upload-spinner");
    if (spinner) {
        if (show) spinner.classList.remove("hidden");
        else spinner.classList.add("hidden");
    }
}

function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    const toastMsg = document.getElementById("toast-msg");
    const toastIcon = document.getElementById("toast-icon");
    if (!toast || !toastMsg) return;

    toastMsg.innerText = message;
    if (type === "success") {
        toastIcon.className = "fas fa-check-circle text-emerald-400 text-base";
    } else if (type === "error") {
        toastIcon.className = "fas fa-exclamation-circle text-rose-400 text-base";
    } else {
        toastIcon.className = "fas fa-info-circle text-brand-400 text-base";
    }

    toast.classList.remove("hidden");
    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3500);
}

function checkInitialState() {
    // Check if server already has dataset loaded
    fetch("/api/diagnose").then(r => r.json()).then(data => {
        if (data.status === "success" && data.diagnosis) {
            handleDataLoaded({
                dataset_name: data.dataset_name,
                diagnosis: data.diagnosis,
                columns: [],
                preview: [],
                rows: data.diagnosis.summary.total_rows,
                cols: data.diagnosis.summary.total_cols
            });
        }
    }).catch(() => {});
}
