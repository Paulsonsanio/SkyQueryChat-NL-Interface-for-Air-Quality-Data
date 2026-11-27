import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path

out_dir = Path('report_assets')
out_dir.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# Figure 1: 5-Stage Agentic Pipeline
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis('off')

stages = [
    ('1. Query Planning', 'Groq Cloud LLM\n(openai/gpt-oss-120b)\n+ RulePlanner fallback', '#0F766E'),
    ('2. Schema & Bounds', 'Schema Sanitizer\nIndian Gazetteer\n(28 States, 248 Cities)', '#1E293B'),
    ('3. Vector Engine', '3D NumPy Array\nHaversine 25km Filter\nCloud Mask (<30%)', '#0284C7'),
    ('4. Math Verifier', 'Independent Verifier\nPure-Python math\n1e-6 Tolerance Check', '#B45309'),
    ('5. Presentation', 'Altair Charts\nMetric Cards & Audit\nDeterministic Templates', '#059669')
]

for i, (title, desc, col) in enumerate(stages):
    x = 0.3 + i * 1.95
    rect = patches.FancyBboxPatch((x, 1.0), 1.65, 2.7, boxstyle='round,pad=0.08,rounding_size=0.15',
                                  facecolor='#FFFFFF', edgecolor=col, linewidth=2, zorder=2)
    ax.add_patch(rect)
    header_rect = patches.FancyBboxPatch((x, 3.1), 1.65, 0.6, boxstyle='round,pad=0.08,rounding_size=0.1',
                                         facecolor=col, edgecolor=col, linewidth=1, zorder=3)
    ax.add_patch(header_rect)
    ax.text(x + 0.825, 3.4, title, ha='center', va='center', color='#FFFFFF', fontsize=8.5, fontweight='bold', zorder=4)
    ax.text(x + 0.825, 2.05, desc, ha='center', va='center', color='#1E293B', fontsize=7.5, multialignment='center', zorder=4)
    
    if i < len(stages) - 1:
        ax.annotate('', xy=(x + 1.95, 2.35), xytext=(x + 1.65, 2.35),
                    arrowprops=dict(arrowstyle='->', lw=2, color='#64748B'), zorder=5)

ax.text(5, 4.4, 'SkyQueryChat: End-to-End 5-Stage Agentic Architecture', ha='center', va='center',
        fontsize=12, fontweight='bold', color='#0F172A')
plt.tight_layout()
fig.savefig(out_dir / 'fig1_architecture.png', bbox_inches='tight')
plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 2: India Grid & City Plumes Map
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 6.5), dpi=300)
lat = np.linspace(6, 38, 129)
lon = np.linspace(68, 98, 121)
X, Y = np.meshgrid(lon, lat)
Z = 1.0 + 15.0 * np.exp(-((Y - 28.6)**2 + (X - 77.2)**2) / 8.0)
Z += 12.0 * np.exp(-((Y - 31.1)**2 + (X - 75.3)**2) / 7.0)
Z += 8.0 * np.exp(-((Y - 19.1)**2 + (X - 72.9)**2) / 6.0)
Z += 9.0 * np.exp(-((Y - 22.6)**2 + (X - 88.4)**2) / 6.0)
Z += 5.0 * np.exp(-((Y - 13.0)**2 + (X - 77.6)**2) / 5.0)

cs = ax.contourf(X, Y, Z, levels=30, cmap='YlOrRd', alpha=0.85)
cbar = plt.colorbar(cs, ax=ax, shrink=0.8)
cbar.set_label('Tropospheric NO2 Column (x10^15 molecules/cm2)', fontsize=9, fontweight='bold')

cities = {
    'Delhi': (77.2090, 28.6139),
    'Punjab (Chandigarh)': (76.7794, 30.7333),
    'Mumbai': (72.8777, 19.0760),
    'Kolkata': (88.3639, 22.5726),
    'Bengaluru': (77.5946, 12.9716),
    'Chennai': (80.2707, 13.0827),
    'Hyderabad': (78.4867, 17.3850),
    'Ahmedabad': (72.5714, 23.0225),
    'Lucknow': (80.9462, 26.8467)
}
for name, (c_lon, c_lat) in cities.items():
    ax.scatter(c_lon, c_lat, color='#0F172A', s=35, zorder=5, edgecolor='#FFFFFF', linewidth=1)
    ax.text(c_lon + 0.5, c_lat, name, fontsize=8, fontweight='bold', color='#0F172A', zorder=6)

ax.set_title('Satellite Atmospheric NO2 Coverage Domain (India 6N-38N, 68E-98E)', fontsize=11, fontweight='bold')
ax.set_xlabel('Longitude (deg E)', fontsize=9)
ax.set_ylabel('Latitude (deg N)', fontsize=9)
ax.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
fig.savefig(out_dir / 'fig2_india_grid.png', bbox_inches='tight')
plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 3: Traditional vs SkyQueryChat Workflow
# -----------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
ax1.set_title('Traditional Earth Observation Workflow', fontsize=11, fontweight='bold', color='#DC2626')
ax1.axis('off')
trad_steps = [
    '1. Download massive NetCDF4/HDF5 files (10s of GBs)',
    '2. Write custom GIS/Python scripts (xarray, GDAL)',
    '3. Understand QA flags, cloud-fraction masks, SZA',
    '4. Compute spatial subsetting & area-weighted averages',
    '5. Produce static plots; high technical barrier'
]
for idx, s in enumerate(trad_steps):
    rect = patches.FancyBboxPatch((0.05, 0.8 - idx*0.18), 0.9, 0.12, boxstyle='round,pad=0.04',
                                  facecolor='#FEE2E2', edgecolor='#EF4444', lw=1.5)
    ax1.add_patch(rect)
    ax1.text(0.5, 0.86 - idx*0.18, s, ha='center', va='center', fontsize=8, color='#991B1B', fontweight='semibold')

ax2.set_title('SkyQueryChat Conversational AI Workflow', fontsize=11, fontweight='bold', color='#059669')
ax2.axis('off')
sq_steps = [
    '1. User asks natural query (e.g. "air quality in Punjab")',
    '2. High-speed Groq LLM brain extracts JSON query plan',
    '3. Vectorized NumPy engine slices 3D satellite grid',
    '4. Pure-Python verifier validates math (1e-6 tolerance)',
    '5. Interactive Altair chart & verified summary in < 1 sec'
]
for idx, s in enumerate(sq_steps):
    rect = patches.FancyBboxPatch((0.05, 0.8 - idx*0.18), 0.9, 0.12, boxstyle='round,pad=0.04',
                                  facecolor='#ECFDF5', edgecolor='#10B981', lw=1.5)
    ax2.add_patch(rect)
    ax2.text(0.5, 0.86 - idx*0.18, s, ha='center', va='center', fontsize=8, color='#065F46', fontweight='semibold')

plt.tight_layout()
fig.savefig(out_dir / 'fig3_workflow_comparison.png', bbox_inches='tight')
plt.close(fig)

print('All 3 diagram figures generated successfully in report_assets/')
