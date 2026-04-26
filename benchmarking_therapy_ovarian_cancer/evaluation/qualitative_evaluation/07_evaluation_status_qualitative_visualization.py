import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Split the qualitative ratings by case status and create stratified plots and summaries.
df = pd.read_excel('qualitative_mapped.xlsx')
# TODO generalize
df_study = pd.read_excel('/Users/sarahberbuir/Desktop/TUM/6-SS-25/MA/qualitative_eval/Studienaufbau kopie.xlsx')

status_map = dict(zip(df_study['Case order google form'], df_study['Status']))
df['status'] = df['case_order'].map(status_map)

dimensions = ['correctness', 'completeness', 'comprehensibility', 'applicability']
dim_labels = ['Correctness', 'Completeness', 'Comprehensibility', 'Applicability']

systems = ['GraphRAG', 'RAG', 'LLM', 'Referenz']
sys_labels = ['GraphRAG', 'RAG', 'LLM', 'Gold Standard']

colors = {
    'poor': '#c9ada7',
    'acceptable': '#9fb8d8',
    'good': '#7ec8c8'
}

status_list = ['Verdacht', 'Diagnose']
status_labels = ['Suspected ovarian cancer (n = 11)', 'Confirmed diagnosis (n = 8)']


# Stratified Likert plots.
fig, axes = plt.subplots(2, 4, figsize=(22, 10))

for row, (st, st_label) in enumerate(zip(status_list, status_labels)):
    df_sub = df[df['status'] == st]

    recs = []

    for system in systems:
        df_sys = df_sub[df_sub['system'] == system]

        for dim in dimensions:
            total = df_sys[dim].notna().sum()

            for val, key in zip([1, 2, 3], ['pct_poor', 'pct_acceptable', 'pct_good']):
                count = (df_sys[dim] == val).sum()

                recs.append({
                    'system': system,
                    'dimension': dim,
                    key: round(count / total * 100, 1) if total > 0 else 0
                })

    df_pivot = pd.DataFrame(recs).groupby(['system', 'dimension']).sum().reset_index()

    for col, (dim, dim_label) in enumerate(zip(dimensions, dim_labels)):
        ax = axes[row, col]
        df_dim = df_pivot[df_pivot['dimension'] == dim].set_index('system').reindex(systems)

        poor = df_dim['pct_poor'].values
        acceptable = df_dim['pct_acceptable'].values
        good = df_dim['pct_good'].values

        y = np.arange(len(systems))

        ax.barh(y, poor, color=colors['poor'], height=0.6)
        ax.barh(y, acceptable, color=colors['acceptable'], height=0.6, left=poor)
        ax.barh(y, good, color=colors['good'], height=0.6, left=poor + acceptable)

        # Add labels only where the segment is wide enough.
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

        if row == 0:
            ax.set_title(dim_label, fontweight='bold', fontsize=18, pad=10)

        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize=16)
        ax.set_yticks(y)

        if col == 0:
            ax.set_yticklabels(sys_labels, fontsize=16)
            ax.tick_params(labelleft=True)
        else:
            ax.set_yticklabels([])

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', linestyle='--', alpha=0.4)

    axes[row, 0].set_ylabel(st_label, fontsize=18, fontweight='bold', labelpad=15)


legend_patches = [
    mpatches.Patch(color=colors['poor'], label='Poor (1)'),
    mpatches.Patch(color=colors['acceptable'], label='Acceptable (2)'),
    mpatches.Patch(color=colors['good'], label='Good (3)'),
]

plt.tight_layout()
plt.subplots_adjust(bottom=0.10, hspace=0.15)

fig.legend(
    handles=legend_patches,
    loc='lower center',
    ncol=3,
    fontsize=14,
    frameon=False,
    bbox_to_anchor=(0.5, 0.01)
)

plt.savefig('figure_ratings_stratified.pdf', bbox_inches='tight', dpi=300)
plt.savefig('figure_ratings_stratified.png', bbox_inches='tight', dpi=300)
plt.show()


# Preference and human-detection summaries by status.
systems_print = ['Referenz', 'LLM', 'GraphRAG', 'RAG']
sys_labels_print = ['Gold Standard', 'LLM', 'GraphRAG', 'RAG']

for st in ['Diagnose', 'Verdacht']:
    df_sub = df[df['status'] == st]

    df_pref = df_sub[['rater', 'case_order', 'preferred_system']].drop_duplicates()
    total_pref = len(df_pref)
    pref_counts = df_pref['preferred_system'].value_counts()

    print(f"\n=== {st} – Präferenz (n={total_pref}) ===")

    for s, l in zip(systems_print, sys_labels_print):
        c = int(pref_counts.get(s, 0))
        print(f"  {l}: {c} ({c / total_pref * 100:.1f}%)")

    df_human = df_sub[['rater', 'case_order', 'human_guess_system']].drop_duplicates()
    not_assessable = int(df_human['human_guess_system'].value_counts().get('Nicht beurteilbar', 0))

    df_human_valid = df_human[
        ~df_human['human_guess_system'].isin(['Nicht beurteilbar', 'nan', 'None'])
    ]

    human_counts = df_human_valid['human_guess_system'].value_counts()
    total_valid = len(df_human_valid)

    print(f"\n=== {st} – Human Detection (n={total_valid}, nicht beurteilbar={not_assessable}) ===")

    for s, l in zip(systems_print, sys_labels_print):
        c = int(human_counts.get(s, 0))
        print(f"  {l}: {c} ({c / total_valid * 100:.1f}%)")


# Likert percentages by status.
print("\n" + "=" * 60)
print("LIKERT-VERTEILUNGEN PRO STATUS")

for st in ['Diagnose', 'Verdacht']:
    df_sub = df[df['status'] == st]

    print(f"\n{'=' * 40} {st} {'=' * 40}")

    for system in ['Referenz', 'LLM', 'RAG', 'GraphRAG']:
        df_sys = df_sub[df_sub['system'] == system]

        print(f"\n  {system}:")

        for dim in dimensions:
            total = df_sys[dim].notna().sum()

            poor = (df_sys[dim] == 1).sum()
            acc = (df_sys[dim] == 2).sum()
            good = (df_sys[dim] == 3).sum()

            print(
                f"    {dim:20s}: "
                f"poor={poor / total * 100:5.1f}%  "
                f"acc={acc / total * 100:5.1f}%  "
                f"good={good / total * 100:5.1f}%  "
                f"(mean={df_sys[dim].mean():.3f})"
            )


# Mean scores by status and system.
print("\n" + "=" * 60)
print("MEAN SCORES PRO STATUS UND SYSTEM")
print(df.groupby(['status', 'system'])[dimensions].mean().round(2))