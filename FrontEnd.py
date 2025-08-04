import streamlit as st
import pandas as pd

from BackEnd_01_Earnings import ER_table_1, EPS_table_2, get_next_earnings_report_date, earnings_outlook
from BackEnd_02_Sector_Performance import sector_1d_comparison
from BackEnd_03_Macro_Data import macro_data_analysis
from BackEnd_04_Playbook import get_trade_plan

st.set_page_config(
    page_title="Bob's Stock Analytics Tool (for IS 430)",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("📈 Stock Analytics")

ticker = st.sidebar.text_input("Enter a stock ticker (e.g. GOOGL, AAPL)", value="GOOGL").upper().strip()
run_button = st.sidebar.button("Run Analysis")


def render_dataframe(df: pd.DataFrame, **kwargs):
    st.dataframe(df.style.format(precision=2), use_container_width=True, **kwargs)


def show_part_i(ticker: str):
    st.header("Ⅰ Earnings Report 🧾")
    with st.spinner("Fetching earnings data…"):
        table_1, er_score = ER_table_1(ticker)
        table_2, eps_score = EPS_table_2(ticker)
        next_call = get_next_earnings_report_date(ticker)
        outlook, _ = earnings_outlook(er_score, eps_score)

    st.subheader("Quarter‑over‑Quarter / Year‑over‑Year Growth")
    render_dataframe(table_1)

    st.subheader("EPS Surprise")
    render_dataframe(table_2)

    st.info(outlook)
    st.write(f"**Next earnings call:** {next_call}")


def show_part_ii(ticker: str):
    st.header("Ⅱ Sector Performance 🏢")
    with st.spinner("Comparing same‑sector performance…"):
        df, status, signal, summary = sector_1d_comparison(ticker)

    render_dataframe(df)
    st.success(summary)


def show_part_iii(ticker: str):
    st.header("Ⅲ Macro Data 🌐")
    with st.spinner("Retrieving sector‑specific macro indicators…"):
        out1, out2, macro_df, macro_signal, _ = macro_data_analysis(ticker)

    if isinstance(macro_df, pd.DataFrame):
        render_dataframe(macro_df)
    else:
        st.write(macro_df)

    st.write(out1)
    st.write(out2)
    st.info(macro_signal)

def show_part_iv(ticker: str):
    st.header("Ⅳ Trade Strategy 🚀")
    with st.spinner("Retrieving sector‑specific macro indicators…"):
        scenario, plan = get_trade_plan(ticker)
    
    st.write(f"**{scenario}**:")
    st.info(f"{plan}")

    
if run_button:
    if not ticker:
        st.warning("Please enter a valid ticker symbol.")
    else:
        try:
            show_part_i(ticker)
            st.markdown("---")
            show_part_ii(ticker)
            st.markdown("---")
            show_part_iii(ticker)
            st.markdown("---")
            show_part_iv(ticker)
        except Exception as e:
            st.error(f"⚠️ An error occurred while running the analysis: {e}")
else:
    st.title("Bob's Stock Analytics Tool (for IS 430)")
    st.markdown(
        "Enter a ticker in the sidebar and click **Run Analysis** to generate a complete report covering Earnings, Sector Performance, and Macro‑economic indicators."
    )
