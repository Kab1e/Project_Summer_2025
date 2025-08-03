import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta

from BackEnd_02_Sector_Performance import get_sector

# Part 3 of Project IS 430:

list_of_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


GENERAL_Output_columns = pd.MultiIndex.from_tuples([
    (f"Latest Data", f"(in Million Dollars)"),
    (f"Latest Data", ""),

    ("MoM", "MoM Change"),
    ("MoM", "MoM Change Pct"),

    ("YoY", "YoY Change"),
    ("YoY", "YoY Change Pct")
])

macro_data_sign = 0



''' *** Durable Goods *** '''

def durable_goods_analysis(Durable_Goods_MoM_pct, Durable_Goods_YoY_pct):
    signal = 0

    if Durable_Goods_MoM_pct > 3:
        if Durable_Goods_YoY_pct > 0:
            analysis_output = (
                "Durable Goods orders are showing strong momentum, with robust MoM growth "
                f"of {Durable_Goods_MoM_pct:.2f}% and a positive YoY change of {Durable_Goods_YoY_pct:.2f}%. "
                "This suggests sustained expansion and healthy industrial demand."
            )
            signal += 5

        else:
            analysis_output = (
                "Despite a YoY decline of {Durable_Goods_YoY_pct:.2f}%, the sharp MoM growth of "
                f"{Durable_Goods_MoM_pct:.2f}% indicates a near-term rebound in Durable Goods orders. "
                "This could signal the beginning of a recovery phase."
            )
            signal += 3

    elif Durable_Goods_MoM_pct > 0:
        if Durable_Goods_YoY_pct > 0:
            analysis_output = (
                f"Durable Goods orders rose modestly MoM (+{Durable_Goods_MoM_pct:.2f}%) "
                f"and remain up YoY (+{Durable_Goods_YoY_pct:.2f}%), indicating a stable and steady growth. "
                "Conditions remain constructive for the industrial sector."
            )
            signal += 1

        else:
            analysis_output = (
                f"MoM Durable Goods orders increased by {Durable_Goods_MoM_pct:.2f}%, "
                f"but remain down YoY (-{abs(Durable_Goods_YoY_pct):.2f}%). "
                "This suggests tentative recovery after a longer-term slowdown."
            )
            signal += 0

    elif Durable_Goods_MoM_pct < 0:
        if Durable_Goods_YoY_pct > 0:
            analysis_output = (
                f"Durable Goods orders declined MoM by {abs(Durable_Goods_MoM_pct):.2f}%, "
                f"though YoY growth remains positive at +{Durable_Goods_YoY_pct:.2f}%. "
                "This may reflect short-term volatility within an otherwise improving trend."
            )
            signal -= 1

        else:
            analysis_output = (
                f"Durable Goods orders are weakening both MoM (-{abs(Durable_Goods_MoM_pct):.2f}%) "
                f"and YoY (-{abs(Durable_Goods_YoY_pct):.2f}%). "
                "This double decline suggests broader industrial headwinds and reduced business investment."
            )
            signal -= 3

    else:
        analysis_output = (
            f"Durable Goods orders were flat MoM ({Durable_Goods_MoM_pct:.2f}%), "
            f"with a YoY change of {Durable_Goods_YoY_pct:.2f}%. "
            "The sector appears to be stabilizing, but further data is needed to assess direction."
        )
        signal -= 5

    return analysis_output, signal

def Durable_Goods():
    HISTORICAL_Durable_Goods_New_Orders = pd.read_excel("https://www.census.gov/manufacturing/m3/prel/historical_data/histshts/naics/naicsnop.xlsx")

    columns = ["Location", "Year"] + list_of_months
    HISTORICAL_Durable_Goods_New_Orders.columns = columns[:len(HISTORICAL_Durable_Goods_New_Orders.columns)]

    Durable_Goods_this_year = HISTORICAL_Durable_Goods_New_Orders.iloc[-1, 1]
    HISTORICAL_Durable_Goods_New_Orders = HISTORICAL_Durable_Goods_New_Orders.drop(columns=["Location"]).groupby("Year").agg("sum").reset_index(drop=False)[-2:]
    Durable_Goods_this_month = (HISTORICAL_Durable_Goods_New_Orders.drop(columns=["Year"]) != 0).sum().sum() - 12

    if Durable_Goods_this_month != 1 and Durable_Goods_this_month != 12:
        latest_month = list_of_months[Durable_Goods_this_month - 1]
        previous_month = list_of_months[Durable_Goods_this_month - 2]
        next_month = list_of_months[Durable_Goods_this_month]

    elif Durable_Goods_this_month == 12:
        latest_month = list_of_months[Durable_Goods_this_month - 1]
        previous_month = list_of_months[Durable_Goods_this_month - 2]
        next_month = list_of_months[0]

    else: 
        latest_month = list_of_months[Durable_Goods_this_month - 1]
        previous_month = list_of_months[11]
        next_month = list_of_months[Durable_Goods_this_month]

    if Durable_Goods_this_month != 1:
        Latest_Month_data = HISTORICAL_Durable_Goods_New_Orders.iloc[1, Durable_Goods_this_month]
        Previous_Month_data = HISTORICAL_Durable_Goods_New_Orders.iloc[1, Durable_Goods_this_month - 1]
        Last_Year_Same_Month_data = HISTORICAL_Durable_Goods_New_Orders.iloc[0, Durable_Goods_this_month]

    else:
        Latest_Month_data = HISTORICAL_Durable_Goods_New_Orders.iloc[1, Durable_Goods_this_month]
        Previous_Month_data = HISTORICAL_Durable_Goods_New_Orders.iloc[0, 11]
        Last_Year_Same_Month_data = HISTORICAL_Durable_Goods_New_Orders.iloc[0, Durable_Goods_this_month]

    Durable_Goods_MoM_Growth = Latest_Month_data - Previous_Month_data
    Durable_Goods_YoY_Growth = Latest_Month_data - Last_Year_Same_Month_data
    Durable_Goods_MoM_pct = Durable_Goods_MoM_Growth / Previous_Month_data * 100
    Durable_Goods_YoY_pct = Durable_Goods_YoY_Growth / Last_Year_Same_Month_data * 100

    Durable_Goods_data = [[
    f"{Latest_Month_data:,}",
    f"({latest_month}, {Durable_Goods_this_year})",

    f"{Durable_Goods_MoM_Growth:+,}",
    f"{Durable_Goods_MoM_pct:+.2f}%",

    f"{Durable_Goods_YoY_Growth:,}",
    f"{Durable_Goods_YoY_pct:+.2f}%"
    ]]

    Durable_Goods_Analysis_Output, Durable_Goods_signal = durable_goods_analysis(Durable_Goods_MoM_pct, Durable_Goods_YoY_pct)

    return Durable_Goods_data, Durable_Goods_Analysis_Output, Durable_Goods_signal


''' *** INDPRO *** '''
# LYSM - Last Year Same Month
# FRED API KEY: ef418abc7729096c77970a459e9d62dd

def INDPRO_analysis(INDPRO_MoM_pct, INDPRO_YoY_pct):
    signal = 0
    if INDPRO_MoM_pct > 3:
        if INDPRO_YoY_pct > 0:
            INDPRO_Analysis_Output = (
                "Industrial Production is expanding strongly, with a sharp MoM increase of "
                f"{INDPRO_MoM_pct:.2f}% and a YoY rise of {INDPRO_YoY_pct:.2f}%. "
                "This reflects broad-based strength in manufacturing, mining, and utilities."
            )
            signal += 5

        else:
            INDPRO_Analysis_Output = (
                f"Although YoY Industrial Production remains down ({INDPRO_YoY_pct:.2f}%), "
                f"the strong MoM growth of {INDPRO_MoM_pct:.2f}% suggests a turning point for the industrial economy."
            )
            signal += 3

    elif INDPRO_MoM_pct > 0:
        if INDPRO_YoY_pct > 0:
            INDPRO_Analysis_Output = (
                f"Industrial Production rose moderately MoM (+{INDPRO_MoM_pct:.2f}%) "
                f"and remains up YoY (+{INDPRO_YoY_pct:.2f}%), indicating stable and healthy output across sectors."
            )
            signal += 1

        else:
            INDPRO_Analysis_Output = (
                f"Despite a YoY contraction of {abs(INDPRO_YoY_pct):.2f}%, "
                f"MoM production rose by {INDPRO_MoM_pct:.2f}%, possibly pointing to early signs of stabilization."
            )
            signal += 0

    elif INDPRO_MoM_pct < 0:
        if INDPRO_YoY_pct > 0:
            INDPRO_Analysis_Output = (
                f"MoM Industrial Production declined by {abs(INDPRO_MoM_pct):.2f}%, "
                f"though YoY output remains positive at +{INDPRO_YoY_pct:.2f}%. "
                "This may reflect temporary volatility in output rather than a long-term trend."
            )
            signal -= 1

        else:
            INDPRO_Analysis_Output = (
                f"Industrial Production is facing dual pressure, falling both MoM (-{abs(INDPRO_MoM_pct):.2f}%) "
                f"and YoY (-{abs(INDPRO_YoY_pct):.2f}%). This points to broad industrial weakness and softer demand."
            )
            signal -= 3

    else:
        INDPRO_Analysis_Output = (
            f"Industrial Production was flat MoM ({INDPRO_MoM_pct:.2f}%), "
            f"with a YoY change of {INDPRO_YoY_pct:.2f}%. "
            "This indicates a neutral environment, with neither growth nor contraction clearly dominating."
        )
        signal -= 5

    return INDPRO_Analysis_Output, signal

def INDPRO():
    fred = Fred(api_key="ef418abc7729096c77970a459e9d62dd")
    ip_data = fred.get_series("INDPRO")
    ip_df = ip_data.to_frame(name="Industrial Production")
    ip_df.index.name = "Date"

    LYSM_INDPRO_data = ip_df.iloc[-13, 0].item()
    Previous_INDPRO_data = ip_df.iloc[-2, 0].item()
    Latest_INDPRO_data = ip_df.iloc[-1, 0].item()

    LYSM_INDPRO_date = fred.get_series_vintage_dates("INDPRO")[-13].strftime("%B %d, %Y")
    Previous_INDPRO_date = fred.get_series_vintage_dates("INDPRO")[-2].strftime("%B %d, %Y")
    Latest_INDPRO_date = fred.get_series_vintage_dates("INDPRO")[-1].strftime("%B %d, %Y")

    INDPRO_MoM_Growth = Latest_INDPRO_data - Previous_INDPRO_data
    INDPRO_YoY_Growth = Latest_INDPRO_data - LYSM_INDPRO_data
    INDPRO_MoM_pct = INDPRO_MoM_Growth / Previous_INDPRO_data * 100
    INDPRO_YoY_pct = INDPRO_YoY_Growth / LYSM_INDPRO_data * 100

    INDPRO_data = [[
    f"{Latest_INDPRO_data:.2f}", f"{Latest_INDPRO_date}",
    f"{INDPRO_MoM_Growth:+.2f}", f"{INDPRO_MoM_pct:+.2f}%",
    f"{INDPRO_YoY_Growth:+.2f}", f"{INDPRO_YoY_pct:+.2f}%"
    ]]

    INDPRO_Analysis_Output, INDPRO_signal = INDPRO_analysis(INDPRO_MoM_pct, INDPRO_YoY_pct)

    return INDPRO_data, INDPRO_Analysis_Output, INDPRO_signal

# Industrials Output

def Industrial_Sector_Company():
    global macro_data_sign

    GENERAL_output_data = []
    Durable_Goods_data, Durable_Goods_Analysis_Output, Durable_Goods_signal = Durable_Goods()
    macro_data_sign += Durable_Goods_signal
    INDPRO_data, INDPRO_Analysis_Output, INDPRO_signal = INDPRO()
    macro_data_sign += INDPRO_signal

    GENERAL_Output_index = ["Durable Goods", "Industrial Production (INDPRO)"]

    GENERAL_output_data += Durable_Goods_data
    GENERAL_output_data += INDPRO_data

    GENERAL_OUTPUT_dataframe = pd.DataFrame(GENERAL_output_data, columns=GENERAL_Output_columns, index=GENERAL_Output_index)

    return Durable_Goods_Analysis_Output, INDPRO_Analysis_Output, GENERAL_OUTPUT_dataframe, macro_data_sign




# Function for Output

def macro_data_analysis(ticker):
    sector = get_sector(ticker)
    
    signal = None #Only For When I Have Not Done All
    if sector == "Materials": #1
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"
    
    elif sector == "Communication Services": #2
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"
    
    elif sector == "Consumer Discretionary": #3
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"
    
    elif sector == "Consumer Staples": #4
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"
    
    elif sector == "Energy": #5
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"
    
    elif sector == "Financials": #6
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"

    elif sector == "Health Care": #7
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"


    elif sector == "Industrials": #8
        Output_Line1, Output_Line2, df, signal = Industrial_Sector_Company()
        macro_data_analysis_output1 = Output_Line1
        macro_data_analysis_output2 = Output_Line2
        macro_data_analysis_output_df = df
    
    elif sector == "Real Estate": #9
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"

    elif sector == "Information Technology": #10
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"

    elif sector == "Utilities": #11
        macro_data_analysis_output1 = f"Not Done Yet"
        macro_data_analysis_output2 = f"Not Done Yet"
        macro_data_analysis_output_df = f"Not Done Yet"


    Default = f"Market Expectation: "
    if signal == 10 or signal == 8:
        signal_output = (Default + f"Very Good. \n" + "\n" + f"Industrial macro indicators are firing on all cylinders. Robust order books and rising capacity utilisation point to continued revenue tailwinds and margin support across the sector.")
    elif signal in [6, 5, 4]:
        signal_output = (Default + f"Good. \n" + "\n" + f"Key macro metrics show healthy – though moderating – growth. The backdrop remains constructive, but monitor upcoming releases for signs of cooling demand.")
    elif signal in [3, 2, 1, 0, -1, -2, -3]:
        signal_output = (Default + f"Give It Some Time. \n" + "\n" + f"Signals are mixed. A stabilisation phase could be forming, but you’ll want confirmation from next month’s Durable-Goods and INDPRO prints.")
    elif signal in [-4, -5, -6]:
        signal_output = (Default + f"Bad. \n" + "\n" + f"Macro momentum has soured, with contracting orders and production flagging near-term headwinds. A more defensive stance is prudent.")
    elif signal == -8 or signal == -10:
        signal_output = (Default + f"Very Bad. \n" + "\n" + f"Leading indicators flash recessionary warnings. Expect broad demand weakness and potential earnings downgrades sector-wide.")
    else:
        signal_output = (f"Something Went WRONG!!!")

    return macro_data_analysis_output1, macro_data_analysis_output2, macro_data_analysis_output_df, signal_output