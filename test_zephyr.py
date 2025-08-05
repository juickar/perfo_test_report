import re
import os
import matplotlib.pyplot as plt
import numpy as np

filename_mp13 = 'mp13.txt'
filename_mp25 = 'mp25.txt'
output_dir = 'barplots_comparison_zephyr'
os.makedirs(output_dir, exist_ok=True)

metrics = ['mean']
metric_patterns = {m: re.compile(
    rf'^(?P<test>[\w\.\+\-]+)\.{m}\s*:\s*\d+\s*cycles\s*,\s*(?P<ns>\d+)\s*ns'
) for m in metrics}

section_pattern = re.compile(r'^////\s*(.+?)\s*////$')

def parse_file(filename):
    sections = {}
    current_section = 'Global'
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            sec_match = section_pattern.match(line)
            if sec_match:
                current_section = sec_match.group(1).strip()
                if current_section not in sections:
                    sections[current_section] = {}
                continue

            for m in metrics:
                match = metric_patterns[m].match(line)
                if match:
                    test_name = match.group('test')
                    ns_val = int(match.group('ns'))
                    if current_section not in sections:
                        sections[current_section] = {}
                    if test_name not in sections[current_section]:
                        sections[current_section][test_name] = {}
                    sections[current_section][test_name][m] = ns_val
    return sections

data_mp13 = parse_file(filename_mp13)
data_mp25 = parse_file(filename_mp25)

def plot_comparison_p90max(section_name, data1, data2, label1='mp13', label2='mp25'):
    tests_common = set(data1.keys()) & set(data2.keys())
    if not tests_common:
        print(f"Aucun test commun dans la section '{section_name}', ignoré.")
        return

    tests_common = sorted(tests_common)
    n = len(tests_common)
    x = np.arange(n)
    width = 0.35

    plt.figure(figsize=(max(10, n*0.7), 6))

    # Barres 0-mean pour mp13
    mins1 = [0 for t in tests_common]
    p90s1 = [data1[t]['mean'] for t in tests_common]
    heights1 = [p90s1[i] - mins1[i] for i in range(n)]
    bars1 = plt.bar(x - width/2, heights1, width, bottom=mins1, color='lightblue', alpha=0.7, label=label1, edgecolor='black')

    # Barres 0-mean pour mp25
    mins2 = [0 for t in tests_common]
    p90s2 = [data2[t]['mean'] for t in tests_common]
    heights2 = [p90s2[i] - mins2[i] for i in range(n)]
    bars2 = plt.bar(x + width/2, heights2, width, bottom=mins2, color='lightgreen', alpha=0.7, label=label2, edgecolor='black')

    plt.xticks(x, tests_common, rotation=45, ha='right')
    plt.ylabel('Temps (ns)')
    plt.title(f"Comparaison temps moyen pour la section '{section_name}'")
    ax = plt.gca()

    colors = {
        'mean': 'red',
    }
    half_width = width / 2 * 0.9

    # Traits et valeurs pour mp13
    for i, t in enumerate(tests_common):
        stats = data1[t]
        x_center = x[i] - width/2 + width/2
        for metric, color in colors.items():
            if metric in stats:
                val = stats[metric]
                ax.hlines(val, x_center - width, x_center , colors=color, linewidth=2)
                ax.text(x_center - half_width, val + max(p90s1)*0.02, f"{val}", ha='center', va='bottom', fontsize=7, color=color)

    # Traits et valeurs pour mp25
    for i, t in enumerate(tests_common):
        stats = data2[t]
        x_center = x[i] + width/2 + width/2
        for metric, color in colors.items():
            if metric in stats:
                val = stats[metric]
                ax.hlines(val, x_center - width, x_center , colors=color, linewidth=2)
                ax.text(x_center- half_width, val + max(p90s2)*0.02, f"{val}", ha='center', va='bottom', fontsize=7, color=color)

    # Légende
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color=c, lw=2, label=lab.capitalize()) for lab, c in colors.items()]
    legend_elements += [
        plt.Rectangle((0,0),1,1,color='lightblue', alpha=0.7, label=label1),
        plt.Rectangle((0,0),1,1,color='lightgreen', alpha=0.7, label=label2)
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    filename_safe = section_name.replace(' ', '_').replace('/', '_')
    filepath = os.path.join(output_dir, f"{filename_safe}.png")
    plt.savefig(filepath)
    plt.close()
    print(f"Graphique sauvegardé : {filepath}")

sections_common = set(data_mp13.keys()) & set(data_mp25.keys())
for section in sections_common:
    plot_comparison_p90max(section, data_mp13[section], data_mp25[section])
