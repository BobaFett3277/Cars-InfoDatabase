"""
generate_screenshots.py
Run this script to regenerate all chart screenshots for the README.

Usage:
    pip install pandas matplotlib
    python generate_screenshots.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ── Setup ─────────────────────────────────────────────────────────────────
os.makedirs("screenshots", exist_ok=True)
df = pd.read_csv("cars.csv")
df['decade'] = (df['model_year'] // 10) * 10
df['era'] = df['model_year'].apply(
    lambda y: '2000s' if y < 2010 else ('2010s' if y < 2020 else '2020s')
)

# Dark theme colors
BG     = "#0d1117"
PANEL  = "#161b22"
BORDER = "#30363d"
FG     = "#e6edf3"
RED    = "#f85149"
BLUE   = "#58a6ff"
GREEN  = "#3fb950"
ORANGE = "#d29922"
PURPLE = "#bc8cff"

def base_fig(w=11, h=5):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG)
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.tick_params(colors=FG, labelsize=10)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.grid(axis='y', color=BORDER, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    return fig, ax

def save(fig, name):
    path = f"screenshots/{name}.png"
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f"  ✓ {path}")


# ── Chart 1: Average Horsepower by Decade ────────────────────────────────
fig, ax = base_fig(9, 5)
gas = df[df['fuel_type'] == 'Gasoline'].groupby('decade')['horsepower'].mean().reset_index()
bar_colors = [RED, BLUE, GREEN, ORANGE]
bars = ax.bar(gas['decade'].astype(str), gas['horsepower'],
              color=bar_colors[:len(gas)], width=0.55, zorder=3)
for b, v in zip(bars, gas['horsepower']):
    ax.text(b.get_x() + b.get_width() / 2, v + 4, f"{v:.0f} hp",
            ha='center', color=FG, fontweight='bold', fontsize=12)
ax.set_title("Average Horsepower by Decade  (Gasoline Cars)", color=FG, fontsize=14, pad=14)
ax.set_xlabel("Decade", fontsize=11)
ax.set_ylabel("Avg Horsepower", fontsize=11)
ax.set_ylim(0, gas['horsepower'].max() * 1.22)
fig.tight_layout()
save(fig, "01_hp_by_decade")


# ── Chart 2: Horsepower per $1,000 by Brand ───────────────────────────────
fig, ax = base_fig(11, 6)
mk = df.groupby('make').agg(
    hp=('horsepower', 'mean'),
    price=('msrp_usd', 'mean'),
    n=('id', 'count')
).reset_index()
mk['hpk'] = mk['hp'] / mk['price'] * 1000
mk = mk.nlargest(12, 'hpk').sort_values('hpk')
colors = [RED if i % 2 == 0 else BLUE for i in range(len(mk))]
bars = ax.barh(mk['make'], mk['hpk'], color=colors, height=0.6, zorder=3)
for b, v in zip(bars, mk['hpk']):
    ax.text(v + 0.03, b.get_y() + b.get_height() / 2, f"{v:.2f}",
            va='center', color=FG, fontsize=10)
ax.set_title("Horsepower per $1,000 MSRP — Top 12 Brands", color=FG, fontsize=14, pad=14)
ax.set_xlabel("HP per $1,000", fontsize=11)
fig.tight_layout()
save(fig, "02_hp_per_dollar")


# ── Chart 3: Fuel Type Market Share by Year ───────────────────────────────
fig, ax = base_fig(12, 5)
yr = df.groupby(['model_year', 'fuel_type']).size().unstack(fill_value=0)
yr_pct = yr.div(yr.sum(axis=1), axis=0) * 100
for col, color, lbl in [
    ('Electric', BLUE,  'Electric'),
    ('Hybrid',   GREEN, 'Hybrid'),
    ('Gasoline', RED,   'Gasoline'),
]:
    if col in yr_pct:
        ax.fill_between(yr_pct.index, yr_pct[col], alpha=0.25, color=color)
        ax.plot(yr_pct.index, yr_pct[col], color=color, lw=2.5, label=lbl)
ax.set_title("Fuel Type Market Share by Year", color=FG, fontsize=14, pad=14)
ax.set_xlabel("Model Year", fontsize=11)
ax.set_ylabel("% of Market", fontsize=11)
ax.set_xlim(2000, 2024)
ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=FG, fontsize=11)
fig.tight_layout()
save(fig, "03_ev_wave")


# ── Chart 4: Body Style Market Share Over Time ────────────────────────────
fig, ax = base_fig(12, 5)
by = df.groupby(['model_year', 'body_style']).size().unstack(fill_value=0)
by_pct = by.div(by.sum(axis=1), axis=0) * 100
style_colors = {
    'SUV': BLUE, 'Sedan': GREEN, 'Truck': RED,
    'Hatchback': ORANGE, 'Coupe': PURPLE
}
for style, color in style_colors.items():
    if style in by_pct:
        ax.plot(by_pct.index, by_pct[style], color=color, lw=2.5, label=style)
ax.set_title("Body Style Market Share Over Time", color=FG, fontsize=14, pad=14)
ax.set_xlabel("Model Year", fontsize=11)
ax.set_ylabel("% of New Vehicles", fontsize=11)
ax.set_xlim(2000, 2024)
ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=FG, fontsize=11)
fig.tight_layout()
save(fig, "04_suv_takeover")


# ── Chart 5: Average MSRP Heatmap by Segment & Era ───────────────────────
fig, ax = plt.subplots(figsize=(13, 6), facecolor=BG)
ax.set_facecolor(PANEL)
top_segs = df.groupby('segment').size().nlargest(9).index
pivot = (
    df[df['segment'].isin(top_segs)]
    .groupby(['segment', 'era'])['msrp_usd']
    .mean()
    .unstack()[['2000s', '2010s', '2020s']]
)
im = ax.imshow(pivot.values / 1000, cmap='YlOrRd', aspect='auto', vmin=15, vmax=95)
ax.set_xticks(range(3))
ax.set_xticklabels(['2000s', '2010s', '2020s'], color=FG, fontsize=12)
ax.set_yticks(range(len(pivot)))
ax.set_yticklabels(pivot.index, color=FG, fontsize=10)
for i in range(len(pivot)):
    for j in range(3):
        v = pivot.values[i, j]
        ax.text(j, i, f"${v/1000:.0f}k", ha='center', va='center',
                fontsize=10, fontweight='bold', color='black')
cb = plt.colorbar(im, ax=ax, pad=0.02)
cb.ax.tick_params(labelcolor=FG)
cb.set_label('Avg MSRP ($k)', color=FG)
ax.set_title("Average MSRP by Segment & Era", color=FG, fontsize=14, pad=14)
fig.tight_layout()
save(fig, "05_price_heatmap")


# ── Chart 6: Reliability & Safety by Country of Origin ───────────────────
fig, ax = base_fig(10, 5)
rel = df.groupby('country_of_origin').agg(
    rel=('reliability_score', 'mean'),
    saf=('safety_rating', 'mean'),
    n=('id', 'count')
).reset_index()
rel = rel[rel['n'] > 100].sort_values('rel', ascending=False)
x = np.arange(len(rel))
w = 0.35
ax.bar(x - w/2, rel['rel'],     width=w, color=BLUE,  label='Reliability Score (out of 10)', zorder=3)
ax.bar(x + w/2, rel['saf'] * 2, width=w, color=GREEN, label='Safety Rating (×2 to match scale)', zorder=3)
ax.set_xticks(x)
ax.set_xticklabels(rel['country_of_origin'], color=FG, rotation=20, ha='right', fontsize=10)
ax.set_title("Reliability & Safety by Country of Origin", color=FG, fontsize=14, pad=14)
ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=FG, fontsize=10)
fig.tight_layout()
save(fig, "06_reliability_by_origin")


print("\nDone! All screenshots saved to screenshots/")