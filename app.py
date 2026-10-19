import streamlit as st
import streamlit.components.v1 as _components

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberTrace — Digital Forensics Training",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ────────────────────────────────────────────────────
# Scoring: scores[key] = int (points locked in on first submit)
# Submitted: submitted[key] = bool
# Answers: answers[key] = {q_idx: chosen_index}
# Stage: stage[key] = 0..3  (0=overview,1=evidence,2=analysis,3=findings)
for _k, _v in [
    ("page", "home"),
    ("answers", {}),
    ("submitted", {}),
    ("scores", {}),          # {key_prefix: int}  — locked after first submit
    ("stage", {}),           # {key_prefix: 0-3}
    ("scroll_to_top", False),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Scroll-to-top ─────────────────────────────────────────────────────────────
# ROOT CAUSE (confirmed by reading Streamlit 1.66 source bundles)
# ──────────────────────────────────────────────────────────────
# Streamlit's page does NOT scroll on window / document.body / document.documentElement.
# The actual scrolling element is [data-testid="stAppViewContainer"] — a div
# with  overflow:auto; height:100dvh  (see index.DucWPHXi.js, ~line 320140).
# window, document.body, and document.documentElement are NOT scrolled.
#
# All previous fixes targeted the wrong element:
#   window.scrollTo()                → no effect (window is not the scroll container)
#   document.documentElement.scrollTop → no effect
#   document.body.scrollTop          → no effect
#   window.parent.scrollTo()         → no effect (and wrong frame — was in iframe)
#   st.markdown("<script>…")         → script tag converted to text, never executes
#
# CORRECT FIX: scroll [data-testid="stAppViewContainer"] to scrollTop=0
# using st.html(unsafe_allow_javascript=True), which injects directly into
# the page DOM (no iframe) and re-executes script tags via Html.js / React useEffect.


def _scroll_top():
    """No-op — call-sites in render functions remain; scroll is at module level."""
    pass

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

/* ─── Reset & Base ─── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background-color: #060e1c;
    color: #c2d0e8;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    line-height: 1.6;
}
[data-testid="stHeader"]             { background: transparent; }
[data-testid="stSidebar"]            { background: #09152a; }
[data-testid="stMainBlockContainer"] { padding-top: 0 !important; max-width: 1100px; margin: 0 auto; }
section[data-testid="stMain"] > div  { padding-top: 0; }

/* ─── Top nav bar ─── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
    background: #08142a;
    border-bottom: 1px solid #142540;
    padding: 0.8rem 1.8rem;
    margin-bottom: 0;
}
.navbar-brand { font-size: 1.2rem; font-weight: 700; color: #fff; letter-spacing: -0.01em; }
.navbar-brand span { color: #3b9eff; }
.navbar-meta {
    font-size: 0.7rem; color: #2d4a6a;
    font-family: 'Share Tech Mono', monospace; letter-spacing: 0.1em;
}
.navbar-score {
    font-size: 0.7rem; color: #3b7ec8;
    font-family: 'Share Tech Mono', monospace; letter-spacing: 0.06em;
    background: #071630; border: 1px solid #1a3a5a; border-radius: 4px;
    padding: 0.2rem 0.65rem;
}

/* ─── Hero ─── */
.hero {
    text-align: center;
    padding: 3.5rem 1rem 2.5rem;
    border-bottom: 1px solid #142540;
    margin-bottom: 2.4rem;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: #071630; border: 1px solid #1a4770; color: #4a9fd4;
    font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase;
    padding: 0.28rem 0.9rem; border-radius: 999px; margin-bottom: 1.2rem;
    font-family: 'Share Tech Mono', monospace;
}
.hero-title {
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 700; letter-spacing: -0.03em;
    color: #fff; margin: 0 0 0.45rem; line-height: 1.05;
}
.hero-title span { color: #3b9eff; }
.hero-subtitle {
    font-size: clamp(0.95rem, 2vw, 1.05rem);
    color: #5a7898; max-width: 540px; margin: 0 auto 1.2rem; line-height: 1.65;
}
.hero-intro {
    font-size: 0.88rem; color: #3d5570;
    max-width: 600px; margin: 0 auto; line-height: 1.75;
}

/* ─── Dashboard progress bar ─── */
.dash-progress {
    background: #0b1a30; border: 1px solid #142540; border-radius: 10px;
    padding: 1.2rem 1.6rem; margin: 0 0 2rem;
}
.dash-progress-title {
    font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #2d5070; font-family: 'Share Tech Mono', monospace; margin-bottom: 0.9rem;
}
.dash-stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
}
.dash-stat {
    text-align: center; background: #071428;
    border: 1px solid #111f35; border-radius: 8px; padding: 0.8rem 0.5rem;
}
.dash-stat-num {
    font-size: 1.5rem; font-weight: 700; color: #3b9eff;
    font-family: 'Share Tech Mono', monospace; line-height: 1.2;
}
.dash-stat-label { font-size: 0.68rem; color: #2d4a68; letter-spacing: 0.08em; text-transform: uppercase; }
.progress-bar-wrap {
    margin-top: 1rem; background: #071428;
    border: 1px solid #111f35; border-radius: 6px; overflow: hidden; height: 6px;
}
.progress-bar-fill {
    height: 6px; background: linear-gradient(90deg, #1a4a9e, #3b9eff 70%, #00c8d4);
    border-radius: 6px; transition: width 0.3s;
}
.progress-label {
    font-size: 0.68rem; color: #2d4a68; margin-top: 0.35rem;
    font-family: 'Share Tech Mono', monospace; letter-spacing: 0.08em;
}

/* ─── Section heading ─── */
.sec-head { font-size: 1.1rem; font-weight: 600; color: #d8e4ff; margin: 0 0 0.2rem; }
.sec-sub  { font-size: 0.81rem; color: #2d4a68; margin-bottom: 1.2rem; }

/* ─── Case card grid ─── */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.1rem;
    margin-bottom: 2rem;
}
.card {
    background: #0a1628; border: 1px solid #142540;
    border-radius: 10px; padding: 1.3rem 1.3rem 1rem;
    position: relative; overflow: hidden;
    transition: border-color 0.18s, background 0.18s;
    display: flex; flex-direction: column;
}
.card:hover { border-color: #2a5a9e; background: #0c1e38; }
.card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #1a4a9e, #3b9eff 60%, #00c8d4);
}
.card-top {
    display: flex; align-items: flex-start;
    justify-content: space-between; margin-bottom: 0.75rem;
}
.card-icon { font-size: 1.8rem; line-height: 1; }
.card-status {
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.15rem 0.5rem; border-radius: 4px; font-family: 'Share Tech Mono', monospace;
}
.status-open       { background:#071428; border:1px solid #142540; color:#2d5070; }
.status-inprogress { background:#0d2240; border:1px solid #1a4a7a; color:#3b9eff; }
.status-complete   { background:#0b2a18; border:1px solid #1a5030; color:#3dba6c; }
.diff-badge {
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.12rem 0.45rem; border-radius: 4px; font-family: 'Share Tech Mono', monospace;
}
.diff-beginner     { background:#0d2f1a; border:1px solid #1a5e30; color:#3dba6c; }
.diff-intermediate { background:#2a1f05; border:1px solid #5a4010; color:#c49a20; }
.diff-advanced     { background:#2a0d0d; border:1px solid #5e1a1a; color:#d94040; }
.card-cat {
    font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #2d5a8a; font-family: 'Share Tech Mono', monospace; margin-bottom: 0.35rem;
}
.card-title { font-size: 0.97rem; font-weight: 600; color: #d8e4ff; margin-bottom: 0.5rem; }
.card-desc  { font-size: 0.82rem; color: #3a5878; line-height: 1.6; margin-bottom: 0.9rem; flex: 1; }
.card-meta  {
    display: flex; flex-wrap: wrap; gap: 0.5rem;
    font-size: 0.62rem; color: #1f3a58;
    font-family: 'Share Tech Mono', monospace; margin-bottom: 0.8rem;
}
.card-score {
    font-size: 0.65rem; color: #3b9eff;
    font-family: 'Share Tech Mono', monospace; margin-bottom: 0.6rem;
}

/* ─── Buttons ─── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #0e3a94 0%, #0b52c2 100%);
    color: #d8e8ff; border: 1px solid #1a52d0;
    border-radius: 7px; font-size: 0.82rem; font-weight: 600;
    letter-spacing: 0.04em; padding: 0.55rem 1.2rem; width: 100%;
    min-height: 42px; /* tap-friendly */
    transition: background 0.15s;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #1448b0 0%, #1368e0 100%);
    color: #fff; border-color: #3b9eff;
}

/* ─── Investigation header ─── */
.inv-header {
    background: linear-gradient(135deg, #091a34 0%, #071222 100%);
    border: 1px solid #142540; border-radius: 10px;
    padding: 1.6rem 1.8rem 1.4rem; margin-bottom: 1.6rem;
    position: relative; overflow: hidden;
}
.inv-header::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #1a4a9e, #3b9eff 60%, #00c8d4);
}
.inv-cat {
    font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase;
    color: #2d5a8a; font-family: 'Share Tech Mono', monospace; margin-bottom: 0.4rem;
}
.inv-title { font-size: clamp(1.4rem, 3vw, 1.8rem); font-weight: 700; color: #fff; margin: 0 0 0.5rem; }
.inv-obj   { font-size: 0.86rem; color: #4a6a8a; line-height: 1.6; margin: 0; }
.inv-obj strong { color: #6a94b8; }

/* ─── Investigation stage progress ─── */
.stage-bar {
    display: flex; gap: 0; margin-bottom: 1.8rem;
    border: 1px solid #142540; border-radius: 8px; overflow: hidden;
}
.stage-step {
    flex: 1; text-align: center; padding: 0.55rem 0.3rem;
    font-size: 0.62rem; font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.07em; text-transform: uppercase;
    color: #1f3a58; background: #081428; border-right: 1px solid #142540;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.stage-step:last-child { border-right: none; }
.stage-done { background: #091e38; color: #2d6aa0; }
.stage-active { background: #0c2448; color: #3b9eff; font-weight: 600; }

/* ─── Evidence block ─── */
.ev-outer {
    background: #071422; border: 1px solid #112238; border-radius: 9px;
    margin-bottom: 1rem; overflow: hidden;
}
.ev-title-bar {
    background: #0a1c36; border-bottom: 1px solid #112238;
    padding: 0.45rem 0.9rem; display: flex; align-items: center; gap: 0.5rem;
    flex-wrap: wrap;
}
.ev-dot {
    width: 6px; height: 6px; border-radius: 50%; display: inline-block; flex-shrink: 0;
}
.ev-dot-blue  { background: #3b9eff; }
.ev-dot-cyan  { background: #00c8d4; }
.ev-dot-green { background: #3dba6c; }
.ev-label {
    font-size: 0.63rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #2d5a8a; font-family: 'Share Tech Mono', monospace; flex: 1;
    min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.ev-body {
    padding: 0.8rem 0.9rem; font-family: 'Share Tech Mono', monospace;
    font-size: 0.76rem; color: #6a9ec8; line-height: 1.8;
    white-space: pre-wrap; word-break: break-word; overflow-x: auto;
}

/* ─── Analyst callout ─── */
.callout {
    background: #071a30; border-left: 3px solid #3b9eff;
    border-radius: 0 7px 7px 0; padding: 0.75rem 0.95rem;
    font-size: 0.84rem; color: #4a7498; line-height: 1.7;
}

/* ─── Stage section panels ─── */
.stage-panel {
    background: #081422; border: 1px solid #112238; border-radius: 9px;
    padding: 1.2rem 1.4rem; margin-bottom: 1.2rem;
}
.stage-panel-title {
    font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #2d5a8a; font-family: 'Share Tech Mono', monospace; margin-bottom: 0.6rem;
}

/* ─── Question block ─── */
.q-block {
    background: #081422; border: 1px solid #112238; border-radius: 8px;
    padding: 1rem 1.1rem; margin-bottom: 1rem;
}
.q-num {
    font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: #2d5a8a; font-family: 'Share Tech Mono', monospace; margin-bottom: 0.3rem;
}
.q-label { font-size: 0.88rem; font-weight: 600; color: #c8d8f0; line-height: 1.5; margin-bottom: 0.6rem; }

/* ─── Answer options post-submit ─── */
.opt-correct {
    background: #0a2616; border: 1px solid #1a4a28; color: #3dba6c;
    border-radius: 6px; padding: 0.45rem 0.85rem; font-size: 0.84rem; margin: 0.2rem 0;
}
.opt-wrong {
    background: #280c0c; border: 1px solid #561818; color: #d94040;
    border-radius: 6px; padding: 0.45rem 0.85rem; font-size: 0.84rem;
    margin: 0.2rem 0; text-decoration: line-through;
}
.opt-neutral { color: #2d4a68; padding: 0.45rem 0.85rem; font-size: 0.84rem; margin: 0.2rem 0; }

/* ─── Score banners ─── */
.score-perfect { background:#0a2616; border:1px solid #1a4a28; color:#3dba6c;
    border-radius:8px; padding:0.85rem 1.1rem; font-size:0.9rem; font-weight:600; }
.score-good    { background:#091c36; border:1px solid #182e58; color:#4a9fd4;
    border-radius:8px; padding:0.85rem 1.1rem; font-size:0.9rem; font-weight:600; }
.score-low     { background:#281806; border:1px solid #56380e; color:#c49a20;
    border-radius:8px; padding:0.85rem 1.1rem; font-size:0.9rem; font-weight:600; }

/* ─── Summary & findings ─── */
.summary-box {
    background: #071422; border: 1px solid #112238; border-radius: 9px;
    padding: 1.3rem 1.5rem; margin-top: 1rem;
}
.summary-box h4 { color: #3b9eff; font-size: 0.9rem; margin-bottom: 0.7rem; }
.summary-box p  { color: #5a7898; font-size: 0.86rem; line-height: 1.75; }
.finding-row {
    display: flex; align-items: flex-start; gap: 0.7rem;
    padding: 0.6rem 0; border-bottom: 1px solid #0e2038;
    font-size: 0.84rem;
}
.finding-row:last-child { border-bottom: none; }
.finding-icon { font-size: 1rem; flex-shrink: 0; line-height: 1.4; }
.finding-text { color: #5a7898; line-height: 1.55; }
.finding-text strong { color: #7aaac8; }

/* ─── Chain of custody tag ─── */
.coc-tag {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: #071630; border: 1px solid #102240;
    color: #2d5070; font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.15rem 0.5rem; border-radius: 3px;
    font-family: 'Share Tech Mono', monospace; margin-left: 0.4rem;
}

/* ─── Divider ─── */
hr { border-color: #0e1e32; margin: 1.4rem 0; }

/* ─── Streamlit widget overrides ─── */
.stRadio > label        { color: #8aaac8 !important; font-size: 0.86rem !important; }
.stRadio [data-testid="stMarkdownContainer"] p
                        { font-size: 0.84rem !important; color: #8aaac8 !important; }
div[data-testid="stExpander"] summary
                        { color: #4a7298 !important; font-size: 0.83rem !important; }
[data-testid="stAlert"] { border-radius: 8px !important; }
[data-testid="stAlert"] p { font-size: 0.86rem !important; }

/* ─── Responsive tweaks ─── */
@media (max-width: 640px) {
    .navbar { padding: 0.7rem 1rem; }
    .hero   { padding: 2.2rem 0.75rem 1.8rem; }
    .inv-header { padding: 1.1rem 1rem 1rem; }
    .ev-body    { font-size: 0.7rem; }
    .stage-bar  { display: none; }   /* too cramped on phones — hidden gracefully */
    .dash-stat-grid { grid-template-columns: repeat(2, 1fr); }
    div[data-testid="stButton"] > button { font-size: 0.85rem; min-height: 46px; }
}

/* ─── Footer ─── */
.footer {
    text-align: center; padding: 1.8rem 1rem 1.4rem; margin-top: 2.5rem;
    border-top: 1px solid #0e1e32; color: #1e3050; font-size: 0.76rem; letter-spacing: 0.03em;
}
</style>
""", unsafe_allow_html=True)


# ── Case definitions ──────────────────────────────────────────────────────────
# Fields: icon, tag, title, difficulty, evidence_types, desc,
#         background, objective,
#         evidence (list: label, content, explain),
#         questions (list: text, options, answer, explain),
#         summary

CASES = [

    # ─── Case 0: Phishing Attack ─────────────────────────────────────────────
    {
        "icon": "🎣",
        "tag": "Social Engineering",
        "title": "Phishing Attack",
        "difficulty": "beginner",
        "evidence_types": "Email Headers · WHOIS · Proxy Logs",
        "questions_count": 3,
        "desc": (
            "Employees at NovaTech Solutions began receiving urgent emails asking them "
            "to reset their passwords on a convincing but fake portal. Trace the email "
            "headers, inspect the lookalike domain, and identify the attacker's infrastructure."
        ),
        "background": (
            "**Organisation (Fictional):** NovaTech Solutions Pvt. Ltd.\n\n"
            "**Incident Date:** 14 March 2025\n\n"
            "On the morning of 14 March 2025, NovaTech's IT helpdesk received 23 reports "
            "from staff who had received an email warning that their corporate password "
            "would expire within 24 hours. The email included a link to what appeared to "
            "be the company's internal portal. Three employees entered their credentials "
            "before the security team blocked the domain. You have been assigned to "
            "conduct the post-incident investigation."
        ),
        "objective": "Identify the spoofed sender infrastructure, confirm the credential-harvesting mechanism, and trace all evidence back to a single attacker IP.",
        "evidence": [
            {
                "label": "EVIDENCE 001 — Raw Email Header (Sanitised)",
                "dot": "ev-dot-blue",
                "content": """\
Return-Path:  <bounce@novatech-secure.net>
Received:     from mail.shady-relay.zz (mail.shady-relay.zz [103.45.67.88])
              by mx1.novatech.zz (Postfix) with ESMTP id A3F2B2C4D1
              on Thu, 14 Mar 2025 08:42:18 +0000
DKIM-Signature: v=1; a=rsa-sha256; d=novatech-secure.net; s=default;
              b=FORGED_SIGNATURE_ABCDEF123456==  [VERIFICATION: FAIL]
SPF:          FAIL  (novatech.zz does not authorise 103.45.67.88)
DMARC:        FAIL  (policy: reject; disposition: none — not enforced)
From:         NovaTech IT Support <support@novatech-secure.net>
Reply-To:     attacker7712@freemail.zz
To:           staff@novatech.zz
Subject:      [URGENT] Your NovaTech password expires in 24 hours — action required
Date:         Thu, 14 Mar 2025 08:42:11 +0000
Message-ID:   <20250314084211.773A2@shady-relay.zz>
X-Mailer:     PHPMailer 6.5.1 (https://github.com/PHPMailer/PHPMailer)\
""",
                "explain": (
                    "**What is an email header?**\n\n"
                    "Every email carries hidden metadata called a **header**. It records "
                    "the real path the email took across the internet, including the true "
                    "sending server and its IP address.\n\n"
                    "Key findings here:\n"
                    "- **SPF FAIL** — The sending IP `103.45.67.88` is not authorised to "
                    "send mail on behalf of `novatech.zz`. This is **email spoofing**.\n"
                    "- **DKIM FAIL** — The cryptographic signature is forged; the email "
                    "was not genuinely signed by NovaTech.\n"
                    "- **Reply-To** is a free webmail address unrelated to NovaTech.\n"
                    "- **PHPMailer** is commonly used by attackers to send bulk phishing emails."
                ),
            },
            {
                "label": "EVIDENCE 002 — WHOIS Record for novatech-secure.net",
                "dot": "ev-dot-cyan",
                "content": """\
Domain Name:      novatech-secure.net
Registry Domain ID: D20250312-FICTREG
Registrar:        PrivacyDomains Ltd (Fictitious)
Registered On:    2025-03-12T06:14:33Z   ← 2 days before the attack
Updated On:       2025-03-12T06:14:33Z
Expires On:       2026-03-12T06:14:33Z
Registrant:       REDACTED FOR PRIVACY (proxy registration)
Name Servers:     ns1.shady-relay.zz
                  ns2.shady-relay.zz
DNSSEC:           unsigned
Resolved IP:      103.45.67.88
Hosting ASN:      AS64511  shady-relay.zz  [Bulletproof hosting — abuse unresponsive]\
""",
                "explain": (
                    "**What is WHOIS?**\n\n"
                    "WHOIS is a public database that shows who registered a domain name "
                    "and when. It is one of the first tools an investigator checks.\n\n"
                    "Key findings:\n"
                    "- Domain registered **just 2 days** before the attack — a classic "
                    "indicator called a **Newly Registered Domain (NRD)**.\n"
                    "- The registrant used a **privacy proxy** to hide their identity.\n"
                    "- The domain resolves to the same IP as the relay server in Evidence 1.\n"
                    "- The hosting ASN is flagged as **bulletproof hosting** — providers "
                    "that deliberately ignore abuse complaints, often used by cybercriminals."
                ),
            },
            {
                "label": "EVIDENCE 003 — Corporate Proxy Filter Log (Credential Harvest Page)",
                "dot": "ev-dot-green",
                "content": """\
[PROXY LOG — NovaTech Secure Web Gateway]
Timestamp:        2025-03-14 08:48:32 UTC
Source Host:      WORKSTATION-NV-042  (10.0.1.42)
Source User:      j.henderson@novatech.zz
Requested URL:    http://novatech-secure.net/reset/login?ref=staff&utm=email1
HTTP Method:      GET → then POST (form submission)
HTTP Status:      200 OK
SSL Certificate:  NONE  (plain HTTP — no HTTPS)
Page <title>:     "NovaTech Employee Portal — Secure Password Reset"
Form POST target: http://103.45.67.88/collect.php
POST body (decoded):
  username=j.henderson%40novatech.zz
  password=REDACTED_FOR_REPORT
  token=2025031408

[THREAT INTELLIGENCE]
  103.45.67.88 — Listed on FictSpam Blocklist since 2024-11-03
  103.45.67.88 — Associated with 4 prior phishing campaigns (TI feed: CyberTrace-TI)\
""",
                "explain": (
                    "**HTTP vs HTTPS and credential harvesting**\n\n"
                    "- **HTTP** sends all data in plain text. **HTTPS** encrypts it. "
                    "A real login page always uses HTTPS (shown by the padlock icon).\n"
                    "- The proxy captured the raw form POST — the username and password "
                    "were sent openly to `103.45.67.88/collect.php`, the attacker's "
                    "**credential harvester**.\n"
                    "- **Threat Intelligence (TI)** feeds are databases that track known "
                    "malicious IPs. This IP appears on a blocklist and is linked to "
                    "previous phishing campaigns, confirming it is attacker-controlled."
                ),
            },
        ],
        "questions": [
            {
                "text": "Q1 — The email header shows SPF FAIL and DKIM FAIL. What do these failures tell the investigator?",
                "options": [
                    "NovaTech's mail server was hacked and is sending spam.",
                    "The email did not come from NovaTech's authorised servers — the sender domain was spoofed.",
                    "The email was delayed in transit and the signatures expired.",
                    "The recipient's mail client failed to verify the email correctly.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** SPF (Sender Policy Framework) and DKIM (DomainKeys Identified Mail) "
                    "are email authentication standards. SPF FAIL means the sending IP is not on "
                    "NovaTech's approved list. DKIM FAIL means the cryptographic signature is forged. "
                    "Together they confirm the email was **spoofed** — it only appeared to come from "
                    "NovaTech. The real server at `103.45.67.88` is attacker-controlled."
                ),
            },
            {
                "text": "Q2 — The fake login page used plain HTTP instead of HTTPS. Why is this significant forensically?",
                "options": [
                    "HTTP pages load faster, which helps the attacker avoid detection.",
                    "HTTP transmits data in plain text, so the proxy captured the victim's credentials unencrypted.",
                    "HTTPS requires a paid certificate, so attackers avoid it to save money.",
                    "It is not significant; most legitimate websites also use HTTP.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** HTTP sends all data — including passwords — as readable plain text. "
                    "This allowed NovaTech's proxy to log the exact credentials entered. It also means "
                    "anyone on the network path could intercept them. HTTPS encrypts the data so only "
                    "the server can read it. The absence of HTTPS on a login page is a strong indicator "
                    "of a malicious or negligently built site."
                ),
            },
            {
                "text": "Q3 — Three separate pieces of evidence all point to the same IP address (103.45.67.88). What conclusion does this support?",
                "options": [
                    "The IP belongs to NovaTech's IT department and was used legitimately.",
                    "The IP is a shared hosting server unrelated to the attack.",
                    "A single attacker-controlled server was used for sending the phishing email, hosting the fake page, and harvesting credentials.",
                    "Three different attackers coincidentally used the same server.",
                ],
                "answer": 2,
                "explain": (
                    "✅ **Correct.** The email relay, the WHOIS-resolved IP of the fake domain, "
                    "and the form POST destination all converge on `103.45.67.88`. This consistency "
                    "across three independent evidence sources strongly supports a single, coordinated "
                    "attacker using one server for the entire phishing operation. This technique — "
                    "correlating IoCs (Indicators of Compromise) across evidence — is fundamental to "
                    "digital forensics."
                ),
            },
        ],
        "summary": (
            "**Case Conclusion — Phishing Attack**\n\n"
            "An external threat actor registered the lookalike domain `novatech-secure.net` "
            "48 hours before the attack using a privacy proxy, hosting it on bulletproof "
            "infrastructure at `103.45.67.88` (AS64511). Mass phishing emails were distributed "
            "via PHPMailer with forged SPF/DKIM records. Three employees submitted credentials "
            "to the HTTP-only harvester at `/collect.php`. All three evidence artefacts — "
            "email relay, WHOIS, and proxy log — converge on the same attacker IP, providing "
            "strong attribution.\n\n"
            "**Recommended actions:** Reset all affected credentials immediately. Block "
            "`103.45.67.88` and `novatech-secure.net` at the firewall. Enforce DMARC with "
            "`policy=reject`. Deploy an email security gateway with NRD detection. "
            "Conduct phishing awareness training for all staff."
        ),
    },

    # ─── Case 3: Suspicious Account Login ────────────────────────────────────
    {
        "icon": "🔓",
        "tag": "Unauthorised Access",
        "title": "Suspicious Account Login",
        "difficulty": "beginner",
        "evidence_types": "Session Logs · DM Phishing · Settings Audit",
        "questions_count": 3,
        "desc": (
            "Social media influencer Nia Okafor's ConnectSphere account posted scam content "
            "and had its payment link changed — while she was at a conference in Lagos. "
            "An impossible-travel login from Romania is the key lead."
        ),
        "background": (
            "**Victim (Fictional):** Nia Okafor, ConnectSphere influencer, 1.2M followers\n\n"
            "**Incident Date:** 19 April 2025\n\n"
            "At approximately 14:30 on 19 April 2025, Nia tried to post from her verified "
            "ConnectSphere account and found herself locked out. Her management team confirmed "
            "an unauthorised post had been published to her 1.2 million followers promoting a "
            "fraudulent investment scheme, and her linked payment page had been redirected to "
            "an attacker-controlled wallet. Nia was physically at a conference in Lagos, "
            "Nigeria, and had not accessed her account since 09:02 that morning. "
            "ConnectSphere's Trust & Safety team provided the access logs."
        ),
        "objective": "Confirm the account was compromised, identify how credentials were stolen, and document all unauthorised changes for the platform's incident report.",
        "evidence": [
            {
                "label": "EVIDENCE 001 — ConnectSphere Session & Activity Log (@nia_okafor_official)",
                "dot": "ev-dot-blue",
                "content": """\
[CONNECTSPHERE TRUST & SAFETY — SESSION LOG]
Account:   @nia_okafor_official  |  Verified: YES  |  Followers: 1,243,800
──────────────────────────────────────────────────────────────────────
TIMESTAMP (UTC+1)    ACTION              IP ADDRESS        GEO / DEVICE
2025-04-19 09:02:11  LOGIN               197.210.55.12     Lagos, Nigeria / iPhone-Pro  [KNOWN]
2025-04-19 09:02–09:45  [No activity]
2025-04-19 09:47:33  LOGIN               45.76.204.33      Bucharest, Romania / Chrome 124 Win11  [NEW]
2025-04-19 09:49:07  PROFILE_EDIT        45.76.204.33      Bio updated; payment link changed
2025-04-19 09:52:14  POST_PUBLISHED      45.76.204.33      "Amazing guaranteed investment returns..."
2025-04-19 10:01:48  PASSWORD_CHANGED    45.76.204.33      Previous password invalidated
2025-04-19 10:03:22  RECOVERY_EMAIL_CHG  45.76.204.33      → hacker_drop@tempmail.zz
2025-04-19 10:03:41  2FA_REMOVED         45.76.204.33      Phone 2FA disabled
2025-04-19 14:30:05  LOGIN_FAIL          197.210.55.12     Lagos, Nigeria / iPhone-Pro  [password rejected]
2025-04-19 14:31:18  ACCOUNT_LOCKED      [reported by owner via identity verification]
──────────────────────────────────────────────────────────────────────
IMPOSSIBLE TRAVEL FLAG: 09:02 Lagos → 09:47 Bucharest  [Delta: 45 min, Distance: ~5,700 km]
RISK SCORE:  97 / 100  (CRITICAL)\
""",
                "explain": (
                    "**Impossible travel detection**\n\n"
                    "Modern security systems calculate the physical distance between consecutive "
                    "logins and the time elapsed. If it would be physically impossible to travel "
                    "that distance (e.g., no flight covers 5,700 km in 45 minutes), the system "
                    "flags an **impossible travel** alert — one of the strongest account takeover "
                    "indicators.\n\n"
                    "Key findings:\n"
                    "- All unauthorised changes originated from `45.76.204.33` in Bucharest.\n"
                    "- Within 16 minutes of gaining access, the attacker changed the payment "
                    "link, published a scam post, changed the password, changed the recovery "
                    "email, and removed 2FA — completely locking out the real owner.\n"
                    "- The **risk score of 97/100** means the platform's system considered "
                    "this extremely likely to be an account takeover."
                ),
            },
            {
                "label": "EVIDENCE 002 — Phishing Direct Message (Recovered from DMs)",
                "dot": "ev-dot-cyan",
                "content": """\
[CONNECTSPHERE — DIRECT MESSAGE RECORD]
Message ID:    DM-CS-20250418-448821
Received:      2025-04-18 21:14:39 UTC+1  (evening before the takeover)
From Account:  @ConnectSphere_Verify  [IMPERSONATION — not the official @ConnectSphere account]
To:            @nia_okafor_official

─── MESSAGE BODY ───────────────────────────────────────────────────
Hi Nia ✔

Your verified creator badge is due for renewal within the next 2 hours.

Failure to confirm will result in permanent badge removal and
follower count reset.

Please verify your account immediately at:
  http://connectsphere-verify.zz/badge/confirm?creator=nia_okafor

This link expires in 2 hours.

— ConnectSphere Creator Verification Team
─── END MESSAGE ────────────────────────────────────────────────────

URL ANALYSIS:
  Domain:       connectsphere-verify.zz  [NOT affiliated with ConnectSphere]
  Registered:   2025-04-17  (1 day before phishing DM)
  Resolves to:  103.99.45.201
  Hosting:      Romania  (same country as attacker session IP)
  Page type:    Credential harvester (copies ConnectSphere login UI)\
""",
                "explain": (
                    "**In-platform phishing and social engineering triggers**\n\n"
                    "Attackers do not always use email. Direct messages on social platforms "
                    "can deliver phishing links just as effectively.\n\n"
                    "Key findings:\n"
                    "- The message used two powerful **social engineering** triggers: "
                    "**urgency** ('2 hours') and **fear of loss** ('follower count reset').\n"
                    "- The sender account `@ConnectSphere_Verify` impersonates the official "
                    "platform — a common tactic.\n"
                    "- The phishing domain was registered **one day** before the message.\n"
                    "- The hosting location (Romania) matches the attacker's login IP, "
                    "confirming the same actor sent the DM and performed the takeover."
                ),
            },
            {
                "label": "EVIDENCE 003 — Account Settings Change Audit Trail",
                "dot": "ev-dot-green",
                "content": """\
[CONNECTSPHERE — SETTINGS CHANGE AUDIT]
Account:   @nia_okafor_official
Period:    2025-04-19 09:47 — 10:04 UTC+1  [All changes from 45.76.204.33, Bucharest]
──────────────────────────────────────────────────────────────────────
09:49:07  PAYMENT_LINK
  BEFORE: payouts@niaokafor.com  (legitimate creator payout page)
  AFTER:  https://fraud-wallet.zz/pay/nia  (attacker-controlled page)

09:52:14  POST PUBLISHED (ID: POST-CS-20250419-9921)
  Content: "I've been investing with @GoldReturnsFast — 300% in 2 weeks!
            Limited slots. Link in bio. Don't miss out! 🔥💰"
  Reach:   1,243,800 followers  |  Engagement in 2h: 4,200 clicks on fraud link

10:01:48  PASSWORD
  BEFORE: [redacted]
  AFTER:  [new password set from Bucharest session]

10:03:22  RECOVERY EMAIL
  BEFORE: nia.okafor.real@mailbox.zz  (legitimate)
  AFTER:  hacker_drop@tempmail.zz

10:03:41  TWO-FACTOR AUTHENTICATION
  STATUS: DISABLED  (phone number removed)\
""",
                "explain": (
                    "**Account lockout sequence**\n\n"
                    "After gaining access, the attacker executed a methodical **account "
                    "lockout sequence** to prevent recovery:\n\n"
                    "1. **Payment link changed** — monetises the account immediately.\n"
                    "2. **Scam post published** — reaches 1.2M followers; 4,200 clicked.\n"
                    "3. **Password changed** — blocks owner's current credentials.\n"
                    "4. **Recovery email changed** — blocks account recovery via email.\n"
                    "5. **2FA removed** — eliminates the last recovery option.\n\n"
                    "This entire sequence took just **14 minutes**. The attacker prioritised "
                    "monetisation first (payment link + post) then fortified their control. "
                    "This is the standard **ATO (Account Takeover)** playbook."
                ),
            },
        ],
        "questions": [
            {
                "text": "Q1 — The session log shows a login from Romania just 45 minutes after a login from Lagos. What is this called and why is it significant?",
                "options": [
                    "A duplicate login — it means Nia accidentally logged in twice.",
                    "An impossible travel flag — the physical distance makes it impossible for the same person to have made both logins, proving a separate person logged in from Romania.",
                    "A VPN detection — Nia connected through a VPN server in Romania.",
                    "A session hijack warning — someone captured her active session cookie.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** Lagos to Bucharest is approximately 5,700 km. No commercial "
                    "flight covers this in 45 minutes. The **impossible travel** detection is one of "
                    "the most reliable automated signals in account security. Combined with the new "
                    "unrecognised device, risk score of 97/100, and all subsequent changes from the "
                    "Bucharest IP, this proves two separate people were active on the account."
                ),
            },
            {
                "text": "Q2 — The phishing DM used the messages 'badge removal' and 'expires in 2 hours'. What social engineering technique do these represent?",
                "options": [
                    "Reciprocity — offering something valuable to gain trust.",
                    "Authority — impersonating a powerful figure.",
                    "Urgency and fear of loss — pressuring the victim to act quickly before thinking critically.",
                    "Consensus — claiming many other creators have already verified.",
                ],
                "answer": 2,
                "explain": (
                    "✅ **Correct.** **Urgency** (a 2-hour countdown) and **fear of loss** "
                    "(losing a verified badge and follower count) are the two most common social "
                    "engineering triggers used in phishing. They bypass rational thinking by "
                    "making the target feel they have no time to verify the request's legitimacy. "
                    "Whenever a message creates artificial urgency around clicking a link, it should "
                    "be treated as a phishing attempt until independently verified."
                ),
            },
            {
                "text": "Q3 — The attacker changed the payment link before publishing the scam post. What does this sequence reveal about their primary motive?",
                "options": [
                    "Their primary motive was vandalism — they wanted to embarrass Nia publicly.",
                    "Their primary motive was financial — redirect follower payments and use the trusted account to promote a fraud scheme to 1.2M people.",
                    "Their primary motive was data theft — they wanted Nia's private direct messages.",
                    "Their primary motive was access — they intended to use the account as a launchpad to attack other influencers.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** The order of changes is deliberate: payment link first (captures "
                    "any legitimate creator revenue), then the scam post (harvests clicks from 1.2M "
                    "followers). Evidence 3 shows 4,200 clicks on the fraud link within 2 hours. "
                    "High-follower verified accounts are specifically targeted for their audience trust "
                    "and reach — a follower is far more likely to click a link from a trusted creator "
                    "than from an unknown account."
                ),
            },
        ],
        "summary": (
            "**Case Conclusion — Suspicious Account Login**\n\n"
            "On 18 April 2025, the attacker sent a phishing DM from the impersonator account "
            "`@ConnectSphere_Verify`, directing Nia to a fake credential harvester hosted in "
            "Romania. After obtaining her password, the attacker logged in from `45.76.204.33` "
            "(Bucharest) at 09:47 — 45 minutes after Nia's verified Lagos session, triggering "
            "an impossible travel flag with a risk score of 97/100. Within 14 minutes, the "
            "attacker changed the payment link, published a scam post reaching 1.2M followers, "
            "changed the password and recovery email, and removed 2FA — fully locking Nia out.\n\n"
            "**Recommended actions:** Contact ConnectSphere's Trust & Safety team with the "
            "audit evidence to restore the account via identity verification. Request deletion "
            "of POST-CS-20250419-9921. Submit the fraud wallet URL to relevant authorities. "
            "Once restored, immediately enable 2FA with an authenticator app, set a strong "
            "unique password, and enrol in ConnectSphere's advanced login protection."
        ),
    },

    # ─── Case 1: Online Financial Fraud ──────────────────────────────────────
    {
        "icon": "💳",
        "tag": "Financial Crime",
        "title": "Online Financial Fraud",
        "difficulty": "intermediate",
        "evidence_types": "Auth Logs · Transaction Records · Telecom Data",
        "questions_count": 3,
        "desc": (
            "BlueStar National Bank customer Priya Sharma discovered three large transfers "
            "she never authorised. A VPN-masked device, a freshly opened mule account, and "
            "a suspicious phone call all form part of the digital money trail."
        ),
        "background": (
            "**Organisation (Fictional):** BlueStar National Bank\n\n"
            "**Incident Date:** 2 April 2025  |  **Amount Lost:** ₹87,000\n\n"
            "On the morning of 2 April 2025, customer Priya Sharma (account ****4471) "
            "contacted BlueStar's fraud hotline after noticing three transfers she did not "
            "make. All three were processed between 01:09 and 01:14 while Priya was asleep. "
            "The transfers were completed successfully despite OTP verification being enabled. "
            "The bank's fraud team pulled the digital logs and requested a forensic review."
        ),
        "objective": "Establish how the fraudster authenticated, identify the mule account, and reconstruct the full attack chain from credential theft to cash withdrawal.",
        "evidence": [
            {
                "label": "EVIDENCE 001 — Account Authentication Log (Account ****4471)",
                "dot": "ev-dot-blue",
                "content": """\
[BLUESTAR NATIONAL BANK — AUTHENTICATION LOG]
Account:        ****4471  |  Customer: Priya Sharma
Report Period:  01 Apr 2025 20:00 UTC — 02 Apr 2025 10:00 UTC
──────────────────────────────────────────────────────────────────────
TIMESTAMP (UTC)      EVENT            DEVICE ID        IP ADDRESS         GEO
2025-04-01 22:14:07  AUTH_SUCCESS     iPhone-A1F3      49.36.12.5         Chennai, IN
2025-04-02 01:07:43  AUTH_SUCCESS     Android-UNKN     185.220.101.6      [VPN EXIT NODE]
2025-04-02 01:09:14  TXN_INITIATED    Android-UNKN     185.220.101.6      ₹29,000 → XX7821
2025-04-02 01:11:02  TXN_INITIATED    Android-UNKN     185.220.101.6      ₹31,000 → XX7821
2025-04-02 01:14:37  TXN_INITIATED    Android-UNKN     185.220.101.6      ₹27,000 → XX7821
2025-04-02 01:14:50  OTP_DELIVERED    SMS → +91-98XXXXX  [3 OTPs delivered, all accepted]
2025-04-02 09:30:11  AUTH_SUCCESS     iPhone-A1F3      49.36.12.5         Chennai, IN
──────────────────────────────────────────────────────────────────────
DEVICE NOTE: Android-UNKN has no prior registration on this account.
VPN NOTE:     185.220.101.6 — Tor/VPN exit, listed on AbuseIPDB (confidence: 89%)\
""",
                "explain": (
                    "**Authentication logs and impossible device detection**\n\n"
                    "An auth log records every login attempt with the device ID, IP address, "
                    "and geographic location.\n\n"
                    "Key findings:\n"
                    "- Priya's known device is `iPhone-A1F3` from Chennai. The fraudulent "
                    "session used an unknown Android device via a **VPN exit node** — a "
                    "server that hides the fraudster's real location.\n"
                    "- Three OTPs (One-Time Passwords) were delivered to Priya's number "
                    "and accepted. This means the fraudster had access to those OTPs — "
                    "they did not bypass the system technically; they socially engineered "
                    "Priya into providing them.\n"
                    "- The AbuseIPDB confidence score of 89% means this IP has been "
                    "reported as malicious by 89% of the security community reporters."
                ),
            },
            {
                "label": "EVIDENCE 002 — Mule Account & Transaction Records",
                "dot": "ev-dot-cyan",
                "content": """\
[BLUESTAR NATIONAL BANK — DESTINATION ACCOUNT REPORT]
Account:          XX7821
Registered Name:  Vikram Online Traders
Account Type:     Current Account
Account Opened:   2025-03-31  (2 days before fraud)
KYC Status:       FLAGGED — Aadhaar scan returned MISMATCHED BIOMETRICS
                  Address proof: digitally altered utility bill (detected by compliance AI)

INBOUND TRANSACTIONS on 2025-04-02:
  TXN-ID: BSB-20250402-001  01:09:22  ₹29,000  from ****4471  STATUS: CREDITED
  TXN-ID: BSB-20250402-002  01:11:15  ₹31,000  from ****4471  STATUS: CREDITED
  TXN-ID: BSB-20250402-003  01:14:50  ₹27,000  from ****4471  STATUS: CREDITED
  TOTAL RECEIVED: ₹87,000

CASH WITHDRAWAL:
  TXN-ID: ATM-20250402-MW01
  Time:    2025-04-02 02:31:07 (77 minutes after first transfer)
  ATM ID:  MUM-CS-047  |  Location: Mumbai Central Station
  Amount:  ₹87,000  (full balance)
  Method:  Debit card (card issued same day account opened)\
""",
                "explain": (
                    "**Mule accounts and KYC fraud**\n\n"
                    "A **mule account** is a bank account opened under a false or stolen "
                    "identity. It receives stolen funds and the cash is withdrawn quickly "
                    "to cut the money trail.\n\n"
                    "Key findings:\n"
                    "- The account was opened just 2 days before the fraud.\n"
                    "- KYC (Know Your Customer) verification failed — biometrics did not "
                    "match and the address proof was digitally altered.\n"
                    "- The fraudster withdrew the full ₹87,000 in cash just 77 minutes "
                    "after the first transfer — a classic **smash-and-grab** mule strategy.\n"
                    "- Transaction IDs are unique reference numbers that allow investigators "
                    "to trace each movement of money precisely."
                ),
            },
            {
                "label": "EVIDENCE 003 — Telecom Provider Call Record & OTP Timing Analysis",
                "dot": "ev-dot-green",
                "content": """\
[TELECOM PROVIDER — FICTITIOUS: INDOTEL]
Subscriber:   Priya Sharma  |  MSISDN: +91-98XXXXX
Report Range: 2025-04-01 23:00 — 2025-04-02 02:00 UTC
────────────────────────────────────────────────────────────
CALL DETAIL RECORDS:
  2025-04-01 23:55:12  INBOUND   from +91-70XXXXX   Duration: 18m 04s
  Caller CLI:          +91-70XXXXX  [UNREGISTERED — prepaid, activated 30 Mar 2025]
  Network trace:       Call routed via VoIP gateway: voip-gw-44.freeswitch.zz

OTP DELIVERY CORRELATION:
  OTP #1 sent:  2025-04-02 01:09:11  →  Entered: 2025-04-02 01:09:14  (3 seconds)
  OTP #2 sent:  2025-04-02 01:11:00  →  Entered: 2025-04-02 01:11:02  (2 seconds)
  OTP #3 sent:  2025-04-02 01:14:44  →  Entered: 2025-04-02 01:14:50  (6 seconds)

  [NOTE] Legitimate OTP self-entry typically takes 15–45 seconds.
  Entry under 10 seconds consistent with dictation to a third party.

BANK FRAUD CALL SCRIPT (reconstructed from Priya's statement):
  Caller claimed to be "BlueStar Fraud Prevention Team"
  Stated: "Your account has been compromised — we need to verify via OTP"
  Requested all three OTPs verbally during the 18-minute call\
""",
                "explain": (
                    "**Vishing (Voice Phishing) and OTP timing analysis**\n\n"
                    "**Vishing** is a phone-based social engineering attack where the "
                    "attacker impersonates a trusted organisation (here, the bank) to "
                    "extract sensitive information like OTPs.\n\n"
                    "Key findings:\n"
                    "- The 18-minute call preceded the fraud session by about 1 hour — "
                    "the fraudster was preparing Priya.\n"
                    "- OTPs were entered in 2–6 seconds — far too fast for someone reading "
                    "a text message themselves. This is consistent with the victim **reading "
                    "the OTP aloud** to the caller.\n"
                    "- The caller used an unregistered prepaid SIM and a VoIP gateway to "
                    "hide their identity. Real banks **never ask for OTPs by phone**."
                ),
            },
        ],
        "questions": [
            {
                "text": "Q1 — The OTPs were entered 2–6 seconds after delivery. What does the timing analysis indicate?",
                "options": [
                    "Priya entered her own OTPs unusually quickly.",
                    "The attacker hacked the bank's OTP generation system.",
                    "The OTPs were read aloud by Priya to the fraudster during the phone call, who entered them immediately.",
                    "An automated script was intercepting SMS messages on Priya's device.",
                ],
                "answer": 2,
                "explain": (
                    "✅ **Correct.** Legitimate self-entry of an OTP typically takes 15–45 seconds "
                    "(receive SMS, open app, read and type). Entry in under 10 seconds is only "
                    "consistent with someone dictating the code in real time to a third party. "
                    "The 18-minute vishing call immediately before the transactions confirms this "
                    "scenario. The fraudster did not technically bypass OTP — they socially "
                    "engineered the victim into handing the codes over voluntarily."
                ),
            },
            {
                "text": "Q2 — The mule account (XX7821) had its full balance withdrawn 77 minutes after the first transfer. Why is rapid withdrawal a key fraud tactic?",
                "options": [
                    "To avoid paying monthly account maintenance fees.",
                    "To convert stolen funds to untraceable cash before the bank freezes the account upon a fraud report.",
                    "To trigger a higher daily ATM limit available only to new accounts.",
                    "Because the fraudster needed the money for an urgent legitimate purpose.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** Banks can freeze accounts flagged for suspicious activity, "
                    "but this process typically takes hours. Fraudsters exploit this window by "
                    "withdrawing cash as quickly as possible. Once funds become physical cash, "
                    "they are extremely difficult to trace or recover. This is why the mule "
                    "account had a debit card issued the same day it was opened — everything "
                    "was pre-planned for immediate withdrawal."
                ),
            },
            {
                "text": "Q3 — Which chain of evidence most completely reconstructs the attack from start to finish?",
                "options": [
                    "Vishing call extracts OTPs → fraudster logs in on unknown VPN device → transfers to mule account → ATM cash withdrawal.",
                    "Priya's own device was infected with malware → malware forwarded OTPs → funds transferred automatically.",
                    "An insider at BlueStar leaked Priya's credentials → mule account opened internally → funds transferred.",
                    "Priya forgot to log out on a public computer → fraudster used her active session.",
                ],
                "answer": 0,
                "explain": (
                    "✅ **Correct.** All three evidence sources form a coherent chain: "
                    "(1) Evidence 3 — vishing call obtained OTPs; "
                    "(2) Evidence 1 — unknown VPN device used stolen credentials + OTPs to authenticate; "
                    "(3) Evidence 2 — funds sent to a pre-prepared mule account with forged KYC, "
                    "then withdrawn as cash 77 minutes later. "
                    "This is a textbook **account takeover fraud** chain."
                ),
            },
        ],
        "summary": (
            "**Case Conclusion — Online Financial Fraud**\n\n"
            "A fraudster obtained Priya's banking credentials through an earlier phishing or "
            "data breach event, then conducted an 18-minute vishing call posing as BlueStar's "
            "fraud team to extract three OTPs in real time. An unknown Android device, "
            "masked behind VPN exit node `185.220.101.6`, completed three transfers totalling "
            "₹87,000 to mule account XX7821 — opened 2 days earlier with forged KYC documents. "
            "The full balance was withdrawn in cash at Mumbai Central Station ATM within 77 "
            "minutes, before a freeze could be applied.\n\n"
            "**Recommended actions:** Freeze and close account XX7821. Submit ATM CCTV "
            "footage reference to law enforcement (TXN-ID: ATM-20250402-MW01). Alert Priya "
            "never to share OTPs by phone. Implement behavioural biometrics and device "
            "trust scoring at login. Flag `185.220.101.6` on the bank's firewall."
        ),
    },

    # ─── Case 2: Identity Theft ───────────────────────────────────────────────
    {
        "icon": "🪪",
        "tag": "Personal Data Theft",
        "title": "Identity Theft",
        "difficulty": "intermediate",
        "evidence_types": "Dark Web Dump · Credit Logs · Email Forensics",
        "questions_count": 3,
        "desc": (
            "Arjun Mehta began receiving collection notices for loans he never took. "
            "A data breach, a credential-stuffing attack, and a hidden email forwarding "
            "rule enabled an attacker to open five fraudulent credit accounts undetected."
        ),
        "background": (
            "**Victim (Fictional):** Arjun Mehta, DOB 15 Aug 1992\n\n"
            "**Discovery Date:** March 2025\n\n"
            "Arjun received collection letters for two credit cards and one personal loan he "
            "had never applied for. A credit bureau alert showed five new credit accounts "
            "opened in his name between January and March 2025. His email inbox showed no "
            "approval or welcome messages from any lender. A digital forensics review was "
            "requested to determine how his identity was used without his knowledge."
        ),
        "objective": "Identify the breach that exposed Arjun's data, trace the attacker's method of email interception, and confirm the device used to submit fraudulent applications.",
        "evidence": [
            {
                "label": "EVIDENCE 001 — Dark Web Leaked Record (Source: ShopEasy.zz Breach)",
                "dot": "ev-dot-blue",
                "content": """\
[CYBERTRACE THREAT INTELLIGENCE — DARK WEB MONITORING ALERT]
Alert ID:      CT-DW-20250106-0042
Source DB:     ShopEasy_customers_dec2024.sql.gz
Breach Date:   ~2024-12-18 (estimated from forum post timestamp)
Data Class:    PII + Plaintext Passwords (CRITICAL)

MATCHED RECORD:
  Full Name:   Arjun Mehta
  DOB:         1992-08-15
  PAN Number:  ABCPM1234Z  [FICTIONAL — training data only]
  Email:       arjun.mehta92@mailbox.zz
  Phone:       +91-87XXXXXXX
  Address:     42 Sunflower Lane, Pune 411001 [Fictional]
  Password:    arjun1992  [STORED IN PLAINTEXT — critical finding]
  Loyalty ID:  SE-00294871
  Last Login:  2024-11-30

BREACH CONTEXT:
  ShopEasy.zz database was exfiltrated via an unpatched SQL injection vulnerability.
  Estimated 2.4 million records affected.
  Data appeared on DarkTrace Forum on 2025-01-04.\
""",
                "explain": (
                    "**Dark web monitoring and data breaches**\n\n"
                    "When a website is hacked, the stolen database is often sold or posted "
                    "on dark web forums. Investigators use monitoring tools to detect when a "
                    "person's data appears in such leaks.\n\n"
                    "Key findings:\n"
                    "- Arjun's full PII (Personally Identifiable Information) — including "
                    "his government ID (PAN), address, and phone — was exposed.\n"
                    "- The password `arjun1992` was stored in **plaintext** (not encrypted). "
                    "This is a serious security failure by ShopEasy.\n"
                    "- **SQL injection** is a hacking technique where malicious database "
                    "commands are inserted into a website's input fields to steal data."
                ),
            },
            {
                "label": "EVIDENCE 002 — Credit Application Submission Log",
                "dot": "ev-dot-cyan",
                "content": """\
[CREDIT BUREAU — FICTIONAL: INDIACREDIT]
Subject:       Arjun Mehta  |  PAN: ABCPM1234Z
Report Date:   2025-03-20
──────────────────────────────────────────────────────────────────────
APP-ID         LENDER             DATE        IP ADDRESS         STATUS
APP-2025-0110  QuickCredit Card   2025-01-10  91.108.56.200      APPROVED
APP-2025-0118  FlexiLoan          2025-01-18  91.108.56.200      APPROVED
APP-2025-0203  GoldCard Plus      2025-02-03  45.33.100.77       APPROVED
APP-2025-0215  RapidCash Online   2025-02-15  45.33.100.77       APPROVED
APP-2025-0301  PrimeCredit        2025-03-01  91.108.56.200      APPROVED
──────────────────────────────────────────────────────────────────────
DOCUMENTS SUBMITTED (all five applications):
  - PAN card: ABCPM1234Z  (authentic)
  - DOB: 1992-08-15  (authentic)
  - Address proof: Utility bill — DIGITALLY ALTERED (flagged by 3 lenders, not acted on)
  - Photo ID: MISMATCHED FACIAL FEATURES (retrospective check)

DEVICE FINGERPRINT (all five applications):
  Browser:      Chrome 120.0.6099.130
  OS:           Windows 11 (22H2)
  Screen:       1920x1080
  Timezone:     UTC+5:30
  Fingerprint:  fp_a3b9c1d2e4f8  [IDENTICAL across all five submissions]\
""",
                "explain": (
                    "**Tor, VPN, and device fingerprinting**\n\n"
                    "- `91.108.56.200` is a known **Tor exit node** — traffic from the Tor "
                    "network exits here, hiding the attacker's true IP.\n"
                    "- `45.33.100.77` is a commercial VPN server in the Netherlands.\n"
                    "- Despite changing IPs, all five applications share an **identical "
                    "device fingerprint** — a unique signature made from browser version, "
                    "OS, screen resolution, and timezone. This confirms one person on one "
                    "machine submitted all five applications.\n"
                    "- The address proof was altered digitally but was not caught in real "
                    "time — a gap in the lenders' KYC process."
                ),
            },
            {
                "label": "EVIDENCE 003 — Email Account Forensic Audit (arjun.mehta92@mailbox.zz)",
                "dot": "ev-dot-green",
                "content": """\
[MAILBOX.ZZ — ACCOUNT SECURITY AUDIT LOG]
Account:       arjun.mehta92@mailbox.zz
Audit Period:  2025-01-04 00:00 — 2025-01-06 00:00 UTC
──────────────────────────────────────────────────────────────────────
TIMESTAMP           EVENT                    IP               DETAIL
2025-01-05 03:14:07  LOGIN_SUCCESS            91.108.56.200    Password: arjun1992
2025-01-05 03:14:52  EMAIL_SEARCH             91.108.56.200    Query: "bank" "credit" "statement"
2025-01-05 03:16:30  PASSWORD_RESET_REQUEST   [from QuickCredit portal] → link sent to this inbox
2025-01-05 03:16:44  EMAIL_OPENED             91.108.56.200    Subject: "QuickCredit — Verify Your Identity"
2025-01-05 03:20:11  FILTER_RULE_CREATED      91.108.56.200    Rule: IF sender contains "bank" OR "credit"
                                                               OR "loan" THEN forward to hidden.drop@freemail.zz
                                                               AND mark as read AND skip inbox
2025-01-05 03:22:04  ALL_ALERTS_MARKED_READ   91.108.56.200    47 security notifications marked read
──────────────────────────────────────────────────────────────────────
FILTER RULE STATUS:  ACTIVE until discovered on 2025-03-18 (74 days active)
EMAILS INTERCEPTED:  ~183 messages silently forwarded to hidden.drop@freemail.zz\
""",
                "explain": (
                    "**Credential stuffing and inbox takeover**\n\n"
                    "- **Credential stuffing** is when attackers take a leaked username and "
                    "password and try it on other websites. Arjun used the same password "
                    "`arjun1992` on ShopEasy and his email — the attacker tried it and succeeded.\n"
                    "- Within 6 minutes of logging in, the attacker created a hidden "
                    "**inbox filter rule** that silently forwarded any email containing "
                    "bank/credit terms to their own address `hidden.drop@freemail.zz`, "
                    "then marked them as read so Arjun would never see them.\n"
                    "- This rule was active for **74 days**, intercepting 183 emails "
                    "including all credit approval notifications and OTPs."
                ),
            },
        ],
        "questions": [
            {
                "text": "Q1 — All five fraudulent applications share the same device fingerprint despite different IP addresses. What does this prove?",
                "options": [
                    "Five different people collaborated on the fraud using the same instructions.",
                    "The fingerprinting system was malfunctioning during that period.",
                    "A single person on one physical device submitted all five applications, changing IPs through Tor and a VPN to avoid detection.",
                    "The lenders' systems incorrectly generated a duplicate fingerprint.",
                ],
                "answer": 2,
                "explain": (
                    "✅ **Correct.** A device fingerprint is generated from immutable characteristics "
                    "like browser build, OS version, screen size, and timezone. Changing an IP address "
                    "does not change the fingerprint. The attacker used Tor and a VPN to rotate IPs but "
                    "did not use separate browser profiles or virtual machines to spoof their fingerprint. "
                    "This is a common investigative technique: correlate fingerprints across multiple "
                    "fraudulent applications to link them to one actor."
                ),
            },
            {
                "text": "Q2 — The attacker took control of Arjun's email using the leaked password 'arjun1992'. What attack technique is this called?",
                "options": [
                    "Brute force — systematically guessing every possible password.",
                    "Credential stuffing — taking a password leaked from one breach and trying it on other services.",
                    "Password spraying — trying one common password against many accounts.",
                    "Keylogging — recording keystrokes to capture passwords as they are typed.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** Credential stuffing involves taking leaked username/password pairs "
                    "from one breach and automatically testing them against other services. It works "
                    "because many people reuse the same password across multiple accounts. This is why "
                    "security professionals recommend using a unique password for every service, ideally "
                    "managed by a password manager."
                ),
            },
            {
                "text": "Q3 — The inbox filter rule forwarded emails and marked them as read. What was the strategic purpose of this action?",
                "options": [
                    "To help Arjun manage his inbox more efficiently.",
                    "To ensure the attacker received lender OTPs while Arjun remained completely unaware of all credit activity for months.",
                    "To slow down the attacker's own inbox by reducing incoming messages.",
                    "To prevent Arjun from cancelling his ShopEasy account.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** By creating a silent forwarding rule and marking all intercepted "
                    "emails as read, the attacker achieved two goals: (1) they received all "
                    "verification links, OTPs, and welcome letters from lenders, enabling account "
                    "openings; (2) Arjun's inbox appeared normal — he saw no unread alerts. The rule "
                    "remained active for 74 days and intercepted 183 messages before being discovered. "
                    "This technique is called **inbox shadowing**."
                ),
            },
        ],
        "summary": (
            "**Case Conclusion — Identity Theft**\n\n"
            "Arjun's PII and plaintext password were exposed in the ShopEasy.zz SQL injection "
            "breach of December 2024. The attacker used credential stuffing to access his email "
            "on 5 January 2025, immediately searched for financial emails, and installed a silent "
            "forwarding rule to `hidden.drop@freemail.zz` within 6 minutes. For 74 days, 183 "
            "credit-related emails were intercepted. Five fraudulent credit applications — "
            "all sharing the same device fingerprint `fp_a3b9c1d2e4f8` — were approved using "
            "Arjun's authentic PAN and a digitally altered address proof.\n\n"
            "**Recommended actions:** Report to the credit bureau to place a **credit freeze**. "
            "File a formal police complaint with all transaction IDs and app IDs. Enable "
            "two-factor authentication on all accounts. Use unique passwords (a password manager "
            "is recommended). Delete the forwarding rule immediately and review all inbox filters."
        ),
    },

    # ─── Case 4: Malware Incident ─────────────────────────────────────────────
    {
        "icon": "🦠",
        "tag": "Malware Analysis",
        "title": "Malware Incident",
        "difficulty": "advanced",
        "evidence_types": "Malware Alert · Network Traffic · Endpoint Forensics",
        "questions_count": 3,
        "desc": (
            "Greenfield Academy's network ground to a halt and files began disappearing. "
            "A ransom note appeared on staff screens. Examine AV alerts, network traffic, "
            "and endpoint logs to find Patient Zero and trace the ransomware's spread."
        ),
        "background": (
            "**Organisation (Fictional):** Greenfield Academy (Secondary School)\n\n"
            "**Incident Date:** 7 May 2025  |  **Malware Family:** LockByte v2.1\n\n"
            "At approximately 07:50 on 7 May 2025, Greenfield Academy's IT administrator "
            "received calls from multiple staff members whose computers were running slowly "
            "and displaying strange error messages. By 08:15, ransom notes had appeared on "
            "screens across the school and files on the shared drive were inaccessible. The "
            "IT team immediately isolated the network from the internet and called in an "
            "incident response team. You have been given the first-responder evidence collection."
        ),
        "objective": "Identify the malware type, locate Patient Zero (the first infected machine), and reconstruct how the ransomware spread across the school network.",
        "evidence": [
            {
                "label": "EVIDENCE 001 — Antivirus / EDR Alert & Ransom Note",
                "dot": "ev-dot-blue",
                "content": """\
[GREENSHIELD AV — ENDPOINT DETECTION & RESPONSE ALERT]
Alert ID:       GSH-20250507-0089
Severity:       CRITICAL
Detection Time: 2025-05-07 07:39:42 UTC
Host:           STAFF-PC-07  (192.168.1.45)
User:           dosei  (Mr. David Osei, Science Dept)
──────────────────────────────────────────────────────────────────────
File Name:      GradeSheet_Final.xlsx.exe
File Path:      C:\\Users\\dosei\\Downloads\\GradeSheet_Final.xlsx.exe
File Size:      847,360 bytes (827 KB)
MD5  Hash:      a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6  [FICTIONAL]
SHA-256 Hash:   4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b  [FICTIONAL]
Detection:      Ransom.LockByte.v2  (Behavioural + Signature match)
MITRE ATT&CK:   T1566.001 (Spearphishing Attachment), T1486 (Data Encrypted for Impact)

─── RANSOM NOTE TEXT (displayed on screen) ───
  YOUR FILES HAVE BEEN ENCRYPTED BY LockByte v2.1
  All .docx .xlsx .pdf .pptx files on this machine and network drives
  have been encrypted with AES-256.
  Send 0.5 BTC to wallet: 1FfmbHfnpaZjKFvyi1okTjJJusN455paPH [FICTIONAL]
  You have 72 hours. Contacting law enforcement = permanent deletion.
─────────────────────────────────────────────\
""",
                "explain": (
                    "**Ransomware, file hashes, and MITRE ATT&CK**\n\n"
                    "- **Ransomware** encrypts your files and demands payment for the "
                    "decryption key. Paying does not guarantee recovery.\n"
                    "- A **file hash** (MD5, SHA-256) is a unique digital fingerprint for "
                    "a file. Investigators use hashes to identify known malware samples in "
                    "threat intelligence databases. Even renaming a file does not change its hash.\n"
                    "- The **double extension trick** (`GradeSheet_Final.xlsx.exe`) — the "
                    "file looks like a spreadsheet but is actually an executable program (.exe). "
                    "Windows hides the last extension by default, making it appear as `GradeSheet_Final.xlsx`.\n"
                    "- **MITRE ATT&CK** is a globally recognised framework that categorises "
                    "attacker techniques. T1566.001 = phishing attachment, T1486 = encrypting files."
                ),
            },
            {
                "label": "EVIDENCE 002 — Network Intrusion Detection System (NIDS) Log",
                "dot": "ev-dot-cyan",
                "content": """\
[GREENFIELD ACADEMY — NIDS LOG: Snort 3.1.x]
Capture Period: 2025-05-07 07:38 — 08:15 UTC
──────────────────────────────────────────────────────────────────────
TIME      SRC IP          DST IP / PORT       PROTOCOL  EVENT
07:43:11  192.168.1.45    185.220.101.9:443   HTTPS     C2 Beacon — User-Agent: LockByte/2.1
07:43:18  192.168.1.45    185.220.101.9:443   HTTPS     C2 Config download (encrypted payload)
07:44:55  192.168.1.45    192.168.1.0/24:445  SMB       NIDS ALERT: SMBv1 EternalBlue scan
07:49:52  192.168.1.45    192.168.1.12:445    SMB       EXPLOIT ATTEMPT → SUCCESS (MS17-010)
07:50:09  192.168.1.12    185.220.101.9:443   HTTPS     C2 Beacon (new infected host)
07:53:28  192.168.1.45    192.168.1.28:445    SMB       EXPLOIT ATTEMPT → SUCCESS (MS17-010)
07:58:17  192.168.1.45    192.168.1.33:445    SMB       EXPLOIT ATTEMPT → SUCCESS (MS17-010)
08:05:44  Multiple hosts  185.220.101.9:443   HTTPS     C2 Beacons × 7 hosts
08:10:02  192.168.1.45    192.168.1.0/24      BROADCAST File encryption broadcast detected
──────────────────────────────────────────────────────────────────────
DNS QUERY (07:43:08): lockbyte-c2.zz → 185.220.101.9  [C2 domain]\
""",
                "explain": (
                    "**C2 servers, SMB, EternalBlue, and lateral movement**\n\n"
                    "- A **C2 (Command and Control) server** is a remote server the malware "
                    "'phones home' to for instructions and to exfiltrate data.\n"
                    "- **SMB (Server Message Block)** is the protocol Windows uses for file "
                    "sharing on a local network. **EternalBlue (MS17-010)** is a critical "
                    "Windows vulnerability that allows attackers to remotely execute code via SMB.\n"
                    "- **Lateral movement** is when malware moves from one machine to others "
                    "on the same network. The NIDS log shows infection spreading from "
                    "`192.168.1.45` to multiple hosts in under 30 minutes.\n"
                    "- The `User-Agent: LockByte/2.1` in the C2 beacon is the malware "
                    "identifying itself — a forensic artefact confirming the malware family."
                ),
            },
            {
                "label": "EVIDENCE 003 — Endpoint Forensic Timeline (STAFF-PC-07 / Patient Zero)",
                "dot": "ev-dot-green",
                "content": """\
[DIGITAL FORENSICS — ENDPOINT TIMELINE]
Machine:   STAFF-PC-07  |  IP: 192.168.1.45  |  Hostname: GFA-STAFF-07
User:      Mr. David Osei (Science Teacher)
OS:        Windows 10 21H2  |  Last Patched: 2023-11-14  [CRITICAL: unpatched 18 months]
──────────────────────────────────────────────────────────────────────
TIMESTAMP        EVENT                                SOURCE
07:31:04         Email received from unknown sender   Outlook mail client
                 Subject: "Updated Grade Sheets for Moderation"
                 Attachment: GradeSheet_Final.xlsx.exe
07:38:19         File saved to Downloads              $MFT filesystem record
07:38:21         File executed (user double-clicked)  Windows Prefetch (PF hash: 3A9F)
07:38:25         GradeSheet_Final.xlsx.exe spawned:   Process tree (Event ID 4688)
                   → cmd.exe /c powershell -enc BASE64PAYLOAD
                   → powershell.exe  [downloaded dropper]
07:39:42         AV ALERT (quarantine failed)         GreenShield EDR
07:40:08         Registry persistence key created:    Windows Registry (Event ID 13)
                   HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
                   Key: "WindowsSecurityUpdate"  → GradeSheet_Final.xlsx.exe
07:40:44         Shadow copy deletion:                VSS event log (Event ID 8193)
                   vssadmin delete shadows /all /quiet
07:43:08         DNS query: lockbyte-c2.zz            Sysmon Event ID 22
07:43:11         First outbound C2 connection         Sysmon Event ID 3 (Network)\
""",
                "explain": (
                    "**Endpoint forensics: process tree, registry persistence, and VSS deletion**\n\n"
                    "- **Windows Event IDs** are unique codes logged for every system action. "
                    "Event ID 4688 = new process created; Event ID 13 = registry value modified.\n"
                    "- The malware launched `cmd.exe` which launched `powershell.exe` to download "
                    "additional components — this is called a **dropper/loader** pattern.\n"
                    "- A **registry Run key** makes the malware start automatically on every reboot "
                    "— this is called **persistence**.\n"
                    "- `vssadmin delete shadows /all /quiet` deletes Windows **Volume Shadow Copies** "
                    "(VSS) — local backups Windows creates automatically. This prevents easy file recovery.\n"
                    "- The machine was **unpatched for 18 months**, leaving it vulnerable to "
                    "EternalBlue (MS17-010), enabling the subsequent network spread."
                ),
            },
        ],
        "questions": [
            {
                "text": "Q1 — STAFF-PC-07's Windows OS had not been patched for 18 months. How does this relate to the ransomware spreading across the network?",
                "options": [
                    "It has no direct relevance; the malware spread through the Wi-Fi password.",
                    "Unpatched machines lack security updates, leaving MS17-010 (EternalBlue) open — the exact SMB exploit the malware used to move laterally to other machines.",
                    "It caused the antivirus to stop working, which allowed the malware to run.",
                    "Old operating systems cannot run AV software, making them easy targets.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** MS17-010 (EternalBlue) is a critical SMB vulnerability "
                    "patched by Microsoft in March 2017. Machines that have not applied this "
                    "patch remain vulnerable. The NIDS log shows the malware explicitly scanning "
                    "for SMB (port 445) and successfully exploiting MS17-010 on three machines "
                    "(192.168.1.12, .28, .33) within minutes. A single unpatched machine "
                    "acting as Patient Zero effectively endangered the entire school network."
                ),
            },
            {
                "text": "Q2 — The malware deleted Volume Shadow Copies immediately after establishing persistence. Why is this step critical for the attacker?",
                "options": [
                    "Shadow copies slow down the encryption process, so the malware removes them for speed.",
                    "Shadow copies are Windows' built-in local backup mechanism; deleting them prevents the school from recovering files without paying the ransom.",
                    "Shadow copies contain logs that could identify the attacker.",
                    "The malware needed to free up disk space for the encrypted file storage.",
                ],
                "answer": 1,
                "explain": (
                    "✅ **Correct.** Volume Shadow Copies (VSS) are automatic Windows backups "
                    "that allow users to restore previous file versions without external backups. "
                    "Ransomware groups universally delete VSS as one of their first actions because "
                    "it eliminates the easiest free recovery option, maximising pressure to pay. "
                    "The command `vssadmin delete shadows /all /quiet` is so commonly associated "
                    "with ransomware that it is now a standalone detection rule in most EDR products."
                ),
            },
            {
                "text": "Q3 — Using all three evidence sources, which statement best identifies Patient Zero and the complete infection chain?",
                "options": [
                    "A student brought in an infected USB drive and plugged it into STAFF-PC-07.",
                    "The school's web server was exploited by an external attacker who pushed malware directly.",
                    "Mr. Osei opened a malicious email attachment on STAFF-PC-07 at 07:38; the malware beaconed to C2 at 07:43, then exploited unpatched SMB on three adjacent machines, spreading to 7+ hosts within 30 minutes.",
                    "The malware was pre-installed by the school's IT supplier and activated remotely.",
                ],
                "answer": 2,
                "explain": (
                    "✅ **Correct.** The three evidence sources form a complete chain: "
                    "Evidence 3 (endpoint) shows Mr. Osei executing the attachment at 07:38:21 on "
                    "STAFF-PC-07; Evidence 1 (AV alert) confirms the malware family and file hash; "
                    "Evidence 2 (NIDS) shows the C2 beacon at 07:43:11 and subsequent EternalBlue "
                    "exploitation of three machines, growing to 7 infected hosts by 08:05. "
                    "STAFF-PC-07 is definitively Patient Zero. The entire network compromise "
                    "took under 30 minutes from a single email attachment."
                ),
            },
        ],
        "summary": (
            "**Case Conclusion — Malware Incident**\n\n"
            "At 07:31, Mr. David Osei on STAFF-PC-07 received a spearphishing email with "
            "attachment `GradeSheet_Final.xlsx.exe` (SHA-256: 4a5b...4a5b). Upon execution "
            "at 07:38:21, the LockByte v2.1 ransomware dropped a PowerShell loader, established "
            "persistence via a Registry Run key, deleted all Volume Shadow Copies, and "
            "beaconed to C2 server `185.220.101.9` at 07:43:11. The malware then exploited "
            "MS17-010 (EternalBlue) via SMB port 445, spreading to at least 7 unpatched "
            "machines within 30 minutes. Files with extensions .docx, .xlsx, .pdf, and .pptx "
            "across local and network drives were encrypted with AES-256.\n\n"
            "**Recommended actions:** Do not pay the ransom. Restore all files from the most "
            "recent **offline** backup. Apply MS17-010 patch to all machines immediately. "
            "Disable SMBv1 network-wide. Implement email attachment sandboxing. Deploy EDR "
            "on all endpoints. Report to the National Cyber Security Centre with IoCs: "
            "`185.220.101.9`, `lockbyte-c2.zz`, file hash `a1b2c3d4...` (MD5)."
        ),
    },
]



# ── Constants ─────────────────────────────────────────────────────────────────
DIFF_CSS   = {"beginner": "diff-beginner", "intermediate": "diff-intermediate", "advanced": "diff-advanced"}
DIFF_LABEL = {"beginner": "Beginner",      "intermediate": "Intermediate",      "advanced": "Advanced"}
TOTAL_Qs   = sum(len(c["questions"]) for c in CASES)   # 15
MAX_SCORE  = TOTAL_Qs                                   # 1 pt per correct answer

STAGE_LABELS = ["1 · Overview", "2 · Evidence", "3 · Analysis", "4 · Findings"]


# ── Score helpers ─────────────────────────────────────────────────────────────

def _case_score(case_id: int) -> int:
    """Return the locked score for a case, or 0 if not yet submitted."""
    return st.session_state.scores.get(f"case_{case_id}", 0)


def _total_score() -> int:
    return sum(_case_score(i) for i in range(len(CASES)))


def _completed_cases() -> int:
    return sum(1 for i in range(len(CASES)) if st.session_state.submitted.get(f"case_{i}", False))


def _case_status(case_id: int) -> tuple:
    """Return (css_class, label) for a case card status badge."""
    key = f"case_{case_id}"
    if st.session_state.submitted.get(key):
        return "status-complete", "Complete"
    if key in st.session_state.answers and st.session_state.answers[key]:
        return "status-inprogress", "In Progress"
    return "status-open", "Open"


# ── Shared components ─────────────────────────────────────────────────────────

def render_navbar(show_back: bool = False, case_title: str = ""):
    total     = _total_score()
    completed = _completed_cases()
    crumb = f'<span class="navbar-meta">/ {case_title}</span>' if show_back else ""
    st.markdown(
        f'<div class="navbar">'
        f'<div class="navbar-brand">Cyber<span>Trace</span></div>'
        f'<div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;">'
        f'{crumb}'
        f'<span class="navbar-meta">Digital Forensics Training</span>'
        f'<span class="navbar-score">Score: {total}/{MAX_SCORE} &nbsp;·&nbsp; {completed}/{len(CASES)} cases</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        """
<div class="footer">
    CyberTrace &nbsp;·&nbsp; Digital Forensics Training Platform &nbsp;·&nbsp;
    All cases, names, IP addresses, and organisations are entirely fictional
    and created for educational purposes only.
</div>
""",
        unsafe_allow_html=True,
    )


def render_stage_bar(current: int):
    """Render the 4-step investigation progress bar."""
    steps_html = ""
    for i, label in enumerate(STAGE_LABELS):
        if i < current:
            cls = "stage-step stage-done"
        elif i == current:
            cls = "stage-step stage-active"
        else:
            cls = "stage-step"
        steps_html += f'<div class="{cls}">{label}</div>'
    st.markdown(f'<div class="stage-bar">{steps_html}</div>', unsafe_allow_html=True)


def render_dashboard_panel():
    """Progress panel on the home page."""
    total = _total_score()
    done  = _completed_cases()
    n     = len(CASES)
    pct   = int(done / n * 100)

    case_cells = ""
    for i, c in enumerate(CASES):
        sc        = _case_score(i)
        submitted = st.session_state.submitted.get(f"case_{i}", False)
        q_total   = len(c["questions"])
        if submitted:
            icon      = "✅"
            label_col = "#3dba6c"
            score_str = f"{sc}/{q_total} pts"
        elif st.session_state.answers.get(f"case_{i}"):
            icon      = "🔵"
            label_col = "#3b9eff"
            score_str = "in progress"
        else:
            icon      = "○"
            label_col = "#2d4a68"
            score_str = "not started"
        case_cells += (
            f'<div class="dash-stat">'
            f'<div style="font-size:1.1rem;line-height:1.4;">{icon}</div>'
            f'<div style="font-size:0.68rem;color:{label_col};font-family:\'Share Tech Mono\',monospace;'
            f'margin-top:0.25rem;letter-spacing:0.04em;word-break:break-word;line-height:1.35;">'
            f'{c["title"]}</div>'
            f'<div style="font-size:0.63rem;color:#2d5070;margin-top:0.2rem;">{score_str}</div>'
            f'</div>'
        )

    st.markdown(
        f"""
<div class="dash-progress">
<div class="dash-progress-title">📊 &nbsp; Your Investigation Progress</div>
<div class="dash-stat-grid">
<div class="dash-stat"><div class="dash-stat-num">{total}</div><div class="dash-stat-label">Total Score</div></div>
<div class="dash-stat"><div class="dash-stat-num">{done}/{n}</div><div class="dash-stat-label">Cases Done</div></div>
<div class="dash-stat"><div class="dash-stat-num">{MAX_SCORE}</div><div class="dash-stat-label">Max Points</div></div>
<div class="dash-stat"><div class="dash-stat-num">{pct}%</div><div class="dash-stat-label">Completion</div></div>
</div>
<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{pct}%;"></div></div>
<div class="progress-label">{done} of {n} cases completed &nbsp;·&nbsp; {total} / {MAX_SCORE} points</div>
</div>
<div style="margin-bottom:1.6rem;">
<div class="sec-head" style="margin-bottom:0.6rem;">📋 &nbsp; Case Status</div>
<div class="dash-stat-grid" style="grid-template-columns:repeat(auto-fill,minmax(160px,1fr));">{case_cells}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ── Home page ─────────────────────────────────────────────────────────────────

def render_home():
    _scroll_top()
    render_navbar()

    st.markdown("""
<div class="hero">
<div class="hero-badge">🔐 &nbsp; Educational Platform &nbsp;·&nbsp; Digital Forensics</div>
<h1 class="hero-title">Cyber<span>Trace</span></h1>
<p class="hero-subtitle">
Explore Digital Evidence.&nbsp; Investigate Cybercrime.&nbsp; Think Like an Investigator.
</p>
<p class="hero-intro">
CyberTrace is a digital forensics training platform. Work through five fictional cybercrime
cases, examine realistic-style evidence, answer investigative questions, and read expert
conclusions. All data is entirely fictional and labelled for educational use.
</p>
</div>
""", unsafe_allow_html=True)

    render_dashboard_panel()

    st.markdown(
        '<p class="sec-head">🗂 &nbsp; Active Investigation Cases</p>'
        '<p class="sec-sub">Select a case to open the investigation. Cases can be completed in any order.</p>',
        unsafe_allow_html=True,
    )

    # Each card and its button rendered together in the same column cell.
    # Using st.columns so that st.button() (a Python widget) sits directly
    # below its card HTML — this is the only reliable way to keep them paired.
    cols = st.columns(3, gap="medium")
    for i, case in enumerate(CASES):
        with cols[i % 3]:
            diff_cls           = DIFF_CSS.get(case["difficulty"], "diff-beginner")
            diff_lbl           = DIFF_LABEL.get(case["difficulty"], "Beginner")
            stat_cls, stat_lbl = _case_status(i)
            sc                 = _case_score(i)
            q_total            = len(case["questions"])
            score_html         = (
                f'<div class="card-score">Score: {sc}/{q_total}</div>'
                if st.session_state.submitted.get(f"case_{i}") else ""
            )
            st.markdown(
                f"""
<div class="card">
<div class="card-top">
<span class="card-icon">{case["icon"]}</span>
<span class="card-status {stat_cls}">{stat_lbl}</span>
</div>
<div style="display:flex;gap:0.4rem;align-items:center;margin-bottom:0.35rem;flex-wrap:wrap;">
<span class="card-cat">{case["tag"]}</span>
<span class="diff-badge {diff_cls}">{diff_lbl}</span>
</div>
<div class="card-title">{case["title"]}</div>
<p class="card-desc">{case["desc"]}</p>
<div class="card-meta"><span>📂 {case["evidence_types"]}</span></div>
{score_html}
</div>
""",
                unsafe_allow_html=True,
            )
            done      = st.session_state.submitted.get(f"case_{i}", False)
            btn_label = "Review Investigation →" if done else "Open Investigation →"
            if st.button(btn_label, key=f"btn_home_{i}"):
                st.session_state.page = f"case_{i}"
                st.session_state.scroll_to_top = True
                st.rerun()

    render_footer()


# ── Case investigation page ───────────────────────────────────────────────────

def render_case(case_id: int):
    _scroll_top()
    case        = CASES[case_id]
    key_prefix  = f"case_{case_id}"
    n_questions = len(case["questions"])

    render_navbar(show_back=True, case_title=case["title"])

    # ── Navigation bar ───────────────────────────────────────────────────────
    bcol, _ = st.columns([2, 10])
    with bcol:
        if st.button("← All Cases", key=f"back_{case_id}"):
            st.session_state.page = "home"
            st.session_state.scroll_to_top = True
            st.rerun()

    # ── Stage state ──────────────────────────────────────────────────────────
    submitted = st.session_state.submitted.get(key_prefix, False)
    # Once submitted, always jump to stage 3 (findings).
    if submitted:
        stage = 3
    else:
        stage = st.session_state.stage.get(key_prefix, 0)

    if key_prefix not in st.session_state.answers:
        st.session_state.answers[key_prefix] = {}

    # ── Investigation header ─────────────────────────────────────────────────
    diff_cls = DIFF_CSS.get(case["difficulty"], "diff-beginner")
    diff_lbl = DIFF_LABEL.get(case["difficulty"], "Beginner")
    st.markdown(
        f"""
<div class="inv-header">
<div class="inv-cat">
{case["icon"]} &nbsp; {case["tag"]} &nbsp;·&nbsp;
<span class="diff-badge {diff_cls}" style="vertical-align:middle;">{diff_lbl}</span>
</div>
<div class="inv-title">{case["title"]}</div>
<p class="inv-obj"><strong>Objective:</strong> {case["objective"]}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── Stage progress bar ───────────────────────────────────────────────────
    render_stage_bar(stage)

    # ════════════════════════════════════════════════════════════════════════
    # STAGE 0 — Case Overview
    # ════════════════════════════════════════════════════════════════════════
    if stage == 0:
        st.markdown(
            '<p class="sec-head">📋 Stage 1 — Case Overview</p>'
            '<p class="sec-sub">Read the briefing carefully before examining the evidence.</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="stage-panel"><div class="stage-panel-title">🗂 Case Briefing</div>',
            unsafe_allow_html=True,
        )
        st.markdown(case["background"])
        st.markdown("</div>", unsafe_allow_html=True)

        n_ev = len(case["evidence"])
        st.markdown(
            f"""
<div class="stage-panel" style="margin-top:0.8rem;">
<div class="stage-panel-title">📌 Investigation Facts</div>
<div class="finding-row"><span class="finding-icon">🎯</span><span class="finding-text"><strong>Objective:</strong> {case["objective"]}</span></div>
<div class="finding-row"><span class="finding-icon">📂</span><span class="finding-text"><strong>Evidence types:</strong> {case["evidence_types"]}</span></div>
<div class="finding-row"><span class="finding-icon">🔬</span><span class="finding-text"><strong>Evidence items:</strong> {n_ev} (simulated training data)</span></div>
<div class="finding-row"><span class="finding-icon">🧩</span><span class="finding-text"><strong>Questions:</strong> {n_questions} (1 point each, max {n_questions} pts)</span></div>
<div class="finding-row"><span class="finding-icon">⚠️</span><span class="finding-text">All evidence is <strong>entirely fictional</strong> and labelled [SIM] / [TRAINING DATA]. It does not represent real incidents, persons, or verified threat intelligence.</span></div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        _, btn_col, _ = st.columns([1, 3, 1])
        with btn_col:
            if st.button("Proceed to Evidence Examination →", key=f"stage0_{key_prefix}"):
                st.session_state.stage[key_prefix] = 1
                st.session_state.scroll_to_top = True
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # STAGE 1 — Evidence Collection & Examination
    # ════════════════════════════════════════════════════════════════════════
    elif stage == 1:
        st.markdown(
            '<p class="sec-head">🔎 Stage 2 — Evidence Examination</p>'
            '<p class="sec-sub">Examine each piece of evidence. Expand the analyst notes to understand what each item means.</p>',
            unsafe_allow_html=True,
        )

        for ev_idx, ev in enumerate(case["evidence"]):
            dot = ev.get("dot", "ev-dot-blue")
            coc = '<span class="coc-tag">SIM</span><span class="coc-tag">TRAINING DATA</span>'
            st.markdown(
                f"""
<div class="ev-outer">
<div class="ev-title-bar">
<span class="ev-dot {dot}"></span>
<span class="ev-label">{ev["label"]}</span>
{coc}
</div>
<div class="ev-body">{ev["content"]}</div>
</div>
""",
                unsafe_allow_html=True,
            )
            with st.expander(
                "📖 Analyst Notes — What does this evidence mean?",
                expanded=(ev_idx == 0),
            ):
                st.markdown(
                    f'<div class="callout">{ev["explain"]}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        nav_l, nav_r = st.columns(2)
        with nav_l:
            if st.button("← Back to Overview", key=f"stage1_back_{key_prefix}"):
                st.session_state.stage[key_prefix] = 0
                st.session_state.scroll_to_top = True
                st.rerun()
        with nav_r:
            if st.button("Proceed to Analysis Questions →", key=f"stage1_fwd_{key_prefix}"):
                st.session_state.stage[key_prefix] = 2
                st.session_state.scroll_to_top = True
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # STAGE 2 — Analysis (questions)
    # ════════════════════════════════════════════════════════════════════════
    elif stage == 2:
        st.markdown(
            '<p class="sec-head">🧩 Stage 3 — Analysis</p>'
            '<p class="sec-sub">Answer all questions based on the evidence. Scores are locked after submitting — you cannot change answers.</p>',
            unsafe_allow_html=True,
        )

        for q_idx, q in enumerate(case["questions"]):
            q_key = f"{key_prefix}_q{q_idx}"
            st.markdown(
                f'<div class="q-block">'
                f'<div class="q-num">Question {q_idx + 1} of {n_questions}</div>'
                f'<div class="q-label">{q["text"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            opts   = ["— Select an answer —"] + q["options"]
            choice = st.radio(
                label=q["text"],
                options=opts,
                index=0,
                key=q_key,
                label_visibility="collapsed",
            )
            if choice != "— Select an answer —":
                st.session_state.answers[key_prefix][q_idx] = q["options"].index(choice)
            else:
                st.session_state.answers[key_prefix][q_idx] = None
            st.write("")

        nav_l, _, nav_r = st.columns([2, 3, 2])
        with nav_l:
            if st.button("← Back to Evidence", key=f"stage2_back_{key_prefix}"):
                st.session_state.stage[key_prefix] = 1
                st.session_state.scroll_to_top = True
                st.rerun()
        with nav_r:
            if st.button("✔ Submit & View Findings", key=f"submit_{key_prefix}"):
                answers     = st.session_state.answers.get(key_prefix, {})
                all_answered = all(
                    answers.get(qi) is not None for qi in range(n_questions)
                )
                if not all_answered:
                    st.warning("⚠️ Please answer all questions before submitting.")
                else:
                    # Lock score only on the very first submission
                    if key_prefix not in st.session_state.scores:
                        locked_score = sum(
                            1 for qi, q in enumerate(case["questions"])
                            if answers.get(qi) == q["answer"]
                        )
                        st.session_state.scores[key_prefix] = locked_score
                    st.session_state.submitted[key_prefix] = True
                    st.session_state.stage[key_prefix]     = 3
                    st.session_state.scroll_to_top = True
                    st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # STAGE 3 — Findings & Conclusion
    # ════════════════════════════════════════════════════════════════════════
    elif stage == 3:
        answers  = st.session_state.answers.get(key_prefix, {})
        score    = st.session_state.scores.get(key_prefix, 0)
        total_q  = n_questions

        st.markdown(
            '<p class="sec-head">📁 Stage 4 — Findings & Conclusion</p>'
            '<p class="sec-sub">Review your answers, read the explanations, and study the case conclusion.</p>',
            unsafe_allow_html=True,
        )

        # Score banner
        if score == total_q:
            st.markdown(
                f'<div class="score-perfect">🎉 Outstanding — {score}/{total_q} correct. Full marks!</div>',
                unsafe_allow_html=True,
            )
        elif score >= (total_q + 1) // 2:
            st.markdown(
                f'<div class="score-good">👍 Good work — {score}/{total_q} correct. Review the explanations below.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="score-low">📚 {score}/{total_q} correct. Study the explanations and evidence carefully.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Per-question results
        st.markdown(
            '<p class="sec-head" style="font-size:0.95rem;">Answer Review</p>',
            unsafe_allow_html=True,
        )
        for q_idx, q in enumerate(case["questions"]):
            chosen  = answers.get(q_idx)
            correct = q["answer"]
            verdict = "✅ Correct" if chosen == correct else "❌ Incorrect"
            v_color = "#3dba6c"   if chosen == correct else "#d94040"

            st.markdown(
                f'<div class="q-block">'
                f'<div class="q-num" style="color:{v_color};">{verdict} — Question {q_idx + 1} of {total_q}</div>'
                f'<div class="q-label">{q["text"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            for opt_idx, opt_text in enumerate(q["options"]):
                if opt_idx == correct:
                    st.markdown(
                        f'<div class="opt-correct">✅ &nbsp;{opt_text}</div>',
                        unsafe_allow_html=True,
                    )
                elif opt_idx == chosen and chosen != correct:
                    st.markdown(
                        f'<div class="opt-wrong">❌ &nbsp;{opt_text}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="opt-neutral">○ &nbsp;{opt_text}</div>',
                        unsafe_allow_html=True,
                    )
            with st.expander("📖 Explanation"):
                st.markdown(q["explain"])
            st.write("")

        st.divider()

        # Case summary / conclusion
        st.markdown(
            f"""
<div class="summary-box">
<h4>📁 Case Conclusion & Recommended Actions</h4>
<p>{case["summary"].replace(chr(10), "<br>")}</p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        nav_l, nav_r = st.columns(2)
        with nav_l:
            if st.button("← Review Evidence Again", key=f"stage3_ev_{key_prefix}"):
                st.session_state.stage[key_prefix] = 1
                st.session_state.scroll_to_top = True
                st.rerun()
        with nav_r:
            if st.button("← Return to Case List", key=f"stage3_home_{key_prefix}"):
                st.session_state.page = "home"
                st.session_state.scroll_to_top = True
                st.rerun()

    render_footer()


# ── Page router ───────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    render_home()
elif page.startswith("case_"):
    try:
        case_index = int(page.split("_")[1])
        if 0 <= case_index < len(CASES):
            render_case(case_index)
        else:
            st.session_state.page = "home"
            st.rerun()
    except (ValueError, IndexError):
        st.session_state.page = "home"
        st.rerun()
else:
    st.session_state.page = "home"
    st.rerun()

# Reset scroll only AFTER the new page/stage has been rendered.
# This avoids the previous early reset and avoids repeated timer loops.
if st.session_state.scroll_to_top:
    st.session_state.scroll_to_top = False
    st.html(
        "<script>"
        "requestAnimationFrame(function(){"
        "requestAnimationFrame(function(){"
        "var el=document.querySelector('[data-testid=\"stAppViewContainer\"]');"
        "if(el){el.scrollTo({top:0,left:0,behavior:'auto'});el.scrollTop=0;}"
        "var main=document.querySelector('[data-testid=\"stMain\"]');"
        "if(main){main.scrollTop=0;}"
        "});"
        "});"
        "</script>",
        unsafe_allow_javascript=True,
    )
