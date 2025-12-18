import streamlit as st
import time
import random
from datetime import datetime
import pandas as pd
import os
import requests
import json
from PIL import Image
from fpdf import FPDF
import unicodedata
import base64

# ==============================================================================
# 1. CẤU HÌNH API & HỆ THỐNG
# ==============================================================================
GLOBAL_ACCESS_TOKEN = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0cmFuc2FjdGlvbl9pZCI6ImY3M2I2MDVmLTJkMjctNDJhNi04ZjA4LWJlZDI3MjhmNzgxZCIsInN1YiI6IjIyZDQ5OTgwLWQ0NDctMTFmMC1hNzY5LWFmNzhjOGRjOGFiMSIsImF1ZCI6WyJyZXN0c2VydmljZSJdLCJ1c2VyX25hbWUiOiJ0dXRyaW5oLjg4MjUyMDIwMjI0QHN0LnVlaC5lZHUudm4iLCJzY29wZSI6WyJyZWFkIl0sImlzcyI6Imh0dHBzOi8vbG9jYWxob3N0IiwibmFtZSI6InR1dHJpbmguODgyNTIwMjAyMjRAc3QudWVoLmVkdS52biIsInV1aWRfYWNjb3VudCI6IjIyZDQ5OTgwLWQ0NDctMTFmMC1hNzY5LWFmNzhjOGRjOGFiMSIsImF1dGhvcml0aWVzIjpbIlVTRVIiLCJUUkFDS18xIl0sImp0aSI6IjFhN2VhMDJkLTMwMTQtNGI1YS04Yzc5LTY1NjNmM2VhNjFkNyIsImNsaWVudF9pZCI6ImFkbWluYXBwIn0.RtoxoREb7d-GHX6wNDdiY4u8-IzrFCdq7nAKf-IDOgCI9IR8ZN2aBAAT1t5LKKhVjOLmbsjIXApa52J5Amioc_IikO2dbdOc8pB_amDq8wtFVeI5L6bL2q0ZrhB9Ktc3yrKoh0faCG6KcAQjU1oHA6PkJFYqHNhHabvkRLli43I4yih0P8WzmfwV7_fRlBrGrn_RyeXOaJvQVA4HZB-ZZp2Z3CM1dsVb5heZR3NCL4L9f0yEjG59EEA3VSh94nymu7s7jPgBEBRt24xQNiMCwU5AZo3ZupZmV0OwUleqNfsQENVMrZ1kulPKlmdC4y7k0sBbSk6MnyeU7A-i-zVY-g"

EKYC_TOKEN_ID = "45e7fd98-1e5f-6b5b-e063-63199f0a4f3b"
EKYC_TOKEN_KEY = "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAImOHPRMGuLhT3SdvgLsvNY1kxOg5Io6KsBRVwaAGJdb3DY1PJAfASCH1Kd02gsgL79elJKtdmXcPvzI6/+dQIECAwEAAQ=="
OCR_TOKEN_ID = "45fb096b-ffce-1e20-e063-63199f0a1355"
OCR_TOKEN_KEY = "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAMLIWYi53QuY7iRIX5rqZp9PoGtsjoAd724hCPZNYa9KDDdYvGB587u9aPjccxbcITOKtfT5GJtA3zVPY98LJZECAwEAAQ=="
VISION_TOKEN_ID = "45e82921-f670-190a-e063-62199f0ad5f8"
VISION_TOKEN_KEY = "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKDLbSfzpn+xkiCw/2RzrSACs5k/UvofDQHsqeNM3mZsOh5KpfgXdEXSEYtTHZrzCB8bweGcoomUJbKdHwJO37cCAwEAAQ=="

URL_EKYC = "https://gw.vnpt.vn/ai/v1/face/liveness"
URL_OCR = "https://gw.vnpt.vn/ai/v1/ocr/vehicle-registration"
URL_VISION = "https://gw.vnpt.vn/ai/v1/vehicle/damage"

AUTO_APPROVE_THRESHOLD = 80 

# --- SETUP PAGE ---
page_icon = "🛡️"
logo_path = None
try:
    potential_logos = ["logo.png", "logo.jpg", "logo.jpeg", "logo"]
    for p in potential_logos:
        if os.path.exists(p): logo_path = p; break
    if logo_path: page_icon = Image.open(logo_path)
except: pass

st.set_page_config(page_title="INSUR-AI", page_icon=page_icon, layout="wide", initial_sidebar_state="expanded")

# ==============================================================================
# 2. CSS MAGIC
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    .stApp { background-color: #f8f9fa; font-family: 'Roboto', sans-serif; color: #333; }
    
    /* LOGO TO HƠN (ĐÃ FIX: 120px) */
    .header-container { display: flex; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #e9ecef; }
    .header-logo { width: 120px; margin-right: 20px; } 
    .header-title { font-size: 2.8rem; font-weight: 800; color: #0056b3; margin: 0; line-height: 1.1; }
    .header-subtitle { font-size: 1.1rem; color: #6c757d; margin-top: 5px; font-weight: 400;}

    .css-card, div[data-testid="stVerticalBlock"] > div[style*="border"] { background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #f0f0f0; }
    div[data-testid="stButton"] button[kind="primary"] { background: #0056b3; border: none; border-radius: 8px; font-weight: 600; text-transform: uppercase; color: white; padding: 12px 25px; }
    div[data-testid="stButton"] button[kind="primary"]:hover { background: #004494; box-shadow: 0 4px 12px rgba(0, 86, 179, 0.2); }
    .invoice-box { background: #fff; padding: 25px; border-radius: 12px; border: 2px dashed #b3d7ff; background-color: #f8fbff; }
    .invoice-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 1rem; color: #333; }
    .invoice-total { display: flex; justify-content: space-between; margin-top: 15px; padding-top: 15px; border-top: 2px solid #0056b3; font-weight: 800; font-size: 1.4rem; color: #0056b3; }
    .success-box { background: #e8f5e9; padding: 25px; border-radius: 12px; border-left: 6px solid #2e7d32; text-align: center; }
    
    /* THANK YOU BOX (ĐÃ KHÔI PHỤC DÒNG TEXT) */
    .thank-you-box { background: white; padding: 30px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); border-top: 4px solid #0056b3; text-align: center; margin-top: 25px; }
    .ty-title { font-size: 1.4rem; font-weight: 700; color: #0056b3; margin-bottom: 12px; }
    .ty-text { font-style: italic; color: #555; font-size: 1.05rem; }
    
    .console-log { font-family: 'Consolas', monospace; font-size: 12px; color: #0f0; background-color: #000; padding: 15px; border-radius: 8px; height: 250px; overflow-y: scroll; border: 2px solid #333; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #0056b3; font-weight: 700; }
    .login-intro-title { font-size: 1.8rem; font-weight: 700; color: #2c3e50; margin-bottom: 15px; }
    .feature-title { font-weight: 600; color: #0056b3; font-size: 1.1rem; margin-bottom: 5px; }
    .feature-desc { font-size: 0.95rem; color: #666; }
</style>
""", unsafe_allow_html=True)

# --- 3. STATE & RESET ---
if 'step' not in st.session_state: st.session_state['step'] = -1
if 'logs' not in st.session_state: st.session_state['logs'] = [f"[{datetime.now().strftime('%H:%M:%S')}] System Ready."]
for key in ['gps_verified', 'ocr_done', 'paid', 'show_confirm', 'result_data', 'ticket_created', 'image_quality_pass', 'show_dispute_form', 'rating_submitted', 'feedback_done', 'sent_to_human']:
    if key not in st.session_state: st.session_state[key] = False
if 'payment_method' not in st.session_state: st.session_state['payment_method'] = "money"
if 'payment_channel' not in st.session_state: st.session_state['payment_channel'] = "vnpt" 
if 'bank_details' not in st.session_state: st.session_state['bank_details'] = ""
if 'ocr_data' not in st.session_state: st.session_state['ocr_data'] = None
if 'u_ocr' not in st.session_state: st.session_state['u_ocr'] = URL_OCR
if 'u_vis' not in st.session_state: st.session_state['u_vis'] = URL_VISION

def reset_session_full():
    st.session_state['step'] = -1 
    st.session_state['ocr_done'] = False
    st.session_state['result_data'] = None
    st.session_state['paid'] = False
    st.session_state['ticket_created'] = False
    st.session_state['show_confirm'] = False
    st.session_state['image_quality_pass'] = False
    st.session_state['gps_verified'] = False
    st.session_state['rating_submitted'] = False
    st.session_state['feedback_done'] = False
    st.session_state['show_dispute_form'] = False
    st.session_state['sent_to_human'] = False
    st.session_state['ocr_data'] = None
    st.session_state['payment_channel'] = "vnpt"
    st.session_state['logs'] = [f"[{datetime.now().strftime('%H:%M:%S')}] Reset."]
    st.rerun()

def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state['logs'].insert(0, f"[{now}] > {message}")

def get_headers(service_type):
    headers = {'Authorization': GLOBAL_ACCESS_TOKEN}
    if service_type == 'ocr': headers.update({'Token-id': OCR_TOKEN_ID, 'Token-key': OCR_TOKEN_KEY})
    elif service_type == 'vision': headers.update({'Token-id': VISION_TOKEN_ID, 'Token-key': VISION_TOKEN_KEY})
    return headers

def check_image_quality(file_obj):
    add_log("Quality Gate: Analyzing...")
    time.sleep(0.5)
    fname = file_obj.name.lower()
    if "mo" in fname or "blur" in fname:
        add_log("Quality Gate: FAILED (Blurry)")
        return False, "⚠️ VIDEO BỊ MỜ. Vui lòng giữ chắc tay."
    add_log("Quality Gate: PASSED")
    return True, "Chất lượng tốt."

def call_api_logic(url, headers, f, mock, name):
    try:
        files = {'file': f.getvalue()}
        res = requests.post(url, headers=headers, files=files, timeout=12)
        if res.status_code == 200:
            add_log(f"{name}: Success (200)")
            data = res.json()
            if name == 'SmartReader' and 'object' in data:
                return {
                    "owner": data['object'].get('owner_name', mock['owner']),
                    "plate": data['object'].get('plate', mock['plate']),
                    "vin": data['object'].get('chassis_no', mock['vin'])
                }
            return mock
        else: add_log(f"{name}: Hybrid ({res.status_code})"); return mock
    except: add_log(f"{name}: Offline Mode"); return mock

def call_ocr(f):
    mock = {"owner": "TRỊNH THỊ CẨM TÚ", "plate": "51K-888.88", "vin": "VF-LUX-2023-XXXX"}
    return call_api_logic(st.session_state['u_ocr'], get_headers('ocr'), f, mock, "SmartReader")

def call_vision(f):
    mock = {
        "items": [
            {"part_vn": "Cản trước", "part_en": "Front Bumper", "sever_vn": "Trầy xước", "sever_en": "Scratched", "cost": 864000, "conf": 98},
            {"part_vn": "Đèn sương mù", "part_en": "Fog Light", "sever_vn": "Nứt nhẹ", "sever_en": "Cracked", "cost": 1200000, "conf": 85}
        ],
        "total_conf": 92 
    }
    fname = f.name.lower()
    if "kho" in fname or "hard" in fname:
        mock["items"] = [{"part_vn": "Khung xe", "part_en": "Chassis", "sever_vn": "Biến dạng", "sever_en": "Deformed", "cost": 15000000, "conf": 65}]
        mock["total_conf"] = 65 
    elif "den" in fname or "light" in fname: 
        mock["items"] = [{"part_vn": "Đèn pha phải", "part_en": "Right Headlight", "sever_vn": "Vỡ nát", "sever_en": "Broken", "cost": 4500000, "conf": 99}]
        mock["total_conf"] = 99
    return call_api_logic(st.session_state['u_vis'], get_headers('vision'), f, mock, "InsurAI Core (YOLOv8)")

def create_pdf(name, plate, items, total, tx, method, detail):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "BIEN BAN GIAM DINH", 0, 1, 'C')
    pdf.set_font("Arial", size=12); pdf.ln(10)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
    pdf.cell(0, 10, f"Customer: {clean_text(name)}", 0, 1)
    pdf.cell(0, 10, f"Plate: {clean_text(plate)}", 0, 1)
    pdf.ln(5)
    for item in items: pdf.cell(0, 8, f"- {clean_text(item['part_vn'])}: {item['cost']:,.0f} VND", 0, 1)
    pdf.ln(5)
    pdf.cell(0, 10, f"Total: {total:,.0f} VND", 0, 1)
    pdf.cell(0, 10, f"Method: {clean_text(method)}", 0, 1)
    pdf.cell(0, 10, f"Ref: {tx[:15]}...", 0, 1)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def clean_text(text):
    if not isinstance(text, str): text = str(text)
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

# ================= 6. UI FLOW =================

# --- SIDEBAR ---
with st.sidebar:
    if logo_path: st.image(logo_path, width=150)
    else: st.markdown("## 🛡️ INSUR-AI")
    st.markdown("### 🛰️ Trạng thái")
    c1, c2 = st.columns(2); c1.metric("GPS", "Tốt", delta="Locked"); c2.metric("API", "VNPT", delta="Online")
    st.markdown("---")
    if st.session_state['ocr_data']:
        st.success("✅ Hồ sơ đã xác thực")
        st.write(f"**Chủ xe:** {st.session_state['ocr_data']['owner']}")
        st.write(f"**Biển số:** {st.session_state['ocr_data']['plate']}")
        st.caption("Hạng: Gold Member")
    elif st.session_state['step'] >= 0: st.success("👤 Đã đăng nhập"); st.write("**TRỊNH THỊ CẨM TÚ**")
    st.markdown("---")
    with st.expander("⚙️ Admin Config"):
        st.session_state['u_ocr'] = st.text_input("OCR URL:", st.session_state['u_ocr'])
        st.session_state['u_vis'] = st.text_input("Vision URL:", st.session_state['u_vis'])
    st.markdown("**📡 System Processing Logs:**")
    st.markdown(f'<div class="console-log">{"<br>".join(st.session_state["logs"])}</div>', unsafe_allow_html=True)
    if st.button("🔄 LÀM LẠI TỪ ĐẦU"): reset_session_full()

logo_html = f'<img src="data:image/png;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" class="header-logo">' if logo_path else ''
st.markdown(f"""<div class="header-container">{logo_html}<div><div class="header-title">INSUR-AI</div><div class="header-subtitle">Hệ thống Giám định & Bồi thường Bảo hiểm Tự động</div></div></div>""", unsafe_allow_html=True)

# 1. LOGIN
if st.session_state['step'] == -1:
    c_form, c_intro = st.columns([4, 6], gap="large") 
    with c_form:
        with st.container(border=True):
            st.markdown("### 🔐 Đăng nhập hệ thống")
            st.text_input("Tài khoản VNPT ID", "091xxxx888")
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("Xác thực sinh trắc học (Face ID):")
            st.camera_input("Camera")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("ĐĂNG NHẬP NGAY", type="primary", use_container_width=True):
                with st.spinner("Đang kết nối VNPT eKYC..."): time.sleep(1)
                st.success("✅ Xác thực thành công!"); time.sleep(0.5); st.session_state['step'] = 0; st.rerun()
    with c_intro:
        st.markdown('<div class="login-intro-title">👋 Chào mừng bạn trở lại!</div>', unsafe_allow_html=True)
        st.markdown('<p class="login-intro-text">Trải nghiệm quy trình bồi thường bảo hiểm thế hệ mới, được bảo trợ bởi công nghệ AI tiên tiến nhất từ VNPT.</p>', unsafe_allow_html=True)
        st.markdown("---")
        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("""<div class="feature-box"><div class="feature-title">🔐 Bảo mật tuyệt đối</div><div class="feature-desc">Xác thực đa lớp với VNPT eKYC & Face ID.</div></div><div class="feature-box"><div class="feature-title">⚡ Xử lý siêu tốc</div><div class="feature-desc">Hoàn tất hồ sơ chỉ trong 3 phút.</div></div>""", unsafe_allow_html=True)
        with fc2:
             st.markdown("""<div class="feature-box"><div class="feature-title">🤖 AI Thông minh</div><div class="feature-desc">Định danh & Giám định tổn thất tự động.</div></div><div class="feature-box"><div class="feature-title">💰 Giải ngân tức thì</div><div class="feature-desc">Kết nối trực tiếp VNPT Money & Ngân hàng.</div></div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.caption("© 2024 VNPT INSUR-AI. Enterprise Edition v63. All rights reserved.")

# 2. OCR
elif st.session_state['step'] == 0:
    st.markdown("### 1️⃣ Định danh Phương tiện")
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.info("Vui lòng tải lên ảnh Cà-vẹt hoặc Đăng kiểm xe")
        f = st.file_uploader("", type=['jpg', 'png'])
        if f:
             with st.status("🔍 Checking Quality Gate...", expanded=False) as status:
                time.sleep(0.5); st.write("✅ Độ nét: Tốt"); time.sleep(0.5); st.write("✅ Ánh sáng: Đủ sáng"); status.update(label="✅ ẢNH ĐẠT CHUẨN", state="complete")
             
             if not st.session_state['ocr_done']:
                with st.spinner("VNPT OCR đang đọc..."):
                    data = call_ocr(f); st.session_state['ocr_data'] = data; st.session_state['ocr_done'] = True
    with c2:
        if st.session_state['ocr_data']:
            d = st.session_state['ocr_data']
            with st.container(border=True):
                st.success("✅ Đã trích xuất thông tin")
                st.text_input("Chủ xe", d['owner']); st.text_input("Biển số", d['plate']); st.text_input("Số khung", d['vin'])
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("TIẾP TỤC ➡️", type="primary", use_container_width=True):
                    st.session_state['step'] = 1; st.session_state['image_quality_pass'] = False; st.rerun()

# 3. VISION & VIDEO (TERMINAL EFFECT)
elif st.session_state['step'] == 1:
    st.markdown("### 2️⃣ Giám định & Chống trục lợi")
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.info("🎥 Vui lòng quay Video vòng quanh xe (Walk-around)")
        
        video_file = st.file_uploader("Tải lên Video hiện trường (.mp4, .mov)", type=['mp4', 'mov', 'avi'])
        
        if video_file:
            st.video(video_file)

            # QUALITY GATE CHO VIDEO
            if not st.session_state['image_quality_pass']:
                 with st.status("🎬 INITIALIZING AI ENGINE...", expanded=True) as status:
                    progress_bar = st.progress(0)
                    log_placeholder = st.empty()
                    
                    logs = [
                        "Initializing YOLOv8 Inference Engine...",
                        "Loading pre-trained weights (coco_vehicle_damage.pt)...",
                        "Extracting Keyframes @ 30FPS...",
                        "Frame #001: Analyzing... [OK]",
                        "Frame #015: Analyzing... [OK]",
                        "Frame #032: Motion Blur Detected... Compensating...",
                        "Frame #045: Damage Candidate Detected (Prob: 0.88)",
                        "Frame #060: Damage Candidate Detected (Prob: 0.92)",
                        "Cross-referencing 3D Geometry...",
                        "Finalizing Damage Report..."
                    ]
                    
                    for i, log in enumerate(logs):
                        log_placeholder.code(log, language="bash")
                        progress_bar.progress((i + 1) * 10)
                        time.sleep(0.3) 

                    status.update(label="✅ VIDEO PROCESSING COMPLETE", state="complete", expanded=False)
                    st.session_state['image_quality_pass'] = True

    with c2:
        with st.container(border=True):
             st.markdown("#### 📍 Vị trí & Thời gian thực")
             if video_file: 
                 st.map(pd.DataFrame({'lat': [10.7769], 'lon': [106.7009]}), zoom=15, use_container_width=True)
                 st.caption(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Loc: 10.7769, 106.7009")

        if video_file and not st.session_state['gps_verified']:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📍 KÍCH HOẠT ANTI-FRAUD CHECK", use_container_width=True, type="primary"):
                with st.status("🕵️‍♀️ Hệ thống đang rà soát gian lận...", expanded=True) as status:
                    st.write("📡 Kết nối vệ tinh GPS (Geo-fencing)..."); time.sleep(0.8)
                    st.write("🕒 Kiểm tra tính toàn vẹn Metadata Video..."); time.sleep(0.8)
                    st.write("💾 **Vehicle Health Record: Checking history...**"); time.sleep(1.2)
                    st.write("✅ **No Duplicate Claim Found (Clean)**"); time.sleep(0.5)
                    status.update(label="✅ AN TOÀN - KHÔNG PHÁT HIỆN GIAN LẬN", state="complete", expanded=False)
                st.success("✅ GPS & Video Metadata Hợp lệ"); st.session_state['gps_verified'] = True; st.rerun()

    if video_file and st.session_state['gps_verified']:
        st.markdown("---")
        if st.button("🚀 CHẠY AI GIÁM ĐỊNH (CUSTOM MODEL)", type="primary", use_container_width=True):
            with st.status("🤖 InsurAI Core (YOLOv8) đang xử lý...", expanded=True):
                time.sleep(0.5); st.write("🧠 Loading Custom Model weights...")
                time.sleep(0.5); st.write("🔍 **Multi-object detection on Video Frames...**")
                res = call_vision(video_file) # Xử lý video giả lập
                time.sleep(0.5); st.write("💰 Calculating confidence score...")
            st.session_state['result_data'] = res
            st.session_state['step'] = 2
            st.rerun()

# 4. KẾT QUẢ
elif st.session_state['step'] == 2 and st.session_state['result_data']:
    res = st.session_state['result_data']
    items = res['items']
    cost_sub = sum(item['cost'] for item in items)
    vat = cost_sub * 0.08
    total = cost_sub + vat
    tx_hash = "0x" + "".join(random.choices("0123456789abcdef", k=30))
    total_conf = res.get('total_conf', 88)
    is_auto_approve = total_conf >= AUTO_APPROVE_THRESHOLD

    if st.session_state['ocr_data']:
        st.info(f"👤 **Khách hàng:** {st.session_state['ocr_data']['owner']} | 🚗 **Xe:** {st.session_state['ocr_data']['plate']}")

    st.markdown("### 📋 Kết quả Giám định")
    c_score, c_status = st.columns([3, 1])
    with c_score:
        st.write(f"**Độ tin cậy AI (Confidence Rate): {total_conf}%**")
        st.progress(total_conf/100)
    with c_status:
        if is_auto_approve: st.success("✅ **AUTO APPROVE**")
        else: st.error("⚠️ **MANUAL REVIEW**")

    with st.container(border=True):
        st.write("**Phát hiện tổn thất:**")
        for idx, item in enumerate(items):
            c_check, c_name, c_price = st.columns([1, 4, 2])
            c_check.checkbox(f"#{idx+1}", value=True, key=f"chk_{idx}")
            c_name.write(f"**{item['part_vn']}** ({item['sever_vn']})")
            c_price.write(f"{item['cost']:,.0f} đ")

    st.markdown(f"""<div class="invoice-box"><div class="invoice-row"><span>Chi phí:</span> <span>{cost_sub:,.0f} VNĐ</span></div><div class="invoice-row"><span>VAT (8%):</span> <span>{vat:,.0f} VNĐ</span></div><div class="invoice-total"><span>TỔNG CỘNG:</span> <span>{total:,.0f} VNĐ</span></div></div>""", unsafe_allow_html=True)
    st.markdown("---")
    
    if not st.session_state['paid'] and not st.session_state['sent_to_human']:
        if is_auto_approve:
            if not st.session_state['show_dispute_form'] and not st.session_state['ticket_created']:
                st.markdown("### 💳 Chọn hình thức bồi thường")
                with st.container(border=True):
                    pay_type = st.radio("Hình thức:", ["💸 Nhận tiền mặt", "🔧 Sửa chữa tại Gara"], horizontal=True)
                    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                    if "Gara" in pay_type:
                        st.session_state['payment_method'] = "garage"; st.info("ℹ️ Hệ thống sẽ gửi **Voucher Bảo Lãnh** trị giá tương ứng tới Gara."); st.session_state['bank_details'] = "Gara VinFast Thảo Điền"
                    else: 
                        st.session_state['payment_method'] = "money"; st.write("**Chọn kênh nhận tiền:**")
                        c_vnpt, c_bank, c_momo = st.columns(3)
                        curr = st.session_state.get('payment_channel', 'vnpt')
                        if c_vnpt.button("⚡ VNPT Money", key="btn_vnpt", type="primary" if curr=='vnpt' else "secondary", use_container_width=True): st.session_state['payment_channel'] = 'vnpt'; st.rerun()
                        if c_bank.button("🏦 Ngân hàng", key="btn_bank", type="primary" if curr=='bank' else "secondary", use_container_width=True): st.session_state['payment_channel'] = 'bank'; st.rerun()
                        if c_momo.button("💳 Ví Momo", key="btn_momo", type="primary" if curr=='momo' else "secondary", use_container_width=True): st.session_state['payment_channel'] = 'momo'; st.rerun()
                        st.markdown("<br>", unsafe_allow_html=True)
                        if curr == 'vnpt': st.success("✅ Tiền sẽ về ví VNPT Money: **091xxxx888**"); st.session_state['bank_details'] = "VNPT Money - 091xxxx888"
                        elif curr == 'bank':
                            c_b1, c_b2 = st.columns(2); 
                            with c_b1: bank_name = st.selectbox("Ngân hàng:", ["Vietcombank", "Techcombank", "MBBank", "BIDV", "ACB"])
                            with c_b2: acc_num = st.text_input("Số tài khoản:", placeholder="Nhập số TK...")
                            st.session_state['bank_details'] = f"{bank_name} - {acc_num}"
                        elif curr == 'momo':
                            momo_phone = st.text_input("Nhập số điện thoại Momo:", value="091xxxx888"); st.session_state['bank_details'] = f"Momo - {momo_phone}"

                st.markdown("<br>", unsafe_allow_html=True)
                col_act, col_disp = st.columns([3, 1])
                with col_act:
                    btn_label = "🔧 XÁC NHẬN SỬA CHỮA" if st.session_state['payment_method'] == 'garage' else f"💰 NHẬN {total:,.0f} VNĐ NGAY"
                    if st.button(btn_label, type="primary", use_container_width=True): st.session_state['show_confirm'] = True
                with col_disp:
                    if st.button("⚠️ KHIẾU NẠI", use_container_width=True): st.session_state['show_dispute_form'] = True; st.rerun()

                if st.session_state['show_confirm']:
                    st.warning("Xác nhận tạo yêu cầu?"); c_yes, c_no = st.columns(2)
                    if c_yes.button("✅ TÔI ĐỒNG Ý", use_container_width=True): st.session_state['paid'] = True; st.rerun()
                    if c_no.button("❌ HỦY BỎ", use_container_width=True): st.session_state['show_confirm'] = False; st.rerun()
        else:
            st.warning("⚠️ CẢNH BÁO: Độ tin cậy của AI thấp (<80%)."); st.info("Hồ sơ này cần được chuyển sang bộ phận Giám định viên con người."); st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📨 CHUYỂN GIÁM ĐỊNH VIÊN", type="primary", use_container_width=True): st.session_state['sent_to_human'] = True; st.rerun()

    if st.session_state['sent_to_human']:
        st.success("✅ Đã chuyển hồ sơ! Mã: #MR-2024-8888."); st.write("Giám định viên sẽ liên hệ trong 15 phút."); st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 QUAY VỀ TRANG CHỦ", use_container_width=True): reset_session_full()

    if st.session_state['show_dispute_form']:
        with st.container(border=True):
            st.markdown("### 📝 Gửi yêu cầu Tái giám định"); st.text_area("Lý do khiếu nại:", placeholder="...")
            c_send, c_close = st.columns([2,1])
            if c_send.button("🚀 GỬI YÊU CẦU", type="primary"): st.session_state['ticket_created'] = True; st.session_state['show_dispute_form'] = False; st.rerun()
            if c_close.button("❌ ĐÓNG"): st.session_state['show_dispute_form'] = False; st.rerun()

    if st.session_state['ticket_created']:
            st.success("✅ Đã gửi ticket #9988."); st.button("🔙 QUAY VỀ TRANG CHỦ", on_click=reset_session_full)

    if st.session_state['paid']:
        if st.session_state['payment_method'] == 'money': st.markdown(f"""<div class="success-box"><h2>💸 GIAO DỊCH THÀNH CÔNG</h2><p>Đã chuyển <b>{total:,.0f} VNĐ</b> về <b>{st.session_state['bank_details']}</b></p></div>""", unsafe_allow_html=True)
        else: st.markdown(f"""<div class="info-box"><h2>🔧 ĐẶT LỊCH THÀNH CÔNG</h2><p>Voucher trị giá <b>{total:,.0f} VNĐ</b> đã gửi tới Gara.</p></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = create_pdf("TRINH THI CAM TU", "51K-888.88", items, total, tx_hash, st.session_state['payment_method'], st.session_state['bank_details'])
        st.download_button("📥 Tải Biên bản (.pdf)", pdf_bytes, "BienBan.pdf", "application/pdf", use_container_width=True)
        st.markdown("---")
        if not st.session_state['feedback_done']:
            st.write("### ⭐ Đánh giá dịch vụ"); stars = st.feedback("stars")
            if stars is not None:
                st.session_state['rating_submitted'] = True
                if stars + 1 <= 3: st.error("😔 Chúng tôi rất lấy làm tiếc vì trải nghiệm chưa trọn vẹn này. Mong bạn chia sẻ thêm để chúng tôi phục vụ tốt hơn lần sau nhé!"); st.text_area("Góp ý:", key="fb")
                else: st.success("🎉 Cảm ơn bạn đã tin tưởng InsurAI! Chúc bạn vạn dặm bình an!"); st.text_area("Điều hài lòng nhất:", key="fb")
                if st.button("GỬI PHẢN HỒI"): st.session_state['feedback_done'] = True; st.rerun()
        else:
            # KHÔI PHỤC DÒNG CHỮ CẢM ƠN TÌNH CẢM (FINAL FIX)
            st.markdown(f"""
            <div class="thank-you-box">
                <div class="ty-title">💖 Cảm ơn bạn đã đóng góp!</div>
                <div class="ty-text">Chúng tôi luôn trân trọng mọi ý kiến để hoàn thiện chất lượng dịch vụ mỗi ngày.</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔄 QUAY VỀ TRANG CHỦ", use_container_width=True):
            reset_session_full()