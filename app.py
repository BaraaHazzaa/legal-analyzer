import streamlit as st
import sqlite3
import os

# Suppress TensorFlow warnings (remove if TensorFlow is uninstalled)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Set up database
conn = sqlite3.connect('memory.db')
conn.execute('CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY, text TEXT, summary TEXT)')

# Summarize function
def summarize_contract(text):
    try:
        from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
        import torch

        # Check device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        st.write(f"Device set to use {device}")

        # Load summarizer
        model_name = 'sshleifer/distilbart-cnn-12-6'
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        summarizer = pipeline(
            'summarization',
            model=model,
            tokenizer=tokenizer,
            framework='pt',
            device=0 if device == 'cuda' else -1
        )
        
        # Dynamically adjust max_length (optional)
        input_length = len(text.split())
        max_length = min(150, input_length)
        
        with torch.no_grad():  # Reduce memory usage
            summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

# Save function
def save_analysis(text, summary):
    conn.execute('INSERT INTO analyses (text, summary) VALUES (?, ?)', (text, summary))
    conn.commit()

# Streamlit interface
st.title('Contract Analyzer')
uploaded_file = st.file_uploader('Upload a contract (text file)', type='txt')
if uploaded_file:
    text = uploaded_file.read().decode('utf-8')
    summary = summarize_contract(text)
    st.write('Summary:', summary)
    save_analysis(text, summary)
    st.success('Analysis saved!')