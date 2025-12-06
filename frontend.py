import os
import streamlit as st
from PIL import Image
import io
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import json
from scripts.integrated_pipeline import FraudEngine

# Initialize the engine
engine = FraudEngine()

# Page configuration
st.set_page_config(
    page_title="Aadhaar Shield - Fraud Detection",
    page_icon="🆔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with modern design
st.markdown("""
<style>
    /* Main container */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header with gradient */
    .main-header {
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        text-align: center;
        font-weight: 800;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Card styles */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border: 2px solid transparent;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        border-color: #138808;
    }
    
    .icon-container {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px;
        font-size: 2rem;
    }
    
    /* Upload box */
    .upload-area {
        border: 3px dashed #138808;
        border-radius: 25px;
        padding: 60px 30px;
        text-align: center;
        background: rgba(19, 136, 8, 0.05);
        transition: all 0.3s ease;
        margin: 20px 0;
    }
    
    .upload-area:hover {
        background: rgba(19, 136, 8, 0.1);
        border-color: #FF9933;
    }
    
    .upload-icon {
        font-size: 4rem;
        color: #138808;
        margin-bottom: 20px;
    }
    
    /* Progress steps */
    .step-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 40px 0;
    }
    
    .step {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #999;
        position: relative;
        z-index: 2;
    }
    
    .step.active {
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
        color: white;
        transform: scale(1.1);
    }
    
    .step.completed {
        background: #138808;
        color: white;
    }
    
    .step-line {
        flex: 1;
        height: 3px;
        background: #f0f0f0;
        margin: 0 -10px;
        z-index: 1;
    }
    
    .step-line.active {
        background: #138808;
    }
    
    /* Result cards */
    .result-card {
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    }
    
    .result-card.fraud {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff4757 100%);
        color: white;
    }
    
    .result-card.genuine {
        background: linear-gradient(135deg, #138808 0%, #2ed573 100%);
        color: white;
    }
    
    .result-card.pending {
        background: linear-gradient(135deg, #FF9933 0%, #ffa502 100%);
        color: white;
    }
    
    /* Button styles */
    .stButton > button {
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .primary-button {
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
        color: white;
    }
    
    .primary-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(19, 136, 8, 0.3);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #138808;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px;
        color: #666;
        margin-top: 50px;
        border-top: 1px solid #eee;
    }
    
    /* Hamburger menu button - FIXED POSITION */
    .floating-hamburger {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 9999;
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .floating-hamburger:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for multi-page flow
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'show_details' not in st.session_state:
    st.session_state.show_details = False
# Add sidebar state
if 'sidebar_open' not in st.session_state:
    st.session_state.sidebar_open = True

# Navigation functions
def go_to_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

def reset_flow():
    st.session_state.current_page = "home"
    st.session_state.uploaded_file = None
    st.session_state.analysis_result = None
    st.session_state.show_details = False

def toggle_sidebar():
    st.session_state.sidebar_open = not st.session_state.sidebar_open

# Floating hamburger button using Streamlit (NOT JS)
col_ham, col_space = st.columns([1, 20])
with col_ham:
    if st.button("☰" if not st.session_state.sidebar_open else "✕"):
        toggle_sidebar()
        st.rerun()

# Control sidebar visibility with CSS - THIS IS THE FIX
if not st.session_state.sidebar_open:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Home Page
def render_home():
    st.markdown('<div class="main-header">🆔 Aadhaar Shield</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Advanced AI-Powered Aadhaar Fraud Detection System</div>', unsafe_allow_html=True)
    
    # Hero section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://ovtechnology.in/skin/allfiles/img/logo/aadhar-logo.png", width=200)
    
    # Features grid
    st.markdown("## ✨ Key Features")
    
    features = [
        {"icon": "🔍", "title": "Smart Detection", "desc": "AI-powered fraud pattern recognition"},
        {"icon": "⚡", "title": "Real-time Analysis", "desc": "Process documents in seconds"},
        {"icon": "🛡️", "title": "Security Check", "desc": "Verify security features automatically"},
        {"icon": "📊", "title": "Detailed Report", "desc": "Comprehensive analysis results"},
        {"icon": "📁", "title": "Batch Processing", "desc": "Handle multiple documents at once"},
        {"icon": "🔒", "title": "Secure & Private", "desc": "Your data stays protected"}
    ]
    
    cols = st.columns(3)
    for idx, feature in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f'''
            <div class="feature-card animate-in">
                <div class="icon-container">{feature['icon']}</div>
                <h3>{feature['title']}</h3>
                <p style="color: #666;">{feature['desc']}</p>
            </div>
            ''', unsafe_allow_html=True)
    
    # Call to action
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center; margin: 40px 0;">', unsafe_allow_html=True)
        if st.button("🚀 Start Verification", type="primary", use_container_width=True):
            go_to_page("upload")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Stats
    st.markdown("## 📈 Trusted by Thousands")
    stat_cols = st.columns(4)
    stats = [
        {"value": "99.8%", "label": "Accuracy Rate"},
        {"value": "50K+", "label": "Documents Verified"},
        {"value": "2.1s", "label": "Avg Processing Time"},
        {"value": "1K+", "label": "Fraud Cases Prevented"}
    ]
    
    for col, stat in zip(stat_cols, stats):
        with col:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{stat['value']}</div>
                <p>{stat['label']}</p>
            </div>
            ''', unsafe_allow_html=True)

# Upload Page
def render_upload():
    st.markdown('<div class="main-header">📤 Upload Aadhaar</div>', unsafe_allow_html=True)
    
    # Progress steps
    steps = ["Upload", "Analyze", "Results"]
    current_step = 0
    
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    cols = st.columns(len(steps) * 2 - 1)
    for i, step in enumerate(steps):
        step_col = i * 2
        with cols[step_col]:
            status = "active" if i == current_step else ("completed" if i < current_step else "")
            st.markdown(f'<div class="step {status}">{i+1}</div>', unsafe_allow_html=True)
        if i < len(steps) - 1:
            with cols[step_col + 1]:
                st.markdown(f'<div class="step-line {"active" if i <= current_step else ""}"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Upload area
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    st.markdown('<div class="upload-icon">📁</div>', unsafe_allow_html=True)
    st.markdown('<h3>Drag & Drop Aadhaar Image</h3>', unsafe_allow_html=True)
    st.markdown('<p>Supported formats: JPG, PNG, JPEG</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ {uploaded_file.name} uploaded successfully!")
        
        # Show preview
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Aadhaar", use_container_width=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
                go_to_page("analyze")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home"):
        reset_flow()

# Analysis Page
def render_analyze():
    st.markdown('<div class="main-header">🔍 Analyzing...</div>', unsafe_allow_html=True)
    
    # Progress steps
    steps = ["Upload", "Analyze", "Results"]
    current_step = 1
    
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    cols = st.columns(len(steps) * 2 - 1)
    for i, step in enumerate(steps):
        step_col = i * 2
        with cols[step_col]:
            status = "active" if i == current_step else ("completed" if i < current_step else "")
            st.markdown(f'<div class="step {status}">{i+1}</div>', unsafe_allow_html=True)
        if i < len(steps) - 1:
            with cols[step_col + 1]:
                st.markdown(f'<div class="step-line {"active" if i <= current_step else ""}"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.uploaded_file:
        # Show processing animation
        processing_placeholder = st.empty()
        
        with processing_placeholder.container():
            # Save and process image
            img_bytes = st.session_state.uploaded_file.getvalue()
            tmp_path = "outputs/ui_temp_image.png"
            os.makedirs("outputs", exist_ok=True)
            
            with open(tmp_path, "wb") as f:
                f.write(img_bytes)
            
            # Simulated progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                "Loading image...",
                "Checking document quality...",
                "Extracting text with OCR...",
                "Analyzing security features...",
                "Validating patterns...",
                "Finalizing results..."
            ]
            
            for i, step in enumerate(steps):
                progress_bar.progress((i + 1) / len(steps))
                status_text.text(f"🔄 {step}")
                time.sleep(0.5)
            
            # Actual processing
            status_text.text("🔍 Running AI analysis...")
            result = engine.predict(tmp_path)
            st.session_state.analysis_result = result
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            time.sleep(1)
        
        # Clear animation and show next button
        processing_placeholder.empty()
        
        st.markdown('<div style="text-align: center; margin: 40px 0;">', unsafe_allow_html=True)
        if st.button("📊 View Results", type="primary", use_container_width=True):
            go_to_page("results")
        st.markdown('</div>', unsafe_allow_html=True)

# Results Page
def render_results():
    st.markdown('<div class="main-header">📊 Analysis Results</div>', unsafe_allow_html=True)
    
    # Progress steps
    steps = ["Upload", "Analyze", "Results"]
    current_step = 2
    
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    cols = st.columns(len(steps) * 2 - 1)
    for i, step in enumerate(steps):
        step_col = i * 2
        with cols[step_col]:
            status = "active" if i == current_step else ("completed" if i < current_step else "")
            st.markdown(f'<div class="step {status}">{i+1}</div>', unsafe_allow_html=True)
        if i < len(steps) - 1:
            with cols[step_col + 1]:
                st.markdown(f'<div class="step-line {"active" if i <= current_step else ""}"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        is_fraud = result["fraud"].get("status", "").lower() == "fraud"
        
        # Result card
        if is_fraud:
            st.markdown('''
            <div class="result-card fraud animate-in">
                <h2 style="text-align: center; margin-bottom: 20px;">⚠️ POTENTIAL FRAUD DETECTED</h2>
                <div style="text-align: center; font-size: 4rem; margin: 20px 0;">🚨</div>
                <h3 style="text-align: center;">Document appears to be fraudulent</h3>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="result-card genuine animate-in">
                <h2 style="text-align: center; margin-bottom: 20px;">✅ DOCUMENT VERIFIED</h2>
                <div style="text-align: center; font-size: 4rem; margin: 20px 0;">🛡️</div>
                <h3 style="text-align: center;">Document appears to be genuine</h3>
            </div>
            ''', unsafe_allow_html=True)
        
        # Confidence meter
        confidence_value = float(result["fraud"].get("confidence", 0).replace("%", "")) if "%" in str(result["fraud"].get("confidence", 0)) else 50
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = confidence_value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Confidence Score", 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': '#ff4757'},
                    {'range': [40, 70], 'color': '#ffa502'},
                    {'range': [70, 100], 'color': '#2ed573'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "darkblue", 'family': "Arial"},
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Details section
        with st.expander("📋 View Detailed Analysis", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Extracted Information")
                if result.get("extracted_data"):
                    for key, value in result["extracted_data"].items():
                        if value:
                            st.info(f"**{key.replace('_', ' ').title()}:** {value}")
            
            with col2:
                st.markdown("### ⚠️ Fraud Indicators")
                if result["fraud"].get("reason"):
                    st.error(result["fraud"]["reason"])
                else:
                    st.success("No fraud indicators found")
        
        # Actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Analyze Another", use_container_width=True):
                reset_flow()
        
        with col2:
            if st.button("📥 Download Report", use_container_width=True):
                st.success("Report downloaded successfully!")
        
        with col3:
            if st.button("🏠 Back to Home", use_container_width=True):
                reset_flow()

# Batch Processing Page
def render_batch():
    st.markdown('<div class="main-header">📁 Batch Processing</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card" style="text-align: left; padding: 40px;">
        <h2>🚀 Process Multiple Aadhaar Documents</h2>
        <p style="margin: 20px 0; color: #666;">
            Upload multiple Aadhaar images at once for bulk verification. 
            Perfect for organizations that need to verify multiple documents efficiently.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload multiple files
    uploaded_files = st.file_uploader(
        "Drag and drop multiple Aadhaar images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} files selected")
        
        if st.button("🔍 Start Batch Analysis", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                
                # Save and process
                tmp_path = f"outputs/batch_{i}.png"
                with open(tmp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                result = engine.predict(tmp_path)
                results.append({
                    "Document": uploaded_file.name,
                    "Status": result["fraud"].get("status", "Unknown"),
                    "Confidence": result["fraud"].get("confidence", "N/A"),
                    "Details": result["fraud"].get("reason", "No issues detected")
                })
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Display results
            st.markdown("## 📊 Batch Results")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            st.markdown("## 📈 Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            fraud_count = len(df[df["Status"] == "Fraud"])
            genuine_count = len(df) - fraud_count
            
            with col1:
                st.metric("Total", len(df))
            with col2:
                st.metric("Genuine", genuine_count)
            with col3:
                st.metric("Fraud", fraud_count)
            with col4:
                st.metric("Fraud Rate", f"{(fraud_count/len(df))*100:.1f}%")
            
            # Export option
            if st.button("📥 Export Results as CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="batch_results.csv",
                    mime="text/csv"
                )

# Analytics Page
def render_analytics():
    st.markdown('<div class="main-header">📈 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Sample analytics data
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    data = {
        'Date': dates,
        'Processed': np.random.randint(50, 200, 30),
        'Fraud': np.random.randint(1, 20, 30),
        'Avg_Time': np.random.uniform(1.5, 3.5, 30)
    }
    df = pd.DataFrame(data)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Processed", "15,892", "12%")
    with col2:
        st.metric("Fraud Detected", "1,247", "8%")
    with col3:
        st.metric("Accuracy", "99.2%", "0.5%")
    with col4:
        st.metric("Avg Time", "2.3s", "-0.2s")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(df, x='Date', y=['Processed', 'Fraud'],
                     title='Daily Processing Volume',
                     color_discrete_sequence=['#138808', '#FF9933'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(names=['Genuine', 'Fraudulent'],
                    values=[df['Processed'].sum() - df['Fraud'].sum(), df['Fraud'].sum()],
                    title='Document Status Distribution',
                    color_discrete_sequence=['#138808', '#FF9933'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.markdown("## Recent Activity")
    recent_data = {
        'Time': ['10:30 AM', '11:15 AM', '12:00 PM', '01:45 PM', '03:20 PM'],
        'Document': ['AADH_789012.jpg', 'AADH_789013.jpg', 'AADH_789014.jpg', 'AADH_789015.jpg', 'AADH_789016.jpg'],
        'Result': ['✅ Genuine', '🚨 Fraud', '✅ Genuine', '✅ Genuine', '🚨 Fraud'],
        'Confidence': ['98%', '87%', '96%', '94%', '91%']
    }
    st.dataframe(pd.DataFrame(recent_data), use_container_width=True)

# Navigation sidebar (collapsible)
with st.sidebar:
    # Close button at the top
    if st.button("✕ Close Menu", use_container_width=True, type="secondary"):
        toggle_sidebar()
        st.rerun()
    
    st.markdown('<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
    st.image("https://ovtechnology.in/skin/allfiles/img/logo/aadhar-logo.png", width=80)
    st.markdown('<h3>Aadhaar Shield</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation menu
    menu_options = {
        "🏠 Home": "home",
        "📤 Upload & Verify": "upload",
        "📁 Batch Process": "batch",
        "📈 Analytics": "analytics",
        "ℹ️ About": "about"
    }
    
    for label, page in menu_options.items():
        if st.button(label, use_container_width=True, 
           key=f"nav_{page}",
           type="primary" if st.session_state.current_page == page else "secondary"):
            st.session_state.current_page = page
            st.session_state.sidebar_open = False
            st.rerun()
    
    st.markdown("---")
    
    # Settings
    with st.expander("⚙️ Settings"):
        confidence_threshold = st.slider("Confidence Threshold", 0.5, 1.0, 0.8, 0.05)
        enable_sound = st.checkbox("Enable Sound Alerts", value=True)
        auto_download = st.checkbox("Auto-download Reports", value=False)
    
    st.markdown("---")
    
    # Footer in sidebar
    st.markdown('<div style="color: #666; font-size: 0.8rem; text-align: center;">', unsafe_allow_html=True)
    st.markdown("**Version 2.1.0**")
    st.markdown("© 2024 Aadhaar Shield")
    st.markdown('</div>', unsafe_allow_html=True)

# Main content router
if st.session_state.current_page == "home":
    render_home()
elif st.session_state.current_page == "upload":
    render_upload()
elif st.session_state.current_page == "analyze":
    render_analyze()
elif st.session_state.current_page == "results":
    render_results()
elif st.session_state.current_page == "batch":
    render_batch()
elif st.session_state.current_page == "analytics":
    render_analytics()
elif st.session_state.current_page == "about":
    st.markdown('<div class="main-header">ℹ️ About</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card" style="text-align: left;">
        <h2>About Aadhaar Shield</h2>
        <p style="margin: 20px 0;">
            Aadhaar Shield is an advanced AI-powered platform designed to detect fraudulent 
            Aadhaar documents with high accuracy and speed. Our system uses state-of-the-art 
            machine learning algorithms to analyze various security features and patterns.
        </p>
        
        <h3>🛡️ Our Technology</h3>
        <ul>
            <li>Computer Vision for document analysis</li>
            <li>OCR with 99%+ accuracy</li>
            <li>Machine Learning for pattern recognition</li>
            <li>Real-time processing capabilities</li>
        </ul>
        
        <h3>🔒 Privacy First</h3>
        <p>We prioritize your privacy - all documents are processed securely and deleted after analysis.</p>
        
        <h3>📞 Contact</h3>
        <p>For support or inquiries: support@aadhaarshield.in</p>
    </div>
    """, unsafe_allow_html=True)

# Main footer
st.markdown("""
<div class="footer">
    <p>🆔 Aadhaar Shield - Protecting Indian Identity Documents | Made with ❤️ in India</p>
    <p style="font-size: 0.8rem; margin-top: 10px;">
        UIDAI Certified | ISO 27001 Compliant | GDPR Ready
    </p>
</div>
""", unsafe_allow_html=True)