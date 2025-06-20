# ---------- app.py (Major Upgrade) ----------
import streamlit as st
import sqlite3
import os
import hashlib
import time
from model import tokenizer, model  # Import from our model module
import torch
from transformers import pipeline
from contextlib import closing

# ===== Configuration =====
DB_PATH = "contract_analytics.db"
MAX_INPUT_LENGTH = 10000  # Characters
HISTORY_LIMIT = 50

# ===== Database Setup =====
def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            text_hash TEXT NOT NULL UNIQUE,
            original_length INTEGER,
            summary TEXT,
            processing_time REAL
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS document_texts (
            text_hash TEXT PRIMARY KEY,
            content TEXT NOT NULL
        )
        """)
        conn.commit()

# ===== Summarization Service =====
class SummarizationEngine:
    _instance = None
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        st.toast(f"Using {'GPU 🔥' if self.device == 'cuda' else 'CPU ⚙️'} acceleration")
        
        self.model = model.to(self.device)
        self.tokenizer = tokenizer
        self.summarizer = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1
        )
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SummarizationEngine()
        return cls._instance
    
    def summarize(self, text: str) -> dict:
        """Generate summary with performance metrics"""
        start_time = time.time()
        
        # Preprocessing
        clean_text = text.strip()[:MAX_INPUT_LENGTH]
        
        # Dynamic length adjustment
        input_length = len(clean_text.split())
        max_length = min(300, max(50, int(input_length * 0.3)))
        min_length = min(100, max(30, int(input_length * 0.1)))
        
        # Generate summary
        with torch.no_grad():
            summary_result = self.summarizer(
                clean_text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )
        
        processing_time = time.time() - start_time
        return {
            "summary": summary_result[0]['summary_text'],
            "original_length": len(clean_text),
            "summary_length": len(summary_result[0]['summary_text']),
            "compression_ratio": len(clean_text) / max(1, len(summary_result[0]['summary_text'])),
            "processing_time": processing_time
        }

# ===== Database Operations =====
def save_analysis(text: str, result: dict):
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    
    with closing(sqlite3.connect(DB_PATH)) as conn:
        # Store original text separately
        conn.execute(
            "INSERT OR IGNORE INTO document_texts (text_hash, content) VALUES (?, ?)",
            (text_hash, text)
        )
        
        # Save analysis metadata
        conn.execute(
            """INSERT INTO analyses (
                text_hash, original_length, summary, processing_time
            ) VALUES (?, ?, ?, ?)""",
            (text_hash, result["original_length"], result["summary"], result["processing_time"])
        )
        conn.commit()

def get_recent_analyses(limit=10):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.execute("""
            SELECT a.id, a.created_at, a.original_length, a.summary, a.processing_time, d.content
            FROM analyses a
            JOIN document_texts d ON a.text_hash = d.text_hash
            ORDER BY a.created_at DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

# ===== Streamlit UI =====
def main():
    # Initialize app
    st.set_page_config(
        page_title="LegalMind AI - Contract Analyzer",
        page_icon="⚖️",
        layout="wide"
    )
    init_db()
    summarizer = SummarizationEngine.get_instance()
    
    # Custom CSS
    st.markdown("""
    <style>
        .summary-box { 
            border-left: 4px solid #4cc9f0;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 0 8px 8px 0;
            color: #333333 !important;  /* Explicit dark text */
            font-size: 16px;
            line-height: 1.6;
        }
        /* Fix Streamlit's default white background */
        .stMarkdown {
            background-color: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("⚖️ LegalMind AI - Contract Analyzer")
    st.caption("AI-powered contract summarization for legal professionals")
    
    # Main content tabs
    tab1, tab2 = st.tabs(["Analyze Contract", "History & Insights"])
    
    with tab1:
        # Input options
        input_method = st.radio("Input method:", 
                               ("File Upload", "Direct Input", "Sample Contract"), 
                               horizontal=True)
        
        text = ""
        if input_method == "File Upload":
            uploaded_file = st.file_uploader("Upload contract document", 
                                           type=["txt", "pdf", "docx"],
                                           help="Supports text, PDF, and Word documents")
            if uploaded_file:
                if uploaded_file.type == "text/plain":
                    text = uploaded_file.read().decode("utf-8")
                else:
                    st.warning("PDF/Word support requires additional libraries. Using text input.")
        
        elif input_method == "Direct Input":
            text = st.text_area("Paste contract text:", height=300,
                               placeholder="Enter contract text here...")
        
        else:  # Sample contract
            with open("test_contract.txt", "r") as f:
                text = f.read()
            st.code(text[:500] + "... [SAMPLE TEXT TRUNCATED]", language="text")
        
        # Analysis controls
        if st.button("Analyze Contract", type="primary", disabled=not text.strip()):
            with st.spinner("Analyzing contract terms..."):
                try:
                    # Process and summarize
                    result = summarizer.summarize(text)
                    
                    # Display results
                    st.subheader("AI Analysis Summary")
                    with st.container():
                        st.markdown(f'<div class="summary-box">{result["summary"]}</div>', 
                                   unsafe_allow_html=True)
                    
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Original Length", f"{result['original_length']:,} chars")
                    col2.metric("Summary Length", f"{result['summary_length']:,} chars")
                    col3.metric("Compression Ratio", f"{result['compression_ratio']:.1f}:1")
                    
                    # Save results
                    save_analysis(text, result)
                    st.success("Analysis saved to database!")
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.exception(e)
    
    with tab2:
        st.subheader("Analysis History")
        analyses = get_recent_analyses(HISTORY_LIMIT)
        
        if not analyses:
            st.info("No analysis history found")
        else:
            # Statistics dashboard
            total_analyses = len(analyses)
            avg_processing = sum(a[4] for a in analyses) / total_analyses
            avg_compression = sum(len(a[3])/a[2] for a in analyses) / total_analyses
            
            st.metric("Total Analyses", total_analyses)
            cols = st.columns(2)
            cols[0].metric("Avg. Processing Time", f"{avg_processing:.2f}s")
            cols[1].metric("Avg. Compression", f"{1/avg_compression:.1f}:1")
            
            # Detailed history
            st.subheader("Recent Analyses")
            for analysis in analyses:
                with st.expander(f"Analysis #{analysis[0]} - {analysis[1]}"):
                    st.caption(f"Processed in {analysis[4]:.2f} seconds")
                    st.write("**Summary:**")
                    st.write(analysis[3])
                    if st.button("View Original", key=f"view_{analysis[0]}"):
                        st.text_area("Full Text", analysis[5], height=300)

# Run the application
if __name__ == "__main__":
    main()