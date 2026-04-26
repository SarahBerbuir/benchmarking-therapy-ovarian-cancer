import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Plot Likert distributions from the LLM-as-a-judge ratings.
df_judge = pd.read_excel('llm_as_a_judge_v2.xlsx', sheet_name='likert_ratings')

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability']
dim_labels = ['Correctness', 'Completeness', 'Comprehensibility', 'Applicability']

systems = ['GraphRAG', 'RAG', 'LLM', 'Referenz']
sys_labels = ['GraphRAG', 'RAG', 'LLM', 'Gold Standard']

colors = {
    'poor': '#c9ada7',
    'acceptable': '#9fb8d8',
    'good': '#7ec8c8',
}

# Compute percentages in the same format as likert_distributions.xlsx.
records = []

for system in systems:
    df_sys = df_judge[df_judge['system'] == system]

    for dim in dimensions:
        total = df_sys[dim].notna().sum()

        for val, label in zip([1, 2, 3], ['pct_poor', 'pct_acceptable', 'pct_good']):
            count = (df_sys[dim] == val).sum()

            records.append({
                'system': system,
                'dimension': dim,
                label: round(count / total * 100, 1) if total > 0 else 0
            })


df_pivot = pd.DataFrame(records).groupby(['system', 'dimension']).sum().reset_index()

fig, axes = plt.subplots(1, 4, figsize=(18, 5), sharey=True)

for idx, (ax, dim, dim_label) in enumerate(zip(axes, dimensions, dim_labels)):
    df_dim = df_pivot[df_pivot['dimension'] == dim].copy()
    df_dim = df_dim.set_index('system').reindex(systems)

    poor = df_dim['pct_poor'].values
    acceptable = df_dim['pct_acceptable'].values
    good = df_dim['pct_good'].values

    y = np.arange(len(systems))

    ax.barh(y, poor, color=colors['poor'], height=0.6)
    ax.barh(y, acceptable, color=colors['acceptable'], height=0.6, left=poor)
    ax.barh(y, good, color=colors['good'], height=0.6, left=poor + acceptable)

    # Show percentage labels only when the segment is large enough.
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

plt.savefig('figure4_judge_ratings.pdf', bbox_inches='tight', dpi=300)
plt.savefig('figure4_judge_ratings.png', bbox_inches='tight', dpi=300)
plt.show()

print("Gespeichert!")