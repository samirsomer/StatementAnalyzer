# 📄 PDF Bank Statement Parser

A simple yet powerful **Streamlit web app** to parse and analyze bank and credit card PDF statements. It extracts tabular transaction data, provides summaries, allows manual editing, and enables CSV export.

---

## 🚀 Features

- 🔀 **Account Type Switch** (Current Account / Credit Card)
- 📄 Upload and process **multiple PDF statements**
- 📊 **Transaction summary** per statement
- 🧾 Inline **data editing**
- ⬇️ Export to **CSV**
- 🐍 Built with **Python**, uses `pdfplumber` and `camelot` for PDF parsing
- 🐳 Docker-ready

---

## 🧰 Tech Stack

- Python 3.10
- Streamlit
- pdfplumber (for current accounts)
- Camelot (for credit cards)
- Pandas

---

## 🧪 How It Works

### 🔁 Current Account PDFs

- Extracts tables using **pdfplumber**
- Parses date, description, debit, credit, and balance
- Calculates total debit/credit and date range

### 💳 Credit Card PDFs

- Extracts tables using **Camelot**
- Parses transaction date, posting date, description, and amount
- Identifies CR/DR values and computes totals

---

## 📦 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/pdf-bank-parser.git
cd pdf-bank-parser
```

### 2. Install dependencies
Make sure [Ghostscript](https://www.ghostscript.com/) is installed if you're running locally.
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

### 🐳 Run with Docker
### 1. Build the image
```bash
docker build -t pdf-bank-parser .
```

### 2. Run the container
```bash
docker run -p 8500:8500 -v "$(pwd)/app.py:/app/app.py" pdf-bank-parser
```
or using docker-compose
```bash
docker-compose up
```

### 📁 File Structure
```bash
.
├── app.py              # Streamlit app logic
├── Dockerfile          # Docker config
├── requirements.txt    # Python dependencies
└── README.md           # You're here!
```

### ✅ To-Do / Ideas
* Add OCR fallback for scanned PDFs
* Automatically detect account type
* Apply regex cleaning for improved robustness

