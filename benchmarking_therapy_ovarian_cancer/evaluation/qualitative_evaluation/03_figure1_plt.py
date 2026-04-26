import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Plot Likert rating distributions for each system and evaluation dimension.
df = pd.read_excel('likert_distributions.xlsx', sheet_name='pivot_percent')

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability']
dim_labels = ['Correctness', 'Completeness', 'Comprehensibility', 'Applicability']

systems = ['GraphRAG', 'RAG', 'LLM', 'Referenz']
sys_labels = ['GraphRAG', 'RAG', 'LLM', 'Gold Standard']

colors = {
    'poor': '#c9ada7',
    'acceptable': '#9fb8d8',
    'good': '#7ec8c8',
}

fig, axes = plt.subplots(1, 4, figsize=(18, 5), sharey=True)

for idx, (ax, dim, dim_label) in enumerate(zip(axes, dimensions, dim_labels)):
    df_dim = df[df['dimension'] == dim].copy()
    df_dim = df_dim.set_index('system').reindex(systems)

    poor = df_dim['pct_poor'].values
    acceptable = df_dim['pct_acceptable'].values
    good = df_dim['pct_good'].values

    y = np.arange(len(systems))

    ax.barh(y, poor, color=colors['poor'], height=0.6)
    ax.barh(y, acceptable, color=colors['acceptable'], height=0.6, left=poor)
    ax.barh(y, good, color=colors['good'], height=0.6, left=poor + acceptable)

    # Label only segments with enough space.
    for i in range(len(systems)):
        if poor[i] >= 8:
            ax.text(
                poor[i] / 2,
                i,
                f'{poor[i]:.0f}%',
                ha='center',
                va='center',
                fontsize=12,
                color='white',
                fontweight='bold'
            )

        if acceptable[i] >= 8:
            ax.text(
                poor[i] + acceptable[i] / 2,
                i,
                f'{acceptable[i]:.0f}%',
                ha='center',
                va='center',
                fontsize=12,
                color='white',
                fontweight='bold'
            )

        if good[i] >= 8:
            ax.text(
                poor[i] + acceptable[i] + good[i] / 2,
                i,
                f'{good[i]:.0f}%',
                ha='center',
                va='center',
                fontsize=12,
                color='white',
                fontweight='bold'
            )

    ax.set_title(dim_label, fontweight='bold', fontsize=18, pad=10)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize=14)
    ax.set_yticks(y)

    if idx == 0:
        ax.set_yticklabels(sys_labels, fontsize=14)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', linestyle='--', alpha=0.4)

# Shared legend below the plots.
legend_patches = [
    mpatches.Patch(color=colors['poor'], label='Poor (1)'),
    mpatches.Patch(color=colors['acceptable'], label='Acceptable (2)'),
    mpatches.Patch(color=colors['good'], label='Good (3)'),
]

plt.tight_layout()
plt.subplots_adjust(bottom=0.22)

fig.legend(
    handles=legend_patches,
    loc='lower center',
    ncol=3,
    fontsize=14,
    frameon=False,
    bbox_to_anchor=(0.5, 0.02)
)

plt.savefig('figure1_expert_ratings.pdf', bbox_inches='tight', dpi=300)
plt.savefig('figure1_expert_ratings.png', bbox_inches='tight', dpi=300)
plt.show()