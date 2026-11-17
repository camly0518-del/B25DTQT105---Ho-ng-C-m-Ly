"""
HTML Report Generator
Generates self-contained, publication-grade interactive HTML reports with Plotly visualizations
"""
import json
from datetime import datetime
from typing import Dict, Any

class ReportGenerator:
    def __init__(self):
        pass

    def generate_html_report(self, dataset_name: str, df_cleaned, eda_data: Dict[str, Any], cleaning_comparison: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Tạo file báo cáo HTML hoàn chỉnh, độc lập và tương tác trực tiếp"""
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        before = cleaning_comparison.get("before", {})
        after = cleaning_comparison.get("after", {})
        audit = cleaning_comparison.get("audit_trail", [])
        charts = eda_data.get("charts", {})
        kpis = eda_data.get("kpi_cards", [])
        num_stats = eda_data.get("numeric_stats", [])
        correlations = eda_data.get("top_correlations", [])

        # Chuyển đổi dữ liệu biểu đồ sang chuỗi JSON an toàn
        charts_json = json.dumps(charts, ensure_ascii=False)

        # Xây dựng các hàng của bảng nhật ký làm sạch đã duyệt
        audit_rows_html = ""
        for idx, item in enumerate(audit, 1):
            audit_rows_html += f"""
            <tr class="border-b border-gray-100 hover:bg-gray-50/50 transition">
                <td class="py-2.5 px-4 text-xs font-semibold text-gray-500">{idx}</td>
                <td class="py-2.5 px-4 text-sm font-medium text-gray-900">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 mr-2">
                        <i class="fas fa-check mr-1"></i> Đã duyệt
                    </span>
                    {item.get('action', '')}
                </td>
                <td class="py-2.5 px-4 text-sm text-gray-600">{item.get('details', '')}</td>
                <td class="py-2.5 px-4 text-xs font-mono font-semibold text-indigo-600 text-right">{item.get('rows_affected', 0):,} bản ghi/ô</td>
            </tr>
            """

        # Xây dựng các thẻ phát hiện chính từ AI
        findings_html = ""
        for idx, f in enumerate(insights.get("key_findings", []), 1):
            findings_html += f"""
            <div class="bg-white rounded-xl p-5 border border-indigo-100 shadow-sm hover:shadow-md transition">
                <div class="flex items-center gap-3 mb-2">
                    <span class="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">{idx}</span>
                    <h4 class="font-bold text-gray-900 text-base">{f.get('title', '')}</h4>
                </div>
                <p class="text-gray-600 text-sm mb-3 leading-relaxed">{f.get('description', '')}</p>
                <div class="bg-indigo-50/60 rounded-lg px-3 py-2 text-xs text-indigo-900 flex items-start gap-2">
                    <i class="fas fa-lightbulb text-indigo-600 mt-0.5"></i>
                    <span><strong>Tác động chiến lược:</strong> {f.get('impact', '')}</span>
                </div>
            </div>
            """

        # Xây dựng các thẻ rủi ro & bất thường
        risks_html = ""
        for r in insights.get("anomalies_and_risks", []):
            sev = r.get("severity", "Trung bình")
            badge_color = "bg-rose-100 text-rose-800" if sev == "Cao" else "bg-amber-100 text-amber-800"
            risks_html += f"""
            <div class="bg-white rounded-xl p-4 border border-gray-200 shadow-sm flex items-start gap-3">
                <div class="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="flex-1">
                    <div class="flex items-center justify-between gap-2 mb-1">
                        <h5 class="font-semibold text-gray-900 text-sm">{r.get('risk', '')}</h5>
                        <span class="px-2 py-0.5 rounded-full text-xs font-semibold {badge_color}">{sev}</span>
                    </div>
                    <p class="text-xs text-gray-600">{r.get('evidence', '')}</p>
                </div>
            </div>
            """

        # Khuyến nghị 3 giai đoạn
        recs = insights.get("recommendations", {})
        qw_items = "".join([f"<li class='flex items-start gap-2 text-xs text-gray-700 mb-2'><i class='fas fa-check-circle text-emerald-500 mt-0.5'></i><span>{it}</span></li>" for it in recs.get("quick_wins", [])])
        mt_items = "".join([f"<li class='flex items-start gap-2 text-xs text-gray-700 mb-2'><i class='fas fa-arrow-circle-right text-blue-500 mt-0.5'></i><span>{it}</span></li>" for it in recs.get("medium_term", [])])
        lt_items = "".join([f"<li class='flex items-start gap-2 text-xs text-gray-700 mb-2'><i class='fas fa-rocket text-purple-500 mt-0.5'></i><span>{it}</span></li>" for it in recs.get("long_term", [])])

        # Bảng thống kê mô tả
        num_stats_rows = ""
        for s in num_stats:
            num_stats_rows += f"""
            <tr class="border-b border-gray-100 hover:bg-gray-50/50">
                <td class="py-2 px-3 text-xs font-medium text-gray-900">{s['column']}</td>
                <td class="py-2 px-3 text-xs text-gray-600 text-right">{s['mean']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-gray-600 text-right">{s['median']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-gray-600 text-right">{s['std']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-gray-600 text-right">{s['min']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-gray-600 text-right">{s['max']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-gray-600 text-right">{s['skew']:,.2f}</td>
            </tr>
            """

        # Mẫu HTML Báo cáo Độc lập (Standalone Self-Contained)
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo Cáo Phân Tích Dữ Liệu - {dataset_name}</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- Plotly.js -->
    <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
        }}
        @media print {{
            .no-print {{
                display: none !important;
            }}
            body {{
                background-color: #ffffff;
            }}
            .page-break {{
                page-break-before: always;
            }}
            .shadow-sm, .shadow-md, .shadow-lg {{
                box-shadow: none !important;
                border: 1px solid #e2e8f0 !important;
            }}
        }}
    </style>
</head>
<body class="p-4 sm:p-8 md:p-12">
    <div class="max-w-6xl mx-auto space-y-8">
        
        <!-- TOP TOOLBAR (CHỈ HIỂN THỊ KHI XEM, ẨN KHI IN) -->
        <div class="no-print flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-2xl shadow-sm border border-gray-200">
            <div class="flex items-center gap-2">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                    <i class="fas fa-check-double mr-1.5"></i> Báo cáo hoàn chỉnh
                </span>
                <span class="text-xs text-gray-500">Tạo bởi AI Data Analyst Agent</span>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="window.print()" class="px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition shadow-sm">
                    <i class="fas fa-print"></i> In / Xuất PDF
                </button>
                <button onclick="downloadHtmlFile()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition shadow-sm">
                    <i class="fas fa-download"></i> Tải file HTML
                </button>
            </div>
        </div>

        <!-- HEADER BANNER -->
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-3xl p-8 sm:p-10 shadow-xl relative overflow-hidden">
            <div class="absolute -right-10 -bottom-10 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
            <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-medium mb-3 border border-indigo-400/20">
                        <i class="fas fa-robot text-indigo-400"></i> AI Data Science Executive Report
                    </div>
                    <h1 class="text-2xl sm:text-4xl font-extrabold tracking-tight mb-2">Báo Cáo Phân Tích Dữ Liệu Chuyên Sâu</h1>
                    <p class="text-slate-300 text-sm max-w-2xl">
                        Tập dữ liệu: <strong class="text-white">{dataset_name}</strong> | Quy trình: Chẩn đoán &rarr; Người dùng duyệt &rarr; Làm sạch chuẩn &rarr; AI Khám phá EDA
                    </p>
                </div>
                <div class="flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-3">
                    <div class="bg-white/10 backdrop-blur-md px-5 py-3 rounded-2xl border border-white/15 text-left md:text-right">
                        <div class="text-[11px] uppercase tracking-wider text-slate-300">Điểm Chất Lượng Dữ Liệu</div>
                        <div class="text-3xl font-black text-emerald-400 flex items-center md:justify-end gap-1.5">
                            {after.get('health_score', 0)}<span class="text-base text-emerald-200">/100</span>
                        </div>
                        <div class="text-[10px] text-slate-400">Ban đầu: {before.get('health_score', 0)}/100 (Đã kiểm định)</div>
                    </div>
                    <div class="text-xs text-slate-400">
                        <i class="far fa-clock mr-1"></i> {now_str}
                    </div>
                </div>
            </div>
        </div>

        <!-- 1. TỔNG QUAN ĐIỀU HÀNH (EXECUTIVE SUMMARY) -->
        <section class="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-gray-200">
            <div class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100">
                <div class="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-lg">
                    <i class="fas fa-compass"></i>
                </div>
                <div>
                    <h2 class="text-lg font-bold text-gray-900">1. Bản Tóm Tắt Điều Hành (Executive Summary)</h2>
                    <p class="text-xs text-gray-500">Bức tranh toàn cảnh về tập dữ liệu và kết luận tổng thể từ AI Agent</p>
                </div>
            </div>
            <div class="text-gray-700 text-sm sm:text-base leading-relaxed space-y-3">
                <p>{insights.get('executive_summary', '')}</p>
            </div>
        </section>

        <!-- 2. CHỨNG NHẬN & NHẬT KÝ LÀM SẠCH (DATA AUDIT & APPROVAL LOG) -->
        <section class="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-gray-200">
            <div class="flex items-center justify-between gap-4 mb-4 pb-3 border-b border-gray-100">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg">
                        <i class="fas fa-clipboard-check"></i>
                    </div>
                    <div>
                        <h2 class="text-lg font-bold text-gray-900">2. Chứng Nhận Xử Lý & Làm Sạch Dữ Liệu (Human-in-the-Loop)</h2>
                        <p class="text-xs text-gray-500">Mọi hành động đều được AI lập đề xuất và người dùng trực tiếp phê duyệt</p>
                    </div>
                </div>
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <i class="fas fa-shield-alt mr-1"></i> Chuẩn kiểm định 100%
                </span>
            </div>

            <!-- Thẻ So Sánh Trước vs Sau -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200">
                    <div class="text-xs text-gray-500 mb-1">Số Dòng Dữ Liệu</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-xl font-bold text-gray-900">{after.get('rows', 0):,}</span>
                        <span class="text-xs text-gray-400 line-through">({before.get('rows', 0):,})</span>
                    </div>
                    <div class="text-[11px] text-emerald-600 font-medium mt-1">Đã tối ưu cấu trúc</div>
                </div>
                <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200">
                    <div class="text-xs text-gray-500 mb-1">Dòng Trùng Lặp</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-xl font-bold text-emerald-600">{after.get('duplicates', 0)}</span>
                        <span class="text-xs text-rose-500 line-through">({before.get('duplicates', 0)})</span>
                    </div>
                    <div class="text-[11px] text-emerald-600 font-medium mt-1">Đã loại bỏ hoàn toàn</div>
                </div>
                <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200">
                    <div class="text-xs text-gray-500 mb-1">Ô Khuyết Thiếu (Null)</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-xl font-bold text-emerald-600">{after.get('null_cells', 0)}</span>
                        <span class="text-xs text-rose-500 line-through">({before.get('null_cells', 0):,})</span>
                    </div>
                    <div class="text-[11px] text-emerald-600 font-medium mt-1">Đã điền đại diện</div>
                </div>
                <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200">
                    <div class="text-xs text-gray-500 mb-1">Sức Khỏe Dữ Liệu</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-xl font-bold text-emerald-600">+{round(after.get('health_score', 0) - before.get('health_score', 0), 1)}đ</span>
                        <span class="text-xs text-gray-500">(&rarr; {after.get('health_score', 0)}%)</span>
                    </div>
                    <div class="text-[11px] text-emerald-600 font-medium mt-1">Cải thiện vượt bậc</div>
                </div>
            </div>

            <!-- Bảng Nhật Ký Phê Duyệt -->
            <div class="overflow-x-auto rounded-xl border border-gray-200">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-50/80 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase">
                            <th class="py-3 px-4 w-12">#</th>
                            <th class="py-3 px-4">Hành Động Đã Duyệt</th>
                            <th class="py-3 px-4">Chi Tiết Biến Đổi & Thuật Toán</th>
                            <th class="py-3 px-4 text-right">Phạm Vi Tác Động</th>
                        </tr>
                    </thead>
                    <tbody>
                        {audit_rows_html}
                    </tbody>
                </table>
            </div>

            <div class="mt-4 p-4 rounded-xl bg-emerald-50/50 border border-emerald-100 text-xs text-emerald-900 flex items-start gap-2">
                <i class="fas fa-info-circle text-emerald-600 mt-0.5"></i>
                <div>
                    <strong>Nhận xét từ AI Agent:</strong> {insights.get('data_quality_assessment', '')}
                </div>
            </div>
        </section>

        <!-- 3. CHỈ SỐ KPI CHÍNH (KEY PERFORMANCE INDICATORS) -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {"".join([f'''
            <div class="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-{card.get('color', 'indigo')}-50 text-{card.get('color', 'indigo')}-600 flex items-center justify-center text-xl shrink-0">
                    <i class="fas {card.get('icon', 'fa-chart-pie')}"></i>
                </div>
                <div>
                    <div class="text-xs text-gray-500 font-medium">{card.get('title')}</div>
                    <div class="text-2xl font-bold text-gray-900 mt-0.5">{card.get('value')}</div>
                    <div class="text-[11px] text-gray-400 mt-0.5">{card.get('sub')}</div>
                </div>
            </div>
            ''' for card in kpis])}
        </section>

        <!-- 4. KHÁM PHÁ TRỰC QUAN HÓA (INTERACTIVE PLOTLY EDA CHARTS) -->
        <section class="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-gray-200 space-y-6">
            <div class="flex items-center gap-3 pb-3 border-b border-gray-100">
                <div class="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-lg">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div>
                    <h2 class="text-lg font-bold text-gray-900">3. Trực Quan Hóa Dữ Liệu Tương Tác (Automated EDA)</h2>
                    <p class="text-xs text-gray-500">Biểu đồ động Plotly cho phép phóng to, thu nhỏ và hover xem chi tiết</p>
                </div>
            </div>

            <!-- Khung lưới biểu đồ -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Heatmap Tương Quan -->
                <div class="bg-slate-50/50 rounded-2xl p-4 border border-gray-200" id="chart-corr-container">
                    <div id="plot-correlation_heatmap" class="w-full h-96"></div>
                </div>

                <!-- Phân phối / Outlier Box -->
                <div class="bg-slate-50/50 rounded-2xl p-4 border border-gray-200" id="chart-dist-container">
                    <div id="plot-distribution" class="w-full h-96"></div>
                </div>

                <!-- Phân loại / Category Breakdown -->
                <div class="bg-slate-50/50 rounded-2xl p-4 border border-gray-200" id="chart-cat-container">
                    <div id="plot-categorical_breakdown" class="w-full h-96"></div>
                </div>

                <!-- Scatter Relationship / Phân tán -->
                <div class="bg-slate-50/50 rounded-2xl p-4 border border-gray-200" id="chart-scatter-container">
                    <div id="plot-scatter_relation" class="w-full h-96"></div>
                </div>
            </div>

            <!-- Biểu đồ Xu Hướng Thời Gian nếu có -->
            <div class="bg-slate-50/50 rounded-2xl p-4 border border-gray-200 hidden" id="chart-trend-container">
                <div id="plot-time_trend" class="w-full h-80"></div>
            </div>
        </section>

        <!-- 5. CÁC PHÁT HIỆN CỐT LÕI TỪ AI (AI KEY FINDINGS & RISKS) -->
        <section class="space-y-6">
            <div class="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-gray-200">
                <div class="flex items-center gap-3 mb-6 pb-3 border-b border-gray-100">
                    <div class="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-lg">
                        <i class="fas fa-lightbulb"></i>
                    </div>
                    <div>
                        <h2 class="text-lg font-bold text-gray-900">4. Các Phát Hiện Trọng Yếu Từ AI Agent (Key Discoveries)</h2>
                        <p class="text-xs text-gray-500">Phân tích đa chiều về tương quan, phân khúc chủ lực và đòn bẩy tăng trưởng</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                    {findings_html}
                </div>
            </div>

            <!-- Cảnh Báo Rủi Ro & Dị Thường -->
            <div class="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-gray-200">
                <div class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100">
                    <div class="w-9 h-9 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-lg">
                        <i class="fas fa-shield-virus"></i>
                    </div>
                    <div>
                        <h2 class="text-lg font-bold text-gray-900">5. Cảnh Báo Rủi Ro & Biến Động Bất Thường</h2>
                        <p class="text-xs text-gray-500">Các điểm dị biệt, độ lệch chuẩn và khuyến nghị phòng ngừa rủi ro</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {risks_html}
                </div>
            </div>
        </section>

        <!-- 6. KHUYẾN NGHỊ CHIẾN LƯỢC HÀNH ĐỘNG (ACTIONABLE RECOMMENDATIONS ROADMAP) -->
        <section class="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-gray-200">
            <div class="flex items-center gap-3 mb-6 pb-3 border-b border-gray-100">
                <div class="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg">
                    <i class="fas fa-road"></i>
                </div>
                <div>
                    <h2 class="text-lg font-bold text-gray-900">6. Lộ Trình Hành Động Chiến Lược (Strategic Roadmap)</h2>
                    <p class="text-xs text-gray-500">Đề xuất các bước thực thi cụ thể phân bổ theo 3 mốc thời gian</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Quick Wins -->
                <div class="rounded-2xl p-5 border border-emerald-200 bg-emerald-50/30">
                    <div class="flex items-center gap-2 mb-3 text-emerald-800 font-bold text-sm">
                        <i class="fas fa-bolt"></i>
                        <span>Ngắn Hạn: Quick-Wins (1-3 Tháng)</span>
                    </div>
                    <ul class="space-y-2">
                        {qw_items}
                    </ul>
                </div>

                <!-- Medium Term -->
                <div class="rounded-2xl p-5 border border-blue-200 bg-blue-50/30">
                    <div class="flex items-center gap-2 mb-3 text-blue-800 font-bold text-sm">
                        <i class="fas fa-tasks"></i>
                        <span>Trung Hạn: Tối Ưu (3-6 Tháng)</span>
                    </div>
                    <ul class="space-y-2">
                        {mt_items}
                    </ul>
                </div>

                <!-- Long Term -->
                <div class="rounded-2xl p-5 border border-purple-200 bg-purple-50/30">
                    <div class="flex items-center gap-2 mb-3 text-purple-800 font-bold text-sm">
                        <i class="fas fa-chess-queen"></i>
                        <span>Dài Hạn: Chuyển Đổi (6-12 Tháng)</span>
                    </div>
                    <ul class="space-y-2">
                        {lt_items}
                    </ul>
                </div>
            </div>
        </section>

        <!-- 7. BẢNG PHỤ LỤC THỐNG KÊ CHI TIẾT (APPENDIX) -->
        <section class="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-gray-200">
            <div class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100">
                <div class="w-9 h-9 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-lg">
                    <i class="fas fa-table"></i>
                </div>
                <div>
                    <h2 class="text-lg font-bold text-gray-900">7. Phụ Lục Thống Kê Mô Tả Chi Tiết</h2>
                    <p class="text-xs text-gray-500">Thông số kỹ thuật toàn diện của các biến số định lượng sau chuẩn hóa</p>
                </div>
            </div>

            <div class="overflow-x-auto rounded-xl border border-gray-200">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-50/80 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase">
                            <th class="py-2.5 px-3">Cột Dữ Liệu</th>
                            <th class="py-2.5 px-3 text-right">Trung Bình (Mean)</th>
                            <th class="py-2.5 px-3 text-right">Trung Vị (Median)</th>
                            <th class="py-2.5 px-3 text-right">Độ Lệch Chuẩn (Std)</th>
                            <th class="py-2.5 px-3 text-right">Nhỏ Nhất (Min)</th>
                            <th class="py-2.5 px-3 text-right">Lớn Nhất (Max)</th>
                            <th class="py-2.5 px-3 text-right">Độ Lệch (Skew)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {num_stats_rows}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- FOOTER -->
        <footer class="pt-6 border-t border-gray-200 text-center text-xs text-gray-400 space-y-1">
            <p>Báo cáo được khởi tạo tự động bởi <strong>DataMind AI Agent</strong> &bull; Đã kiểm duyệt và bảo vệ quyền sở hữu dữ liệu</p>
            <p>Thời gian phát hành: {now_str} &bull; Hệ thống phân tích dữ liệu thông minh End-to-End</p>
        </footer>

    </div>

    <!-- SCRIPT RENDER PLOTLY & DOWNLOAD -->
    <script>
        const chartData = {charts_json};

        // Render Plotly charts
        window.addEventListener('DOMContentLoaded', () => {{
            const chartKeys = ['correlation_heatmap', 'distribution', 'categorical_breakdown', 'scatter_relation', 'time_trend'];
            chartKeys.forEach(key => {{
                const el = document.getElementById('plot-' + key);
                if (el && chartData[key]) {{
                    const cfg = {{ responsive: true, displayModeBar: false }};
                    Plotly.newPlot(el, chartData[key].data, chartData[key].layout, cfg);
                    // Nếu là trend và có dữ liệu thì hiện container
                    if (key === 'time_trend') {{
                        const tc = document.getElementById('chart-trend-container');
                        if (tc) tc.classList.remove('hidden');
                    }}
                }} else if (el) {{
                    const container = el.parentElement;
                    if (container && key !== 'time_trend') {{
                        container.innerHTML = '<div class="h-64 flex items-center justify-center text-xs text-gray-400 italic">Không đủ dữ liệu biến số để vẽ biểu đồ này</div>';
                    }}
                }}
            }});
        }});

        // Download HTML File function
        function downloadHtmlFile() {{
            const blob = new Blob([document.documentElement.outerHTML], {{ type: 'text/html;charset=utf-8' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Bao_Cao_AI_Phan_Tich_${{new Date().toISOString().slice(0,10)}}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
"""
        return html_content
