"""
=============================================================================
   AUTOMATED TRADING AUDIT
=============================================================================
   
   INSTRUCTIONS:
   1. Place your Dhan CSV file in this folder (rename it 'trade_ledger.csv').
   2. Run this script.
   3. Open 'audit_results/' to see your Report and Charts.
=============================================================================
"""

import os
import sys
import datetime

# --- 1. AUTO-DEPENDENCY CHECK ---
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
except ImportError as e:
    print(f"\n[!] CRITICAL ERROR: Missing library '{e.name}'")
    print("    Please run: pip install pandas matplotlib numpy")
    sys.exit(1)

# --- CONFIGURATION ---
TARGET_FILENAME = 'trade_ledger.csv'
OUTPUT_FOLDER = 'audit_results'

def setup_environment():
    if not os.path.exists(OUTPUT_FOLDER):
        try:
            os.makedirs(OUTPUT_FOLDER)
            print(f"[+] Created output directory: ./{OUTPUT_FOLDER}")
        except Exception:
            pass

def find_and_load_data():
    paths = [
        TARGET_FILENAME, 
        os.path.join('data', TARGET_FILENAME),
        os.path.join('raw_data', TARGET_FILENAME)
    ]
    
    for path in paths:
        if os.path.exists(path):
            print(f"[+] Found ledger at: {path}")
            return pd.read_csv(path)
    
    print(f"\n[!] ERROR: Could not find '{TARGET_FILENAME}'")
    print("    Please rename your Dhan file to 'trade_ledger.csv' and place it here.")
    sys.exit(1)

def run_audit(df):
    print("[*] Processing trade data...")
    
    # 1. METADATA EXTRACTION
    total_executions = len(df)
    segments = "Equity" # Default
    if 'Segment' in df.columns:
        unique_segments = df['Segment'].dropna().unique()
        segments = ", ".join(sorted(unique_segments))

    # 2. CLEAN UP
    if 'Status' in df.columns: df = df[df['Status'] == 'Traded'].copy()
    
    # 3. DATE PARSING
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Datetime']).sort_values('Datetime')

    # 4. FIFO MATCHER (Calculates Exact Realized PnL)
    open_positions = {} 
    closed_trades = []

    print("[*] Matching buy/sell orders (FIFO)...")
    for _, row in df.iterrows():
        name = row['Name']
        qty = row['Quantity/Lot']
        price = row['Trade Price']
        side = row['Buy/Sell']
        exit_time = row['Datetime']

        if name not in open_positions: open_positions[name] = []
        
        remaining = qty
        while remaining > 0 and open_positions[name]:
            if open_positions[name][0]['side'] != side:
                match_qty = min(remaining, open_positions[name][0]['qty'])
                entry_price = open_positions[name][0]['price']
                
                # Calculate PnL
                if side == 'SELL': # Closing a Long
                    pnl = (price - entry_price) * match_qty
                else: # Closing a Short
                    pnl = (entry_price - price) * match_qty
                
                closed_trades.append({
                    'Date': exit_time.date(),
                    'PnL': pnl
                })
                
                remaining -= match_qty
                open_positions[name][0]['qty'] -= match_qty
                if open_positions[name][0]['qty'] == 0: open_positions[name].pop(0)
            else:
                break 

        if remaining > 0:
            open_positions[name].append({'side': side, 'qty': remaining, 'price': price})

    if not closed_trades: return None

    # 5. AGGREGATE DATA
    pnl_df = pd.DataFrame(closed_trades)
    pnl_df['Date'] = pd.to_datetime(pnl_df['Date'])
    
    # Daily Data
    daily = pnl_df.groupby('Date')['PnL'].sum().reset_index()
    daily = daily.sort_values('Date')
    daily['Cumulative'] = daily['PnL'].cumsum()
    daily['Peak'] = daily['Cumulative'].cummax()
    daily['Drawdown'] = daily['Cumulative'] - daily['Peak']
    
    # --- METRICS CALCULATION (Exact User Formula) ---
    total_pnl = daily['PnL'].sum()
    max_dd = daily['Drawdown'].min()
    
    # Win Rate
    win_days = daily[daily['PnL'] > 0]
    loss_days = daily[daily['PnL'] <= 0]
    win_rate = (len(win_days) / len(daily)) * 100
    
    # Profit Factor
    gross_win = pnl_df[pnl_df['PnL'] > 0]['PnL'].sum()
    gross_loss = abs(pnl_df[pnl_df['PnL'] < 0]['PnL'].sum())
    profit_factor = gross_win / gross_loss if gross_loss != 0 else 0
    
    # Averages
    avg_daily_win = win_days['PnL'].mean() if not win_days.empty else 0
    avg_daily_loss = abs(loss_days['PnL'].mean()) if not loss_days.empty else 0
    
    # Risk Reward Ratio (1 : X)
    rr_ratio = avg_daily_win / avg_daily_loss if avg_daily_loss != 0 else 0

    metrics = {
        "Total Net Profit": total_pnl,
        "Max Drawdown": max_dd,
        "Profit Factor": profit_factor,
        "Win Rate": win_rate,
        "Avg Daily Win": avg_daily_win,
        "Avg Daily Loss": avg_daily_loss,
        "RR Ratio": rr_ratio,
        "Total Executions": total_executions,
        "Segments": segments,
        "Source File": TARGET_FILENAME
    }
    
    return daily, metrics

def generate_outputs(daily, metrics):
    print(f"[*] Generating visual report in '{OUTPUT_FOLDER}/'...")
    plt.style.use('ggplot') 

    # --- CHART 1: EQUITY CURVE ---
    plt.figure(figsize=(10, 5))
    plt.plot(daily['Date'], daily['Cumulative'], color='#107c10', linewidth=2)
    plt.fill_between(daily['Date'], daily['Cumulative'], 0, color='#107c10', alpha=0.1)
    plt.title(f"Equity Curve (Net: INR {metrics['Total Net Profit']:,.0f})")
    plt.ylabel("INR")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, '1_equity_curve.png'), dpi=150)
    plt.close()

    # --- CHART 2: DRAWDOWN ---
    plt.figure(figsize=(10, 3))
    plt.plot(daily['Date'], daily['Drawdown'], color='#d13438', linewidth=1)
    plt.fill_between(daily['Date'], daily['Drawdown'], 0, color='#d13438', alpha=0.2)
    plt.title(f"Risk Analysis (Max Drawdown: INR {metrics['Max Drawdown']:,.0f})")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, '2_drawdown.png'), dpi=150)
    plt.close()

    # --- TEXT REPORT (USER SPECIFIED FORMAT) ---
    report_path = os.path.join(OUTPUT_FOLDER, 'performance_summary.txt')
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("==================================================================\n")
            f.write(" FY25-26 TRADING PERFORMANCE AUDIT REPORT\n")
            f.write("==================================================================\n")
            f.write(f"Audit Date:       {current_time}\n")
            f.write(f"Data Source:      {metrics['Source File']}\n")
            f.write(f"Total Executions: {metrics['Total Executions']}\n")
            f.write(f"Segments:         {metrics['Segments']}\n\n")
            
            f.write("------------------------------------------------------------------\n")
            f.write(" KEY PERFORMANCE METRICS\n")
            f.write("------------------------------------------------------------------\n")
            f.write(f"Net Profit (Realized):  INR {metrics['Total Net Profit']:,.2f}\n")
            f.write(f"Profit Factor:          {metrics['Profit Factor']:.2f}\n")
            f.write(f"Daily Win Rate:         {metrics['Win Rate']:.1f}%\n")
            f.write(f"Risk/Reward Ratio:      1 : {metrics['RR Ratio']:.2f}\n")
            f.write(f"Max Drawdown:           INR {metrics['Max Drawdown']:,.0f}\n\n")
            
            f.write("------------------------------------------------------------------\n")
            f.write(" AVERAGE TRADE STATISTICS\n")
            f.write("------------------------------------------------------------------\n")
            f.write(f"Avg Daily Win:          INR {metrics['Avg Daily Win']:,.2f}\n")
            f.write(f"Avg Daily Loss:         INR {metrics['Avg Daily Loss']:,.2f}\n\n")
            
            f.write("==================================================================\n")
            f.write("*Generated via Python Audit Script using Pandas Analysis*\n")
            f.write("==================================================================\n")

        print(f"[+] Report saved: {report_path}")
    except Exception as e:
        print(f"[!] Error saving report: {e}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    setup_environment()
    try:
        df = find_and_load_data()
        result = run_audit(df)
        if result:
            generate_outputs(*result)
            print("\n[SUCCESS] Audit Complete! Check 'audit_results' folder.")
        else:
            print("\n[!] No valid trades found.")
    except Exception as e:
        print(f"\n[!] Error: {e}")
