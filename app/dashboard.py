import sys
import os

# Ensure root directory is in sys.path when running via Streamlit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta

st.set_page_config(
    page_title="MLH RecoverAI – AI Revenue Recovery Platform",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sleek Razorpay Dark Midnight Navy Design System (#0c0f1d background)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,800;1,900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hide Streamlit default sidebar & collapse icon */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }

    .stApp {
        background-color: #0c0f1d !important;
        color: #f8fafc !important;
    }

    /* Razorpay Top Navigation Header */
    .rzp-navbar {
        background: #171d34;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 16px 32px;
        margin-bottom: 28px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    /* Razorpay Dark Hero Banner */
    .hero-container {
        background: radial-gradient(circle at 50% 0%, rgba(2, 132, 199, 0.35) 0%, rgba(12, 15, 29, 1) 75%);
        border: 1px solid rgba(2, 132, 199, 0.3);
        border-radius: 24px;
        padding: 50px 40px;
        margin-bottom: 36px;
        text-align: center;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        color: #ffffff;
    }

    .hero-badge {
        background: linear-gradient(90deg, rgba(2, 132, 199, 0.25), rgba(56, 189, 248, 0.25));
        border: 1px solid rgba(56, 189, 248, 0.5);
        color: #38bdf8 !important;
        padding: 6px 20px;
        border-radius: 30px;
        font-size: 0.88rem;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 18px;
        letter-spacing: 0.05em;
    }

    .hero-headline {
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1.18;
        background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
    }

    .hero-sub {
        font-size: 1.12rem;
        color: #94a3b8 !important;
        max-width: 820px;
        margin: 0 auto 28px auto;
        line-height: 1.6;
        font-weight: 500;
    }

    /* Razorpay.com Product Showcase Container (Dark Theme) */
    .rzp-showcase-box {
        background: #171d34;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 36px;
        margin-bottom: 36px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    }

    .rzp-showcase-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 24px;
    }

    /* Keyframe Animations for Liquid / Morphing Wave Fills */
    @keyframes liquidWave {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes morphGlow {
        0% { border-color: rgba(56, 189, 248, 0.4); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4); }
        50% { border-color: rgba(217, 70, 239, 0.6); box-shadow: 0 20px 40px rgba(56, 189, 248, 0.4); }
        100% { border-color: rgba(56, 189, 248, 0.4); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4); }
    }

    /* Razorpay Product Card (Dark 3D Depth Card Box - Top/Middle section) */
    .rzp-card-exact {
        background: #1e2540;
        border-top: 1.5px solid rgba(255, 255, 255, 0.1);
        border-left: 1.5px solid rgba(255, 255, 255, 0.1);
        border-right: 1.5px solid rgba(255, 255, 255, 0.1);
        border-bottom: none !important;
        border-radius: 20px 20px 0 0 !important;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        height: 290px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 0px !important;
        cursor: pointer;
    }

    .rzp-card-exact:hover {
        transform: translateY(-4px);
        border-color: #38bdf8;
        box-shadow: 0 22px 50px rgba(56, 189, 248, 0.35), 0 0 25px rgba(2, 132, 199, 0.2);
    }

    .rzp-card-top-asset {
        height: 160px;
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        padding: 16px;
    }

    .rzp-card-tag {
        position: absolute;
        top: 12px;
        right: 12px;
        background: #0284c7;
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 3px 9px;
        border-radius: 6px;
        letter-spacing: 0.05em;
    }

    .rzp-card-bottom-content {
        padding: 16px 20px 10px 20px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: #1e2540;
    }

    .rzp-card-h3 {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff !important;
        margin-bottom: 6px;
    }

    .rzp-card-p {
        font-size: 0.86rem;
        color: #94a3b8 !important;
        line-height: 1.45;
        font-weight: 500;
    }

    /* Column Button Section: Placed seamlessly inside bottom of card box */
    div[data-testid="column"] .stButton {
        background: #1e2540 !important;
        border-left: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        border-right: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        border-bottom: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        border-top: none !important;
        border-radius: 0 0 20px 20px !important;
        padding: 0px 16px 16px 16px !important;
        margin-top: 0px !important;
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.3) !important;
    }

    /* Buttons Styling: Liquid Morphing Fill + 3D Depth Press Effect */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #0369a1 100%) !important;
        background-size: 200% 200% !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        height: 44px !important;
        font-size: 0.88rem !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 4px 0 #034b75, 0 8px 18px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background-position: 100% 100% !important;
        animation: liquidWave 3s ease infinite !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 0 #034b75, 0 15px 30px rgba(56, 189, 248, 0.5) !important;
        border-color: #38bdf8 !important;
    }

    .stButton > button:active {
        transform: translateY(3px) scale(0.98) !important;
        box-shadow: 0 1px 0 #034b75, 0 4px 10px rgba(0, 0, 0, 0.4) !important;
    }

    /* Dark SaaS Container for Specific Feature Pages */
    .white-card {
        background: #171d34 !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        color: #f8fafc !important;
    }

    .badge-success {
        background-color: rgba(34, 197, 94, 0.2) !important;
        color: #4ade80 !important;
        border: 1.5px solid rgba(34, 197, 94, 0.4) !important;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 800;
    }

    .badge-warning {
        background-color: rgba(234, 179, 8, 0.2) !important;
        color: #facc15 !important;
        border: 1.5px solid rgba(234, 179, 8, 0.4) !important;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 800;
    }

    .badge-danger {
        background-color: rgba(239, 68, 68, 0.2) !important;
        color: #f87171 !important;
        border: 1.5px solid rgba(239, 68, 68, 0.4) !important;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 800;
    }

    .step-box-light {
        background: #1e2540 !important;
        border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        color: #ffffff !important;
    }

    .chat-bubble-agent {
        background: rgba(99, 102, 241, 0.25) !important;
        border-left: 5px solid #818cf8 !important;
        color: #e0e7ff !important;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        font-size: 0.98rem;
        font-weight: 600;
    }

    .chat-bubble-user {
        background: rgba(55, 65, 81, 0.7) !important;
        border-left: 5px solid #38bdf8 !important;
        color: #f8fafc !important;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        font-size: 0.98rem;
        font-weight: 600;
    }

    .white-card p, .white-card span, .white-card h1, .white-card h2, .white-card h3, .white-card h4, .white-card label {
        color: #f8fafc !important;
    }

    div[data-baseweb="select"], div[data-baseweb="base-input"], input, textarea, select {
        background-color: #1e2540 !important;
        color: #ffffff !important;
        border: 1.5px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Imports from app services
from app.database import (
    get_summary_stats, get_hitl_queue, resolve_hitl_item, get_audit_logs,
    get_all_p2p, init_db, save_risk_event, get_category_breakdown_db, get_failure_reason_counts_db
)
from app.services.detector import detect_revenue_at_risk
from app.services.diagnoser import diagnose
from app.services.decision_agent import choose_action
from app.services.recovery import execute_recovery_workflow
from app.services.voice_agent import generate_hinglish_script, simulate_interactive_objection
from app.services.razorpay_client import RazorpayClient
from app.services.promise_to_pay import create_promise_to_pay, verify_p2p_settlements
from app.services.assistant_bot import query_assistant, FAQ_KNOWLEDGE_BASE
from app.services.digital_twin import run_digital_twin_simulation
from app.services.copilot import answer_merchant_copilot, calculate_merchant_health_score
from app.services.whatsapp_service import generate_whatsapp_recovery_message, simulate_whatsapp_dispatch
from app.services.predictive_expiry import predict_upcoming_card_expiries, generate_preemptive_update_notice
from app.evaluation.evaluate import run_batch_evaluation
from data.synthetic_generator import generate_synthetic_batch

init_db()
razorpay_client = RazorpayClient()

stats = get_summary_stats()
if stats["total_events"] == 0:
    sample_batch = generate_synthetic_batch(count=120, seed=42)
    for evt in sample_batch:
        detection = detect_revenue_at_risk(evt)
        diag = diagnose(evt)
        dec = choose_action(evt, diag)
        execute_recovery_workflow(evt, dec, simulate_success=True)
    stats = get_summary_stats()

health = calculate_merchant_health_score()

# Initialize Page Router State
if "active_feature" not in st.session_state:
    st.session_state["active_feature"] = "home"


# ==============================================================================
# ==============================================================================
# OFFICIAL MLH (MAJOR LEAGUE HACKING) TOP NAVBAR
# ==============================================================================

nav_col1, nav_col2, nav_col3 = st.columns([5.5, 3.5, 3])

with nav_col1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:16px;">
        <svg width="230" height="48" viewBox="0 0 280 110" fill="none" xmlns="http://www.w3.org/2000/svg">
            <text x="10" y="70" font-family="'Trebuchet MS', 'Arial Black', sans-serif" font-weight="900" font-size="74" fill="#E73C27">M</text>
            <text x="90" y="70" font-family="'Trebuchet MS', 'Arial Black', sans-serif" font-weight="900" font-size="74" fill="#2E52A4">L</text>
            <text x="155" y="70" font-family="'Trebuchet MS', 'Arial Black', sans-serif" font-weight="900" font-size="74" fill="#F0B332">H</text>
            <text x="115" y="98" font-family="'Plus Jakarta Sans', 'Arial Black', sans-serif" font-weight="900" font-size="13" fill="#FFFFFF" letter-spacing="2.5" text-anchor="middle">MAJOR LEAGUE HACKING</text>
        </svg>
        <span style="background:linear-gradient(90deg, rgba(231, 60, 39, 0.25), rgba(240, 179, 50, 0.25)); border:1.5px solid #F0B332; color:#F0B332; padding:4px 12px; border-radius:12px; font-weight:800; font-size:0.82rem; letter-spacing:0.04em;">RECOVER AI</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    st.markdown("<div style='margin-top:8px; color:#cbd5e1; font-size:0.9rem; font-weight:700;'>🏆 Major League Hacking (MLH) 2026</div>", unsafe_allow_html=True)

with nav_col3:
    if razorpay_client.is_live:
        st.markdown("<div style='margin-top:8px;'><span class='badge-success'>● LIVE GATEWAY CONNECTED</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='margin-top:8px;'><span class='badge-warning'>● MLH TEST SANDBOX MODE</span></div>", unsafe_allow_html=True)

st.markdown("---")


# ==============================================================================
# ROUTER: HOME MAIN PAGE VS SPECIFIC FEATURE PAGE
# ==============================================================================

if st.session_state["active_feature"] == "home":
    
    # --------------------------------------------------
    # MLH DARK HOME SHOWCASE PAGE
    # --------------------------------------------------
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">⚡ POWERED BY MLH RECOVERAI ENGINE</div>
        <div class="hero-headline">Find Revenue That's Slipping Away<br>and Win It Back Automatically.</div>
        <div class="hero-sub">
            An autonomous AI decision engine built for Indian merchants to detect payment degradation, checkout drop-offs, failed subscription renewals, and overdue B2B receivables.
        </div>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("""
    <div class="rzp-showcase-box" style="margin-bottom:28px;">
        <div class="rzp-showcase-title">💰 Enterprise Revenue Recovery ROI Calculator</div>
        <p style="color:#94a3b8; font-weight:600; font-size:1.02rem; margin-top:-16px; margin-bottom:20px;">Calculate how much ARR RecoverAI saves for your transaction volume:</p>
    """, unsafe_allow_html=True)

    col_calc1, col_calc2, col_calc3 = st.columns([4, 4, 4])
    with col_calc1:
        monthly_vol = st.slider("Monthly Processing Volume (₹)", min_value=500000, max_value=50000000, value=10000000, step=500000, format="₹%d")
    with col_calc2:
        failure_rate = st.slider("Payment Failure Rate (%)", min_value=2.0, max_value=20.0, value=8.5, step=0.5, format="%.1f%%")
    with col_calc3:
        recovery_eff = st.slider("RecoverAI Recovery Efficiency (%)", min_value=15.0, max_value=60.0, value=38.0, step=1.0, format="%.1f%%")

    at_risk_mon = monthly_vol * (failure_rate / 100.0)
    recovered_mon = at_risk_mon * (recovery_eff / 100.0)
    arr_saved = recovered_mon * 12

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Monthly Revenue at Risk", f"₹{at_risk_mon:,.0f}")
    with m_col2:
        st.metric("Monthly Recovered (Net)", f"₹{recovered_mon:,.0f}", delta=f"+{recovery_eff:.0f}% Recovered")
    with m_col3:
        st.metric("Annualized ARR Saved", f"₹{arr_saved:,.0f}", delta="Saved Revenue")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="rzp-showcase-box">
        <div class="rzp-showcase-title">Explore Razorpay RecoverAI Product Suite</div>
        <p style="color:#94a3b8; font-weight:600; font-size:1.02rem; margin-top:-16px; margin-bottom:28px;">Select any product below to test and launch specific recovery features live:</p>
    """, unsafe_allow_html=True)

    # 4-Column Grid (Row 1)
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("""
        <div class="rzp-card-exact">
            <div class="rzp-card-top-asset" style="background: linear-gradient(135deg, rgba(2, 132, 199, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">NEW 🔥</span>
                <div style="font-size:3.5rem;">💬</div>
                <div style="color:#38bdf8; font-weight:800; font-size:0.85rem; margin-top:6px;">WHATSAPP & UPI QR</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Smart WhatsApp Recovery</div>
                    <div class="rzp-card-p">Dispatches instant WhatsApp recovery template with 1-click Razorpay UPI QR & 5% cashback link.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💬 Try WhatsApp & UPI QR", key="btn_f1", use_container_width=True):
            st.session_state["active_feature"] = "whatsapp_recovery"
            st.rerun()

    with f2:
        st.markdown("""
        <div class="rzp-card-exact">
            <div class="rzp-card-top-asset" style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">NEW 🔥</span>
                <div style="font-size:3.5rem;">🔮</div>
                <div style="color:#facc15; font-weight:800; font-size:0.85rem; margin-top:6px;">PRE-EMPTIVE EXPIRY</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Pre-Emptive Expiry AI</div>
                    <div class="rzp-card-p">Predicts subscription card & e-Mandate expiries 30 days ahead, sending pre-emptive card update links.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔮 Try Card Expiry Predictor", key="btn_f2", use_container_width=True):
            st.session_state["active_feature"] = "predictive_expiry"
            st.rerun()

    with f3:
        st.markdown("""
        <div class="rzp-card-exact">
            <div class="rzp-card-top-asset" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">TRACK 01</span>
                <div style="font-size:3.5rem;">💳</div>
                <div style="color:#818cf8; font-weight:800; font-size:0.85rem; margin-top:6px;">PAYMENT FAILURE</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Payment Degradation</div>
                    <div class="rzp-card-p">Auto-diagnoses HDFC/SBI bank downtime and routes smart retries via secondary payment routes.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Try Payment Failures", key="btn_f3", use_container_width=True):
            st.session_state["active_feature"] = "payment_failure"
            st.rerun()

    with f4:
        st.markdown("""
        <div class="rzp-card-exact">
            <div class="rzp-card-top-asset" style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">TRACK 02</span>
                <div style="font-size:3.5rem;">🛒</div>
                <div style="color:#4ade80; font-weight:800; font-size:0.85rem; margin-top:6px;">CHECKOUT DROPOFF</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Checkout Drop-Offs</div>
                    <div class="rzp-card-p">Detects high-intent cart abandonment, generating dynamic 5% cashback Razorpay UPI links.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Try Checkout Recovery", key="btn_f4", use_container_width=True):
            st.session_state["active_feature"] = "cart_abandonment"
            st.rerun()

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

    # 4-Column Grid (Row 2)
    f5, f6, f7, f8 = st.columns(4)
    with f5:
        st.markdown("""
        <div class="rzp-card-exact">
            <div class="rzp-card-top-asset" style="background: linear-gradient(135deg, rgba(217, 70, 239, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">VOICE AI</span>
                <div style="font-size:3.5rem;">🎙️</div>
                <div style="color:#f0abfc; font-weight:800; font-size:0.85rem; margin-top:6px;">HINGLISH CALLS</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Hinglish Voice Agent</div>
                    <div class="rzp-card-p">Multi-lingual AI caller (English, Hinglish, Hindi) with audio playback & objection handling.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎙️ Try Hinglish Voice Studio", key="btn_f5", use_container_width=True):
            st.session_state["active_feature"] = "hinglish_voice"
            st.rerun()

    with f6:
        st.markdown("""
        <div class="rzp-card-exact">
            <div class="rzp-card-top-asset" style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">SIMULATOR</span>
                <div style="font-size:3.5rem;">🔮</div>
                <div style="color:#c4b5fd; font-weight:800; font-size:0.85rem; margin-top:6px;">DIGITAL TWIN</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Digital Twin Simulator</div>
                    <div class="rzp-card-p">Simulates Strategy A vs B vs C campaign yield before launch to compare recovery rate (%), cost, & ROI.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔮 Try Digital Twin", key="btn_f6", use_container_width=True):
            st.session_state["active_feature"] = "digital_twin"
            st.rerun()

    with f7:
        st.markdown("""
        <div class="rzp-card-exact">
            <div class="rzp-card-top-asset" style="background: linear-gradient(135deg, rgba(20, 184, 166, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">COPILOT</span>
                <div style="font-size:3.5rem;">🤖</div>
                <div style="color:#5eead4; font-weight:800; font-size:0.85rem; margin-top:6px;">MERCHANT AI</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Merchant Copilot</div>
                    <div class="rzp-card-p">Natural language AI chatbot for merchants to query lost revenue & health scores (84/100).</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💬 Try Merchant Copilot", key="btn_f7", use_container_width=True):
            st.session_state["active_feature"] = "copilot"
            st.rerun()

    with f8:
        st.markdown("""
        <div class="rzp-card-exact">
            <div class="rzp-card-top-asset" style="background: linear-gradient(135deg, rgba(249, 115, 22, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">TELEMETRY</span>
                <div style="font-size:3.5rem;">📊</div>
                <div style="color:#ffedd5; font-weight:800; font-size:0.85rem; margin-top:6px;">ANALYTICS</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Executive Analytics</div>
                    <div class="rzp-card-p">Live revenue leakage funnel, database telemetry, and payment failure root-cause breakdown.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 View Analytics Dashboard", key="btn_f8", use_container_width=True):
            st.session_state["active_feature"] = "analytics"
            st.rerun()

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

    # 4-Column Grid for Secondary Action Cards (Row 3)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("""
        <div class="rzp-card-exact" style="height: 200px !important;">
            <div class="rzp-card-top-asset" style="height: 120px; background: rgba(255, 255, 255, 0.05);">
                <span class="rzp-card-tag">BENCHMARK</span>
                <div style="font-size:2.5rem;">⚡</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Batch Benchmark</div>
                    <div class="rzp-card-p">150-event benchmark test suite for precision, recall & ROI scorecard.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Run 150-Event Batch Test", key="btn_s1", use_container_width=True):
            st.session_state["active_feature"] = "batch_benchmark"
            st.rerun()

    with s2:
        st.markdown("""
        <div class="rzp-card-exact" style="height: 200px !important;">
            <div class="rzp-card-top-asset" style="height: 120px; background: rgba(239, 68, 68, 0.15);">
                <span class="rzp-card-tag">APPROVALS</span>
                <div style="font-size:2.5rem;">⚖️</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">HITL Queue (>₹50k)</div>
                    <div class="rzp-card-p">Human supervisor approval gatekeeper for enterprise payments >₹50,000.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚖️ Check HITL Queue", key="btn_s2", use_container_width=True):
            st.session_state["active_feature"] = "hitl_queue"
            st.rerun()

    with s3:
        st.markdown("""
        <div class="rzp-card-exact" style="height: 200px !important;">
            <div class="rzp-card-top-asset" style="height: 120px; background: rgba(2, 132, 199, 0.15);">
                <span class="rzp-card-tag">AUDIT LOG</span>
                <div style="font-size:2.5rem;">📜</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Audit Log Explorer</div>
                    <div class="rzp-card-p">Immutable SQLite log history of every AI detection & webhook payload.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📜 Explore Audit Logs", key="btn_s3", use_container_width=True):
            st.session_state["active_feature"] = "audit_log"
            st.rerun()

    with s4:
        st.markdown("""
        <div class="rzp-card-exact" style="height: 200px !important;">
            <div class="rzp-card-top-asset" style="height: 120px; background: linear-gradient(135deg, rgba(56, 189, 248, 0.3) 0%, rgba(30, 41, 59, 0.9) 100%);">
                <span class="rzp-card-tag">SANDBOX</span>
                <div style="font-size:2.5rem;">⚡</div>
            </div>
            <div class="rzp-card-bottom-content">
                <div>
                    <div class="rzp-card-h3">Live Webhook Sandbox</div>
                    <div class="rzp-card-p">Simulate live Razorpay failure webhooks, test dynamic payment swap links & AI agent actions.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Launch Live Webhook Simulator", key="btn_s4", use_container_width=True):
            st.session_state["active_feature"] = "webhook_simulator"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True) # End rzp-showcase-box

else:
    # --------------------------------------------------
    # DEDICATED FEATURE DETAIL PAGE VIEW
    # --------------------------------------------------
    top_nav1, top_nav2 = st.columns([3, 9])
    with top_nav1:
        if st.button("⬅️ Back to Main Landing Page", use_container_width=True):
            st.session_state["active_feature"] = "home"
            st.rerun()
    with top_nav2:
        st.markdown(f"<h3 style='margin:0; color:#38bdf8; font-weight:800;'>Selected Feature: <code>{st.session_state['active_feature'].upper()}</code></h3>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    # FEATURE 1: SMART WHATSAPP RECOVERY PAGE VIEW
    if st.session_state["active_feature"] == "whatsapp_recovery":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("💬 Smart WhatsApp Recovery & 1-Click UPI Intent Link Generator")
        st.write("Generates interactive WhatsApp messages with 1-Click Razorpay UPI QR codes & dynamic 5% cashback discount links.")

        w_col1, w_col2 = st.columns([6, 4])
        with w_col1:
            w_name = st.text_input("Customer Name:", "Rahul Sharma", key="w_name")
            w_amt = st.number_input("At Risk Transaction Amount (INR):", value=4999.0, key="w_amt")
            
            if st.button("💬 Dispatch Smart WhatsApp Recovery", type="primary"):
                evt_w = {
                    "event_id": f"EVT_WA_{datetime.now().strftime('%H%M%S')}",
                    "amount": w_amt,
                    "customer": {"name": w_name, "phone": "+919810123456"}
                }
                wa_res = generate_whatsapp_recovery_message(evt_w)
                
                st.success("✅ WhatsApp Message Dispatched & Delivered to Customer!")
                st.markdown("#### 📱 Delivered WhatsApp Message Payload")
                st.code(wa_res["whatsapp_message_text"], language="text")

        with w_col2:
            st.markdown("#### 📲 Generated UPI QR Code & Intent Details")
            st.info("🔗 **Razorpay Payment Link:**\n`https://rzp.io/l/rec_evt_wa`")
            st.success("⚡ **UPI Intent Link:**\n`upi://pay?pa=razorpay.recoverai@icici&am=4749.05`")
            st.markdown("""
            <div style="background:#ffffff; padding:16px; border-radius:16px; text-align:center; color:#0f172a; border:2px solid #38bdf8;">
                <h4 style="margin:0; color:#0f172a !important;">📲 Scan to Pay via UPI</h4>
                <div style="font-size:5rem; margin:10px 0;">📱💳</div>
                <p style="color:#64748b !important; font-size:0.85rem; font-weight:700;">Google Pay • PhonePe • Paytm • BHIM</p>
                <span class="badge-success">5% INSTANT CASHBACK APPLIED</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # FEATURE 2: PRE-EMPTIVE EXPIRY PREDICTOR PAGE VIEW
    elif st.session_state["active_feature"] == "predictive_expiry":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("🔮 Pre-Emptive Subscription Card Expiry Predictor")
        st.write("Scans e-Mandates & recurring subscriptions expiring in the next 30 days, dispatching pre-emptive card update links before payments ever fail!")

        if st.button("🔍 Scan Subscriptions & Run Pre-Emptive AI", type="primary"):
            records = predict_upcoming_card_expiries(count=8)
            st.session_state["expiry_records"] = records

        if "expiry_records" in st.session_state:
            records = st.session_state["expiry_records"]
            st.markdown(f"### 📋 Upcoming Expiring Mandates ({len(records)} Detected)")
            
            for rec in records:
                e_col1, e_col2 = st.columns([8, 4])
                with e_col1:
                    st.warning(f"⚠️ **{rec['customer_name']}** (`{rec['subscription_id']}`) — **{rec['plan_name']}** (₹{rec['monthly_amount']:,.2f}/mo)\n\nCard: `****{rec['card_last4']}` ({rec['bank_name']}) | Expires in **{rec['days_to_expiry']} days** ({rec['expiry_date']}) | Pre-Emptive Risk Score: **{rec['preemptive_risk_score']}/100**")
                with e_col2:
                    if st.button(f"📩 Dispatch Pre-Emptive Link #{rec['subscription_id']}", key=f"p_{rec['subscription_id']}"):
                        notice = generate_preemptive_update_notice(rec)
                        st.success(f"✅ Pre-Emptive Card Update Link sent to {rec['customer_name']} via WhatsApp & Email!")
                        st.code(notice["notice_text"], language="text")

        st.markdown("</div>", unsafe_allow_html=True)

    # PAYMENT FAILURE / CART / SUB / B2B SPECIFIC INTERACTIVE VIEW
    elif st.session_state["active_feature"] in ["payment_failure", "cart_abandonment", "failed_subscription", "b2b_receivable"]:
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        cat_key = st.session_state["active_feature"]
        st.subheader(f"💳 Interactive Recovery Sandbox — Feature Details for `{cat_key.upper()}`")
        st.write("Run the AI decision engine live on this specific category to see detection, diagnosis, priority score, and generated Razorpay link.")

        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            cust_name_input = st.text_input("Customer Name:", "Rahul Sharma")
            amount_input = st.number_input("Amount (INR):", min_value=100.0, max_value=1000000.0, value=24999.0 if cat_key=="cart_abandonment" else (125000.0 if cat_key=="b2b_receivable" else 4999.0))
        with col_in2:
            cust_phone_input = st.text_input("Customer Phone:", "+919810123456")
            cust_email_input = st.text_input("Customer Email:", "rahul@example.com")
        with col_in3:
            reason_input = st.selectbox(
                "Failure Reason:",
                [
                    "BAD_REQUEST_PAYMENT_TIMED_OUT", "ISSUER_BANK_SERVER_DOWN", "INSUFFICIENT_FUNDS",
                    "AUTHENTICATION_FAILED", "MANDATE_EXPIRED", "CART_ABANDONED_HIGH_INTENT", "INVOICE_OVERDUE_30D"
                ]
            )

        if st.button("🚀 Execute AI Recovery Engine"):
            evt = {
                "event_id": f"EVT_FEATURE_{datetime.now().strftime('%H%M%S')}",
                "category": cat_key,
                "amount": amount_input,
                "currency": "INR",
                "failure_reason": reason_input,
                "customer": {"name": cust_name_input, "phone": cust_phone_input, "email": cust_email_input},
                "status": "detected"
            }
            det = detect_revenue_at_risk(evt)
            diag = diagnose(evt)
            dec = choose_action(evt, diag)
            res = execute_recovery_workflow(evt, dec, simulate_success=True)

            st.markdown("---")
            st.markdown("### 📋 4-Step AI Recovery Execution Breakdown")
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                st.markdown(f"""
                <div class="step-box-light">
                    <h4 style="color:#38bdf8 !important; margin-top:0; font-weight:800;">🔍 1. Detection</h4>
                    <p><b>Event:</b> {evt['event_id']}</p>
                    <p><b>Amount:</b> ₹{evt['amount']:,.2f}</p>
                    <p><b>Priority Score:</b> {det['recovery_priority_score']} ({det['priority_label']})</p>
                </div>
                """, unsafe_allow_html=True)
            with s2:
                st.markdown(f"""
                <div class="step-box-light">
                    <h4 style="color:#818cf8 !important; margin-top:0; font-weight:800;">🧠 2. Diagnosis</h4>
                    <p><b>Intent:</b> {diag['customer_intent']}</p>
                    <p><b>Prob:</b> {diag['recovery_probability']*100:.0f}%</p>
                </div>
                """, unsafe_allow_html=True)
            with s3:
                st.markdown(f"""
                <div class="step-box-light">
                    <h4 style="color:#fbbf24 !important; margin-top:0; font-weight:800;">🎯 3. Action</h4>
                    <p><b>Action:</b> <code>{dec['action']}</code></p>
                    <p><b>Confidence:</b> {dec['confidence']*100:.0f}%</p>
                </div>
                """, unsafe_allow_html=True)
            with s4:
                recovered_val = res.get("money_recovered", 0.0)
                st.markdown(f"""
                <div class="step-box-light">
                    <h4 style="color:#4ade80 !important; margin-top:0; font-weight:800;">🛡️ 4. Result</h4>
                    <p><b>Status:</b> {res['status']}</p>
                    <p><b>Recovered:</b> ₹{recovered_val:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # HINGLISH VOICE STUDIO PAGE VIEW
    elif st.session_state["active_feature"] == "hinglish_voice":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("🎙️ Hinglish AI Voice Agent & Objection Handler Studio")
        st.write("Experience the multi-lingual voice agent simulator designed for checkout drop-offs and B2B invoice collection.")

        c1, c2 = st.columns([6, 4])
        with c1:
            st.markdown("### 📞 Trigger AI Voice Recovery Call")
            v_name = st.text_input("Customer Name:", "Rahul Sharma", key="vn")
            v_amt = st.number_input("Invoice / Cart Amount (INR):", value=14999.0, key="va")

            if st.button("🎙️ Start Hinglish AI Call"):
                script_data = generate_hinglish_script({"event_id": "EVT_VOICE_DEMO", "category": "cart_abandonment", "amount": v_amt, "customer": {"name": v_name}})
                st.success(f"📞 Call Connected with {v_name}! (Duration: 38s, Sentiment: Positive)")
                if script_data.get("audio_file_path") and os.path.exists(script_data["audio_file_path"]):
                    st.audio(script_data["audio_file_path"], format="audio/mp3")

                st.markdown("#### 📜 Live Call Speech Bubbles")
                for turn in script_data["dialog_turns"]:
                    if turn["speaker"] == "AI Voice Agent":
                        st.markdown(f"<div class='chat-bubble-agent'><b>🤖 AI Agent:</b> {turn['text']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='chat-bubble-user'><b>👤 {turn['speaker']}:</b> {turn['text']}</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("### 💬 Live Objection Handling Simulator")
            obj_choice = st.selectbox("Select Customer Objection:", ["will_pay_tomorrow", "discount_request", "wrong_invoice", "upi_request"])
            if st.button("Test AI Objection Response"):
                obj_res = simulate_interactive_objection(obj_choice, v_name, v_amt)
                st.markdown(f"<div class='chat-bubble-user'><b>👤 Customer:</b> {obj_res['customer']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chat-bubble-agent'><b>🤖 AI Agent:</b> {obj_res['agent']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # DIGITAL TWIN SIMULATOR PAGE VIEW
    elif st.session_state["active_feature"] == "digital_twin":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("🔮 Recovery Digital Twin & Campaign Simulator")
        st.write("Simulate 3 competing recovery strategies across a batch before launching campaigns to compare Expected Recovery Rate (%), Cost, and Net Financial ROI!")

        sim_size = st.slider("Select Simulation Batch Size:", 50, 500, 150)
        if st.button("🚀 Run Digital Twin Campaign Simulation"):
            sim_events = generate_synthetic_batch(count=sim_size, seed=42)
            sim_res = run_digital_twin_simulation(sim_events)

            st.markdown("### 📊 Digital Twin Simulation Results")
            st.success(f"🏆 **Recommended Strategy:** {sim_res['recommended_strategy']}\n\n*Reasoning:* {sim_res['recommendation_reason']}")

            s_col1, s_col2, s_col3 = st.columns(3)
            strats = sim_res["strategies"]

            with s_col1:
                st.markdown(f"""
                <div class="step-box-light">
                    <h4 style="color:#cbd5e1 !important; margin-top:0; font-weight:800;">Strategy A: Auto-Retry</h4>
                    <p><b>Recovery Rate:</b> {strats['strategy_a']['recovery_rate_pct']}%</p>
                    <p><b>Expected Revenue:</b> ₹{strats['strategy_a']['expected_revenue']:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            with s_col2:
                st.markdown(f"""
                <div class="step-box-light">
                    <h4 style="color:#38bdf8 !important; margin-top:0; font-weight:800;">Strategy B: Smart Dunning</h4>
                    <p><b>Recovery Rate:</b> {strats['strategy_b']['recovery_rate_pct']}%</p>
                    <p><b>Expected Revenue:</b> ₹{strats['strategy_b']['expected_revenue']:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            with s_col3:
                st.markdown(f"""
                <div class="step-box-light" style="border: 2px solid #4ade80;">
                    <h4 style="color:#4ade80 !important; margin-top:0; font-weight:800;">Strategy C: Incentive + Voice ⭐</h4>
                    <p><b>Recovery Rate:</b> {strats['strategy_c']['recovery_rate_pct']}%</p>
                    <p><b>Expected Revenue:</b> ₹{strats['strategy_c']['expected_revenue']:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # MERCHANT COPILOT PAGE VIEW
    elif st.session_state["active_feature"] == "copilot":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("💬 Merchant Recovery Copilot Chatbot")
        st.write("Ask your AI Merchant Copilot questions about lost revenue, health scores, and payment failure root cause analysis.")

        mq1, mq2, mq3, mq4 = st.columns(4)
        m_q = None
        with mq1:
            if st.button("📊 Revenue lost yesterday?", use_container_width=True):
                m_q = "How much revenue did we lose yesterday?"
        with mq2:
            if st.button("💰 How much won back?", use_container_width=True):
                m_q = "How much revenue have we recovered?"
        with mq3:
            if st.button("🔍 Why are payments failing?", use_container_width=True):
                m_q = "Why are payments failing?"
        with mq4:
            if st.button("🏆 Merchant Health Score?", use_container_width=True):
                m_q = "What is our Merchant Recovery Health Score?"

        if m_q:
            st.markdown(answer_merchant_copilot(m_q))

        cop_input = st.text_input("Ask your Merchant Copilot anything:", key="cop_in")
        if st.button("Ask Copilot"):
            if cop_input:
                st.markdown(answer_merchant_copilot(cop_input))
        st.markdown("</div>", unsafe_allow_html=True)

    # EXECUTIVE ANALYTICS PAGE VIEW
    elif st.session_state["active_feature"] == "analytics":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("📊 Executive Analytics & Revenue Trend Story")
        st.write("Visual breakdown of revenue trends, leakage funnels, and failure root causes driven directly by SQLite Database telemetry.")

        c_chart1, c_chart2 = st.columns(2)
        cat_breakdown = get_category_breakdown_db()
        cat_df = pd.DataFrame(cat_breakdown) if cat_breakdown else pd.DataFrame([
            {"category": "payment_failure", "at_risk": 45000, "recovered": 36000},
            {"category": "cart_abandonment", "at_risk": 32000, "recovered": 25000},
            {"category": "failed_subscription", "at_risk": 28000, "recovered": 21000},
            {"category": "b2b_receivable", "at_risk": 65000, "recovered": 48000}
        ])
        cat_df["Track"] = cat_df["category"].str.replace("_", " ").str.title()
        cat_df["Revenue At Risk (₹)"] = cat_df["at_risk"]
        cat_df["Recovered (₹)"] = cat_df["recovered"]

        plotly_font_style = dict(family="Plus Jakarta Sans", size=13, color="#ffffff")

        with c_chart1:
            st.markdown("<h4 style='color:#ffffff; font-weight:800;'>Revenue At Risk vs Recovered by Track</h4>", unsafe_allow_html=True)
            fig_bar_db = px.bar(
                cat_df, x="Track", y=["Revenue At Risk (₹)", "Recovered (₹)"],
                barmode="group", color_discrete_sequence=["#ef4444", "#4ade80"]
            )
            fig_bar_db.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=plotly_font_style)
            st.plotly_chart(fig_bar_db, use_container_width=True)

        with c_chart2:
            st.markdown("<h4 style='color:#ffffff; font-weight:800;'>Cumulative Money Recovered Timeline</h4>", unsafe_allow_html=True)
            logs = get_audit_logs(limit=200)
            rec_logs = [l for l in logs if l.get("money_recovered", 0) > 0]
            if rec_logs:
                rec_df = pd.DataFrame(rec_logs)
                rec_df["timestamp"] = pd.to_datetime(rec_df["timestamp"])
                rec_df = rec_df.sort_values("timestamp")
                rec_df["Cumulative Recovered (₹)"] = rec_df["money_recovered"].cumsum()
                fig_line_db = px.area(rec_df, x="timestamp", y="Cumulative Recovered (₹)", color_discrete_sequence=["#38bdf8"])
            else:
                fig_line_db = px.area(title="No recovered records yet")
            fig_line_db.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=plotly_font_style)
            st.plotly_chart(fig_line_db, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # BATCH BENCHMARK PAGE VIEW
    elif st.session_state["active_feature"] == "batch_benchmark":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("⚡ Run 150-Event Batch Test Benchmark")
        st.write("Run the full AI recovery pipeline across 150 held-out synthetic transactions to test measured money recovered, accuracy, precision, recall, and net ROI.")

        b1, b2, b3 = st.columns(3)
        with b1:
            batch_size = st.slider("Select Batch Size:", min_value=20, max_value=500, value=150, step=10)
        with b2:
            batch_seed = st.number_input("Random Seed:", value=42)
        with b3:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            run_batch_btn = st.button("▶️ Execute Batch Benchmark", use_container_width=True)

        if run_batch_btn or "last_batch_metrics" in st.session_state:
            if run_batch_btn:
                with st.spinner(f"Running RecoverAI Agent across {batch_size} events..."):
                    metrics = run_batch_evaluation(batch_size=batch_size, seed=batch_seed)
                    st.session_state["last_batch_metrics"] = metrics
            else:
                metrics = st.session_state["last_batch_metrics"]

            st.markdown("### 🏆 Hackathon Evaluation Scorecard")
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.metric("Precision", f"{metrics['precision']:.4f}")
            with m2:
                st.metric("Recall", f"{metrics['recall']:.4f}")
            with m3:
                st.metric("Measured Money Recovered", f"₹{metrics['total_revenue_recovered']:,.2f}")
            with m4:
                st.metric("Net Financial ROI", f"{metrics['net_financial_roi_pct']:.1f}%")
            with m5:
                st.metric("Guardrail Violations Prevented", f"{metrics['blocked_by_guardrails']}")

            st.markdown("---")
            st.dataframe(pd.DataFrame(metrics["processed_results"]).head(30), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # HITL QUEUE PAGE VIEW
    elif st.session_state["active_feature"] == "hitl_queue":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("⚖️ Human-In-The-Loop (HITL) Queue & Compliance Guardrails")
        st.write("High-value enterprise invoices (>₹50,000) automatically pause here for 1-click human supervisor approval.")

        items = get_hitl_queue()
        if items:
            for item in items:
                st.warning(f"⚠️ **Event ID #{item['event_id']}** — Amount: **₹{item['amount']:,.2f}** | Action: `{item['proposed_action']}`\n\n*Reason:* {item['reason']}")
                b_app, b_rej, _ = st.columns([2, 2, 6])
                with b_app:
                    if st.button(f"✅ Approve #{item['event_id']}", key=f"app_{item['event_id']}"):
                        resolve_hitl_item(item['event_id'], approved=True)
                        st.success("Approved! Executing recovery workflow.")
                        st.rerun()
                with b_rej:
                    if st.button(f"❌ Reject #{item['event_id']}", key=f"rej_{item['event_id']}"):
                        resolve_hitl_item(item['event_id'], approved=False)
                        st.warning("Rejected.")
                        st.rerun()
        else:
            st.success("🎉 HITL Queue is empty! All current events are fully compliant with automated guardrails.")
        st.markdown("</div>", unsafe_allow_html=True)

    # AUDIT LOG PAGE VIEW
    elif st.session_state["active_feature"] == "audit_log":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("📜 Immutable Audit Log Explorer")
        st.write("Complete timeline log of every AI event, detection, diagnosis, policy rule match, and Razorpay webhook payload.")

        logs = get_audit_logs(limit=100)
        if logs:
            st.dataframe(pd.DataFrame(logs)[["id", "timestamp", "event_id", "category", "event_type", "actor", "money_recovered"]], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # LIVE WEBHOOK SIMULATOR PAGE VIEW
    elif st.session_state["active_feature"] == "webhook_simulator":
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("⚡ Live Razorpay Webhook & Agent Pipeline Sandbox")
        st.write("Simulate real-time incoming Razorpay payment failure webhooks and observe RecoverAI's multi-step detection, diagnosis, guardrails, and Razorpay Payment Link generation in real-time.")

        ws_col1, ws_col2 = st.columns([5, 7])

        with ws_col1:
            st.markdown("#### 1. Input Simulated Webhook Event")
            sim_name = st.text_input("Customer Name", value="Rahul Verma", key="ws_name")
            sim_phone = st.text_input("Customer Phone", value="+919876543210", key="ws_phone")
            sim_email = st.text_input("Customer Email", value="rahul@example.com", key="ws_email")
            sim_bank = st.selectbox("Issuer Bank Rail", ["HDFC", "SBI", "ICICI", "AXIS"], index=0, key="ws_bank")
            sim_reason = st.selectbox("Failure Reason Code", ["INSUFFICIENT_FUNDS", "EXPIRED_CARD", "ISSUER_BANK_SERVER_DOWN", "BAD_REQUEST_PAYMENT_TIMED_OUT"], index=0, key="ws_reason")
            sim_amount = st.number_input("Transaction Amount (₹)", value=12500.0, step=1000.0, key="ws_amount")
            sim_category = st.selectbox("Risk Category", ["payment_failure", "failed_subscription", "cart_abandonment", "b2b_receivable"], index=0, key="ws_cat")

            trigger_btn = st.button("🚀 Trigger Live Webhook & Agent Pipeline", type="primary", use_container_width=True)

        with ws_col2:
            st.markdown("#### 2. Agent Execution Telemetry & Output")
            if trigger_btn:
                import uuid
                evt_id = f"EVT_SIM_{uuid.uuid4().hex[:6]}"
                event_data = {
                    "event_id": evt_id,
                    "category": sim_category,
                    "amount": sim_amount,
                    "currency": "INR",
                    "bank_name": sim_bank,
                    "failure_reason": sim_reason,
                    "customer": {
                        "customer_id": f"CUST_{uuid.uuid4().hex[:4]}",
                        "name": sim_name,
                        "phone": sim_phone,
                        "email": sim_email,
                        "ltv": 25000.0
                    },
                    "attempts_count": 1,
                    "status": "detected"
                }

                st.info(f"📥 Received Webhook Event ID: `{evt_id}`")
                
                # Step 1: Detect
                detection = detect_revenue_at_risk(event_data)
                st.success(f"✅ **[STEP 1: DETECT]** At-Risk Revenue Flagged (Risk Score: `{detection.get('risk_score', 0.85)}`)")

                # Step 2: Diagnose
                diag = diagnose(event_data)
                root_cause = diag.get("root_cause") if isinstance(diag, dict) else getattr(diag, "root_cause", "Unknown")
                rec_action = diag.get("recommended_action") if isinstance(diag, dict) else getattr(diag, "recommended_action", "SMART_RETRY")
                st.write(f"🔬 **[STEP 2: DIAGNOSE]** Root Cause: `{root_cause}` | Recommended: `{rec_action}`")

                # Step 3: Decide & Guardrails
                decision = choose_action(event_data, diag)
                execution = execute_recovery_workflow(event_data, decision, simulate_success=False)

                st.write(f"🛡️ **[STEP 3: GUARDRAILS]** Status: `{execution['status'].upper()}` | Action: `{execution['action']}`")

                # Step 4: Razorpay Payment Swap Link output
                if "execution_details" in execution and "razorpay_link" in execution["execution_details"]:
                    plink_url = execution["execution_details"]["razorpay_link"]
                    st.markdown(f"🔗 **[STEP 4: RAZORPAY PAYMENT LINK]** Dynamic Payment Swap Link Generated: [{plink_url}]({plink_url})")
                    
                    # Generate QR Code image url or mock QR
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={plink_url}", caption=f"Scan to pay ₹{sim_amount:,.2f} via UPI", width=180)
                elif execution.get("status") == "escalated_hitl":
                    st.warning("⚠️ **[HITL ESCALATION]** Transaction amount > ₹50,000! Event routed to Human Supervisor Queue for review.")

                with st.expander("🔍 View Complete Raw JSON Audit Details"):
                    st.json(execution)

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.9rem; font-weight:700;'>MLH RecoverAI • Autonomous AI Revenue Recovery Decision Engine • Major League Hacking (MLH) 2026</p>", unsafe_allow_html=True)

