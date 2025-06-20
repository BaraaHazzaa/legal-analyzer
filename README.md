# ⚖️ LegalMind AI — Contract Analyzer

**LegalMind AI** is an intelligent contract summarization tool for legal professionals. It uses cutting-edge NLP models to generate concise summaries of long legal documents, helping save time and improve comprehension.

---

## 🚀 Features

- 🔍 **AI-Powered Summarization** using Transformer models (e.g. `facebook/bart-large-cnn`)
- ⚡ **GPU Acceleration** if available, for faster performance
- 📥 Input via **file upload**, **direct text**, or **sample contract**
- 📊 Dynamic **summary length tuning** for optimal output
- 🧠 Summary **metrics**: original length, compression ratio, processing time
- 🧾 **Analysis history** with detailed summaries and full document view
- 💾 **SQLite database** with content hashing to prevent duplicates
- 🎨 Sleek **Streamlit UI** with custom CSS and tabbed layout

---


## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/BaraaHazzaa/legal-analyzer.git
cd legal-analyzer
```

### 2. Install dependencies

Make sure Python 3.8+ is installed.

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is missing, create it manually with:
```text
streamlit
transformers
torch
```

### 3. Run the app

```bash
streamlit run app.py
```

---

## 💡 Sample Usage

- Upload a `.txt` contract file, or paste text manually
- Click **"Analyze Contract"**
- View the AI-generated summary and metrics
- Browse past analyses in the **History & Insights** tab

---

## 📁 Project Structure

```
legal-analyzer/
├── app.py                  # Streamlit frontend + app logic
├── model.py                # Summarization model loading
├── .gitignore
├── contract_analytics.db   # (Ignored) SQLite DB for history
├── model_cache/            # (Ignored) Local HuggingFace cache
├── test_contract.txt       # Sample contract text
└── README.md               # You're here!
```

---

## 📌 Notes

- Uses GPU if available (`torch.cuda.is_available()`)
- Local caching for models speeds up load time
- Summaries stored in SQLite with content hashing

---

## ✅ TODO / Future Improvements

- [ ] PDF and DOCX parsing support
- [ ] User authentication & per-user history
- [ ] Export summaries as PDF/Word
- [ ] Search/filter saved analyses

---

## 👤 Author

**Baraa Hazzaa**  
[GitHub](https://github.com/BaraaHazzaa)
