import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# CONFIGURATION
FILE_NAME = 'TRADE_HISTORY_CSV_1103885929_2025-08-01_2026-02-16_0_.csv'

# Auto-detect file path
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, FILE_NAME)

try:
    # 1. Load Data
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Sell = (+), Buy = (-)
    df['Cashflow'] = df.apply(lambda row: row['Trade Value'] if row['Buy/Sell'].strip().upper() == 'SELL' else -row['Trade Value'], axis=1)

    # 2. Stats
    daily_pnl = df.groupby('Date')['Cashflow'].sum().reset_index()
    daily_pnl['Cumulative P&L'] = daily_pnl['Cashflow'].cumsum()
    daily_pnl['Running Peak'] = daily_pnl['Cumulative P&L'].cummax()
    daily_pnl['Drawdown'] = daily_pnl['Cumulative P&L'] - daily_pnl['Running Peak']
    
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    df['Hour'] = df['Time'].apply(lambda x: x.hour)
    hourly_pnl = df.groupby('Hour')['Cashflow'].sum().reset_index()
    hourly_colors = ['#00C853' if x > 0 else '#FF5252' for x in hourly_pnl['Cashflow']]

    # 3. PLOT LAYOUT (1 Top, 2 Bottom)
    fig = plt.figure(figsize=(16, 12))
    grid = plt.GridSpec(2, 2, height_ratios=[1, 0.8], hspace=0.3, wspace=0.2)

    # Top: Equity Curve (Spans Full Width)
    ax1 = fig.add_subplot(grid[0, :])
    ax1.plot(daily_pnl['Date'], daily_pnl['Cumulative P&L'], color='#00C853', linewidth=2)
    ax1.fill_between(daily_pnl['Date'], daily_pnl['Cumulative P&L'], color='#00C853', alpha=0.1)
    ax1.set_title('Account Growth (Equity Curve)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Net Profit (₹)')
    ax1.grid(True, linestyle='--', alpha=0.3)

    # Bottom Left: Drawdown
    ax2 = fig.add_subplot(grid[1, 0])
    ax2.plot(daily_pnl['Date'], daily_pnl['Drawdown'], color='#FF5252', linewidth=1)
    ax2.fill_between(daily_pnl['Date'], daily_pnl['Drawdown'], color='#FF5252', alpha=0.1)
    ax2.set_title('Risk Profile: Drawdown from Peak', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Drawdown (₹)')
    ax2.grid(True, linestyle='--', alpha=0.3)
    plt.setp(ax2.get_xticklabels(), rotation=30)

    # Bottom Right: Hourly Edge
    ax3 = fig.add_subplot(grid[1, 1])
    sns.barplot(x='Hour', y='Cashflow', data=hourly_pnl, palette=hourly_colors, ax=ax3)
    ax3.set_title('Time-of-Day Efficiency', fontsize=12, fontweight='bold')
    ax3.axhline(0, color='black', linewidth=0.8)
    ax3.set_ylabel('Net P&L (₹)')

    # Overall Title
    fig.suptitle('FY25-26 Discretionary Trading Performance Audit', fontsize=20, fontweight='bold', y=0.95)
    
    # Save
    plt.savefig(os.path.join(script_dir, 'trading_performance_dashboard.png'), dpi=300)
    print("Dashboard Saved!")

except Exception as e:
    print(f"Error: {e}")