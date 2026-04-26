import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Load the mapped qualitative evaluation data.
df_mapped = pd.read_excel('qualitative_mapped.xlsx')

systems = ['LLM', 'RAG', 'GraphRAG', 'Referenz']
sys_labels = ['LLM', 'RAG', 'GraphRAG', 'Gold Standard']

colors_map = {
    'LLM': '#b8aee0',
    'RAG': '#6a96c8',
    'GraphRAG': '#4aaba8',
    'Referenz': '#b8e0c8',
}

df_pref = df_mapped[['rater', 'case_order', 'preferred_system']].drop_duplicates()
df_human = df_mapped[['rater', 'case_order', 'human_guess_system']].drop_duplicates()
total = len(df_pref)  # 76


# Preference counts across all systems.
pref_counts = df_pref['preferred_system'].value_counts()
pref_counts = pref_counts.reindex(systems, fill_value=0)

print("=== PRÄFERENZ (alle Systeme) ===")
print(f"Total Bewertungen: {total}")

for s, l in zip(systems, sys_labels):
    count = int(pref_counts.get(s, 0))
    print(f"{l}: {count} ({count / total * 100:.1f}%)")


# Precision and recall when treating each system as a gold-standard substitute.
print("\n--- Precision & Recall als Gold Standard Substitute ---")
gold_count = int(pref_counts.get('Referenz', 0))

for s, l in zip(['LLM', 'RAG', 'GraphRAG'], ['LLM', 'RAG', 'GraphRAG']):
    tp = int(pref_counts.get(s, 0))
    fn = gold_count
    fp = tp

    precision = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0

    print(f"{l}: Precision={precision:.1f}%, Recall={recall:.1f}%")


# Human detection counts.
human_counts = df_human['human_guess_system'].value_counts()
not_assessable = int(human_counts.get('Nicht beurteilbar', 0))

df_human_valid = df_human[
    ~df_human['human_guess_system'].isin(['Nicht beurteilbar', 'nan', 'None'])
]

human_counts_valid = df_human_valid['human_guess_system'].value_counts()
human_counts_valid = human_counts_valid.reindex(systems, fill_value=0)
total_valid = len(df_human_valid)

print("\n=== HUMAN DETECTION (alle Systeme) ===")
print(f"Total valide Antworten: {total_valid}")
print(f"Nicht beurteilbar: {not_assessable}")

for s, l in zip(systems, sys_labels):
    count = int(human_counts_valid.get(s, 0))
    print(f"{l}: {count} ({count / total_valid * 100:.1f}%)")


# Accuracy, precision, and recall for human detection.
gold_human = int(human_counts_valid.get('Referenz', 0))
tp_h = gold_human
fp_h = total_valid - gold_human
fn_h = total_valid - gold_human

print(f"\nGold Standard korrekt erkannt (Accuracy): {gold_human / total_valid * 100:.1f}%")
print(f"Precision: {tp_h / (tp_h + fp_h) * 100:.1f}%")
print(f"Recall:    {tp_h / (tp_h + fn_h) * 100:.1f}%")


# Figure 2: preference counts.
fig2, ax2 = plt.subplots(figsize=(8, 5))

bars = ax2.bar(
    sys_labels,
    [pref_counts[s] for s in systems],
    color=[colors_map[s] for s in systems],
    width=0.5,
    edgecolor='white',
)

for bar in bars:
    h = bar.get_height()
    pct = h / total * 100
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        h + 0.5,
        f'{int(h)}\n({pct:.1f}%)',
        ha='center',
        va='bottom',
        fontsize=12,
        fontweight='bold'
    )

ax2.set_ylabel('Number of Selections', fontsize=14)
ax2.set_xlabel('System', fontsize=14)
ax2.set_ylim(0, max(pref_counts) * 1.25)
ax2.tick_params(axis='both', labelsize=14)

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(axis='y', linestyle='--', alpha=0.4)

plt.tight_layout()
plt.savefig('figure2_preference.pdf', bbox_inches='tight', dpi=300)
plt.savefig('figure2_preference.png', bbox_inches='tight', dpi=300)
plt.show()


# Figure 3: perceived human authorship.
all_labels_human = sys_labels + ['Not assessable']
all_colors_human = [colors_map[s] for s in systems] + ['#cccccc']
all_counts_human = [int(human_counts_valid.get(s, 0)) for s in systems] + [not_assessable]

fig3, ax3 = plt.subplots(figsize=(9, 5))

bars3 = ax3.bar(
    all_labels_human,
    all_counts_human,
    color=all_colors_human,
    width=0.5,
    edgecolor='white',
)

for bar in bars3:
    h = bar.get_height()
    pct = h / total * 100
    ax3.text(
        bar.get_x() + bar.get_width() / 2,
        h + 0.3,
        f'{int(h)}\n({pct:.1f}%)',
        ha='center',
        va='bottom',
        fontsize=12,
        fontweight='bold'
    )

ax3.set_ylabel('Number of Selections', fontsize=14)
ax3.set_xlabel('System', fontsize=14)
ax3.set_ylim(0, max(all_counts_human) * 1.25)
ax3.tick_params(axis='both', labelsize=14)

ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.grid(axis='y', linestyle='--', alpha=0.4)

plt.tight_layout()
plt.savefig('figure3_human_detection.pdf', bbox_inches='tight', dpi=300)
plt.savefig('figure3_human_detection.png', bbox_inches='tight', dpi=300)
plt.show()

print("\nAlle Figures gespeichert!")