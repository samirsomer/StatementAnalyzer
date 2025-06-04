# app.py  –  Streamlit PDF bank-statement parser with account type switch
import logging
import pdfplumber
import pandas as pd
import streamlit as st
import camelot
import tempfile
from datetime import datetime


# -------------------------------------------------------------------
# Streamlit & logging setup
# -------------------------------------------------------------------
logging.getLogger("pdfminer").setLevel(logging.ERROR)
st.set_page_config(page_title="PDF Bank Parser", layout="wide")
st.title("📄 PDF Bank Statement Parser")

# -------------------------------------------------------------------
# Sidebar account type switch
# -------------------------------------------------------------------
account_type = st.sidebar.selectbox("Select account type:", ["Current Account", "Credit Card"])

# -------------------------------------------------------------------
# Upload widget
# -------------------------------------------------------------------
uploaded_files = st.file_uploader(
    f"Upload one or more **{account_type}** PDF statements",
    type="pdf",
    accept_multiple_files=True,
)


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

# -------------------------------------------------------------------
# PDF → DataFrame
# -------------------------------------------------------------------
def parse_pdf(file, account_type="Current Account"):
    
    if account_type == "Current Account":
        rows = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    for r in table:
                        if not r or r[0] in ("Date", ""):
                            continue
                        try:
                            rows.append(
                                [
                                    r[0],  # date
                                    r[1].replace("\n", " "),
                                    r[2].replace("-", ""),
                                    r[3].replace("-", ""),
                                    r[4].replace(" Cr", ""),
                                ]
                            )
                        except Exception as e:
                            continue
        col_names = ["date", "desc", "debit", "credit", "balance"]
        df = pd.DataFrame(rows, columns=col_names)
        df["dttime"] = pd.to_datetime(df["date"], errors="coerce")
        summary = {
            "Transactions": len(df),
            "Start Date": df["dttime"].min().strftime("%d-%m-%Y") if not df.empty else "-",
            "End Date":   df["dttime"].max().strftime("%d-%m-%Y") if not df.empty else "-",
            "Total Debit": pd.to_numeric(
                df.get("debit", pd.Series(dtype=float)).astype(str).str.replace(",", "", regex=False), errors="coerce"
            ).sum(skipna=True),
            "Total Credit": pd.to_numeric(
                df.get("credit", pd.Series(dtype=float)).astype(str).str.replace(",", "", regex=False), errors="coerce"
            ).sum(skipna=True),
        }
        return df.drop(columns=["dttime"], errors="ignore"), summary
    elif account_type == "Credit Card":
        rows = []
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file.read())
            tmp_file_path = tmp_file.name
        try:
            tables = camelot.read_pdf(tmp_file_path, pages='all', flavor='stream')
        except:
            return pd.DataFrame(), {}
        for table in tables:
            df = table.df
            if df.shape[1] != 4:
                continue
            for i in range(1, len(df)):
                r = df.iloc[i]
                if r[0] == "" or not is_valid_date(r[0]):
                    continue
                try:
                    rows.append([
                        r[0],
                        r[1],
                        r[2].replace('\n', ' '),
                        r[3] if 'CR' not in r[3] else '',
                        r[3].replace('CR', '') if 'CR' in r[3] else ''
                    ])
                except Exception as e:
                    continue
        col_names = ["transaction_date", "posting_date", "description", "debit", "credit"]
        df = pd.DataFrame(rows, columns=col_names)
        df["dttime"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        summary = {
            "Transactions": len(df),
            "Start Date": df["dttime"].min().strftime("%d-%m-%Y") if not df.empty else "-",
            "End Date":   df["dttime"].max().strftime("%d-%m-%Y") if not df.empty else "-",
            "Total Debit": pd.to_numeric(
                df.get("debit", pd.Series(dtype=float)).astype(str).str.replace(",", "", regex=False), errors="coerce"
            ).sum(skipna=True),
            "Total Credit": pd.to_numeric(
                df.get("credit", pd.Series(dtype=float)).astype(str).str.replace(",", "", regex=False), errors="coerce"
            ).sum(skipna=True),
        }
        return df.drop(columns=["dttime"], errors="ignore"), summary


# -------------------------------------------------------------------
# Main Streamlit logic (with tabs + forms)
# -------------------------------------------------------------------
if uploaded_files:
    st.markdown("---")
    tab_objs = st.tabs([file.name for file in uploaded_files])

    for file, tab in zip(uploaded_files, tab_objs):
        with tab:
            with st.spinner(f"Processing `{file.name}`…"):
                df, summary = parse_pdf(file, account_type)

            with st.expander(f"📋 Summary of `{file.name}`"):
                st.write(summary)

            st.subheader(f"📝 Edit `{file.name}`")
            with st.form(key=f"form_{file.name}"):
                edited = st.data_editor(
                    df,
                    use_container_width=True,
                    num_rows="dynamic",
                    key=f"editor_{file.name}"
                )
                submitted = st.form_submit_button("Save Changes")

            if submitted:
                st.success("✅ Changes Applied Successfully")
                df = edited

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download to CSV",
                data=csv_bytes,
                file_name=f"{file.name.replace('.pdf', '')}_edited.csv",
                mime="text/csv",
                key=f"{file.name}_csv",
            )
    st.markdown("---")
else:
    st.info("Upload one or more PDF statements to get started.")
