import streamlit as st
import pandas as pd

from BackEnd_01_Earnings import ER_table_1, EPS_table_2, get_next_earnings_report_date, earnings_outlook
from BackEnd_02_Sector_Performance import sector_1d_comparison
from BackEnd_03_Macro_Data import macro_data_analysis

st.set_page_config(
    page_title="IS 430 Stock Analytics Tool",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("📈 Stock Analytics")

ticker = st.sidebar.text_input("Enter a stock ticker (e.g. GOOGL, AAPL)", value="GOOGL").upper().strip()
run_button = st.sidebar.button("Run Analysis")


def render_dataframe(df: pd.DataFrame, **kwargs):
    """Render DataFrame with a wider layout and preserve index."""
    st.dataframe(df.style.format(precision=2), use_container_width=True, **kwargs)


def show_part_i(ticker: str):
    """Earnings analysis section."""
    st.header("Ⅰ Earnings Report 🧾")
    with st.spinner("Fetching earnings data…"):
        table_1, er_score = ER_table_1(ticker)
        table_2, eps_score = EPS_table_2(ticker)
        next_call = get_next_earnings_report_date(ticker)
        outlook = earnings_outlook(er_score, eps_score)

    st.subheader("Quarter‑over‑Quarter / Year‑over‑Year Growth")
    render_dataframe(table_1)

    st.subheader("EPS Surprise")
    render_dataframe(table_2)

    st.info(outlook)
    st.write(f"**Next earnings call:** {next_call}")


def show_part_ii(ticker: str):
    """Sector performance section."""
    st.header("Ⅱ Sector Performance 🏢")
    with st.spinner("Comparing same‑sector performance…"):
        df, status, signal, summary = sector_1d_comparison(ticker)

    render_dataframe(df)
    st.success(summary)
    st.write(f"**Status:** {status} · **Signal:** {signal:+d}")


def show_part_iii(ticker: str):
    """Macro‑economic indicators section."""
    st.header("Ⅲ Macro Data 🌐")
    with st.spinner("Retrieving sector‑specific macro indicators…"):
        out1, out2, macro_df, macro_signal = macro_data_analysis(ticker)

    if isinstance(macro_df, pd.DataFrame):
        render_dataframe(macro_df)
    else:
        st.write(macro_df)

    st.write(out1)
    st.write(out2)
    st.info(macro_signal)


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
        except Exception as e:
            st.error(f"⚠️ An error occurred while running the analysis: {e}")
else:
    st.title("IS 430 Stock Analytics Tool")
    st.markdown(
        "Enter a ticker in the sidebar and click **Run Analysis** to generate a complete report covering Earnings, Sector Performance, and Macro‑economic indicators."
    )
