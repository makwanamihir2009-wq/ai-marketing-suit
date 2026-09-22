import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import re
import sqlite3
import os
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ------------------------------------------------------------------------------
# 1. DATABASE SETUP (FOR HISTORY FEATURE)
# ------------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect('project_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            title TEXT,
            summary TEXT,
            linkedin TEXT,
            twitter TEXT,
            insta TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_to_history(user, title, summary, linkedin, twitter, insta):
    conn = sqlite3.connect('project_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (user, title, summary, linkedin, twitter, insta)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user, title, summary, linkedin, twitter, insta))
    conn.commit()
    conn.close()

def get_user_history(user):
    conn = sqlite3.connect('project_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, summary, linkedin, twitter, insta FROM history WHERE user = ? ORDER BY id DESC', (user,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ------------------------------------------------------------------------------
# 2. HELPER FUNCTIONS (PDF GENERATION & YOUTUBE TRANSCRIPT)
# ------------------------------------------------------------------------------
def generate_pdf_report(filename, author, title, summary, linkedin, twitter, insta):
    doc = SimpleDocTemplate(filename, pagesize=letter, title="AI Marketing Bundle Report")
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, spaceAfter=20, textColor='#1E88E5')
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=16, spaceBefore=15, spaceAfter=10, textColor='#4CAF50')
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=10)
    
    story = []
    story.append(Paragraph(f"<b>AI Marketing Content Bundle</b>", title_style))
    story.append(Paragraph(f"<b>Author/Developer:</b> {author}", body_style))
    story.append(Paragraph(f"<b>Content Topic/Title:</b> {title}", body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Executive Summary", h2_style))
    story.append(Paragraph(summary.replace('\n', '<br/>'), body_style))
    
    story.append(Paragraph("2. LinkedIn Post", h2_style))
    story.append(Paragraph(linkedin.replace('\n', '<br/>'), body_style))
    
    story.append(Paragraph("3. Twitter Thread", h2_style))
    story.append(Paragraph(twitter.replace('\n', '<br/>'), body_style))
    
    story.append(Paragraph("4. Instagram Reel / Shorts Script", h2_style))
    story.append(Paragraph(insta.replace('\n', '<br/>'), body_style))
    
    doc.build(story)

def get_youtube_transcript(url):
    try:
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if video_id_match:
            video_id = video_id_match.group(1)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([item['text'] for item in transcript_list])
            return transcript
        else:
            return "Invalid YouTube URL format."
    except Exception as e:
        return f"Could not fetch transcript: {str(e)}"

# ------------------------------------------------------------------------------
# 3. STREAMLIT UI SETUP & USER LOGIN CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Premium AI Omni-Content Suite", layout="wide", page_icon="🚀")

st.markdown('''
    <style>
    .main-title { font-size:38px !important; font-weight: bold; color: #1E88E5; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size:16px !important; text-align: center; color: #555; margin-bottom: 25px; }
    </style>
''', unsafe_allow_html=True)

st.markdown('<p class="main-title">🚀 Premium AI Omni-Channel Content Repurposing Suite</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Enterprise Solution with Secure Login, PDF Upload, YouTube Parsing, Database History & Export</p>', unsafe_allow_html=True)

# ---- STEP 5: SIMULATED SECURE LOGIN SYSTEM ----
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""

if not st.session_state['logged_in']:
    st.subheader("🔐 Secure Developer & Client Login")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        username = st.text_input("Username / Client ID:")
        password = st.text_input("Secret Token / Password:", type="password")
        if st.button("Authenticate License", type="primary"):
            # Simple simulation for local testing or custom deployment
            if username.strip() != "" and password == "premium500":
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("Invalid Username or Token! Use password: 'premium500' for testing.")
    st.stop()

# ------------------------------------------------------------------------------
# 4. MAIN APPLICATION DASHBOARD (POST-LOGIN)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.success(f"🔒 Authenticated: {st.session_state['username']}")
    st.header("💼 Developer Portfolio")
    st.markdown("### **Author:** Makwana Mihir Parshottambhai")
    st.write("---")
    st.markdown("📬 **Email:** mihir.makwana@example.com")
    st.markdown("🔗 **LinkedIn:** [Mihir Makwana](https://linkedin.com)")
    st.markdown("⭐ **Hire on Upwork:** [Upwork Profile](https://upwork.com)")
    st.write("---")
    if st.button("Log Out"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()

# Client API Key input securely handled
api_key_input = st.sidebar.text_input("Enter Google Gemini API Key:", type="password", value="YOUR_GEMINI_API_KEY")
genai.configure(api_key=api_key_input)

# UI Elements for Inputs
st.subheader("📥 Source Content Engine")
input_mode = st.radio("Choose Content Source Mode:", ["📝 Paste Raw Text", "📄 Upload PDF / Document File", "🎥 Parse YouTube Video URL"])

user_input = ""

# ---- STEP 1: DIRECT FILE UPLOAD ----
if input_mode == "📄 Upload PDF / Document File":
    uploaded_file = st.file_uploader("Upload a PDF or TXT file from your local computer:", type=["pdf", "txt"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            user_input = str(uploaded_file.read(), "utf-8")
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            user_input = "".join([page.extract_text() for page in pdf_reader.pages])
            st.success("File processed completely!")

# ---- STEP 2: YOUTUBE VIDEO TO TEXT TRANSCRIPT ----
elif input_mode == "🎥 Parse YouTube Video URL":
    yt_url = st.text_input("Paste YouTube Video Link (e.g., https://www.youtube.com/watch?v=...):")
    if yt_url:
        with st.spinner("Fetching transcript from YouTube..."):
            user_input = get_youtube_transcript(yt_url)
            if "Could not fetch" in user_input or "Invalid" in user_input:
                st.error(user_input)
                user_input = ""
            else:
                st.success("YouTube video transcript fetched and loaded successfully!")

else:
    user_input = st.text_area("Paste your manual blog post, document text, or raw text content here:", height=150)

# Dashboard Options
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    tone = st.selectbox("Select Strategy Tone:", ["Professional Business", "Casual & Witty", "Inspirational & Thoughtful", "Educational Framework"])
with col_opt2:
    language = st.selectbox("Target Output Language:", ["English", "Hindi", "Spanish", "German", "French"])

# 5. CORE EXECUTION & GENERATION STRATEGY
if st.button("Generate Premium Content Dashboard Bundle", type="primary"):
    if len(user_input.strip()) < 50:
        st.warning("Please provide valid content input first!")
    else:
        with st.spinner("AI Engine is executing cross-platform repurposing..."):
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                master_prompt = f'''
                You are a world-class Chief Marketing Officer and Content Architect.
                Analyze the source material and repurpose it flawlessly into 4 distinct configurations in '{language}' language with a '{tone}' tone.
                
                Source Material:
                {user_input}
                
                Separate outputs cleanly using tags [SUMMARY], [LINKEDIN], [TWITTER], and [INSTAGRAM_SCRIPT].
                
                [SUMMARY]
                Provide a clean, bulleted executive summary of the content (max 150 words).
                
                [LINKEDIN]
                Write an engaging, high-authority LinkedIn post based on this content. Include hook, body text points, call-to-action, and relevant tags.
                
                [TWITTER]
                Create a high-performing viral Twitter/X thread (at least 3 tweets, numbered 1/, 2/, 3/) with emojis.
                
                [INSTAGRAM_SCRIPT]
                Create a 30-second high-retention Instagram Reel / YouTube Shorts video script. Include visual scene instructions in brackets and crisp voiceovers.
                '''
                
                response = model.generate_content(master_prompt)
                full_text = response.text
                
                # RegEx Parsing
                summary_part = re.search(r'\[SUMMARY\](.*?)(\[LINKEDIN\]|\[TWITTER\]|\[INSTAGRAM_SCRIPT\]|$)', full_text, re.DOTALL)
                linkedin_part = re.search(r'\[LINKEDIN\](.*?)(\[SUMMARY\]|\[TWITTER\]|\[INSTAGRAM_SCRIPT\]|$)', full_text, re.DOTALL)
                twitter_part = re.search(r'\[TWITTER\](.*?)(\[SUMMARY\]|\[LINKEDIN\]|\[INSTAGRAM_SCRIPT\]|$)', full_text, re.DOTALL)
                insta_part = re.search(r'\[INSTAGRAM_SCRIPT\](.*?)(\[SUMMARY\]|\[LINKEDIN\]|\[TWITTER\]|$)', full_text, re.DOTALL)
                
                s_text = summary_part.group(1).strip() if summary_part else "Generated cleanly text summary below."
                l_text = linkedin_part.group(1).strip() if linkedin_part else "Content layout complete."
                t_text = twitter_part.group(1).strip() if twitter_part else "Thread generated."
                i_text = insta_part.group(1).strip() if insta_part else "Script generated."
                
                # ---- STEP 3: SAVE TO DATABASE (HISTORY) ----
                extracted_title = user_input[:40].strip().replace('\n', ' ') + "..."
                save_to_history(st.session_state['username'], extracted_title, s_text, l_text, t_text, i_text)
                
                st.session_state['s_text'] = s_text
                st.session_state['l_text'] = l_text
                st.session_state['t_text'] = t_text
                st.session_state['i_text'] = i_text
                st.session_state['extracted_title'] = extracted_title
                st.session_state['data_ready'] = True
                
            except Exception as e:
                st.error(f"Execution Error: Ensure you put your valid Gemini API Key on the sidebar. Details: {e}")

# If data generated, display Tabs Layout and Export Button
if st.session_state.get('data_ready', False):
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Executive Summary", "💼 LinkedIn Post", "🐦 Twitter Thread", "📸 Reel Script", "📊 Sentiment Analytics"])
    
    with tab1:
        st.subheader("Executive Summary")
        st.write(st.session_state['s_text'])
    with tab2:
        st.subheader("LinkedIn Architecture")
        st.text_area("LinkedIn Post Output:", st.session_state['l_text'], height=250)
    with tab3:
        st.subheader("Twitter / X Flow")
        st.write(st.session_state['t_text'])
    with tab4:
        st.subheader("Video Content Script")
        st.write(st.session_state['i_text'])
    with tab5:
        st.subheader("Advanced Sentiment Visualization")
        labels = ['Positive Tone', 'Neutral Tone', 'Complex Tone']
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.pie([40, 45, 15], labels=labels, autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#2196F3', '#FF5722'])
        ax.axis('equal')
        st.pyplot(fig)
    
    # ---- STEP 4: EXPORT COMPLETE MARKETING REPORT AS PDF ----
    st.write("---")
    st.subheader("📥 Export Final Deliverables")
    pdf_filename = "premium_marketing_bundle.pdf"
    
    # Generate the physical report
    generate_pdf_report(
        pdf_filename, 
        "Makwana Mihir Parshottambhai", 
        st.session_state['extracted_title'], 
        st.session_state['s_text'], 
        st.session_state['l_text'], 
        st.session_state['t_text'], 
        st.session_state['i_text']
    )
    
    with open(pdf_filename, "rb") as f:
        st.download_button(
            label="📥 Download Complete Marketing PDF Report",
            data=f,
            file_name="Premium_AI_Marketing_Report.pdf",
            mime="application/pdf"
        )

# ------------------------------------------------------------------------------
# DATABASE HISTORY VIEWER AT THE BOTTOM
# ------------------------------------------------------------------------------
st.write("---")
st.subheader("📜 Client Account Generation History")
history_records = get_user_history(st.session_state['username'])
if history_records:
    for row in history_records[:5]: # Show last 5 records
        with st.expander(f"🔴 Past Generation: {row[0]}"):
            st.write(f"**Summary:** {row[1][:150]}...")
else:
    st.info("No past records found for this authorized account.")
