import re
import os
import matplotlib.pyplot as plt
import numpy as np

def parse_stddev_by_section(filename):
    section_pattern = re.compile(r'^////\s*(.+?)\s*////$')
    stddev_pattern = re.compile(
        r'^(?P<test>[\w\.\+\-]+)\.stddev\s*:\s*\d+\s*cycles\s*,\s*(?P<ns>\d+)\s*ns'
    )
    sections = {}
    current_section = 'Global'
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            sec_match = section_pattern.match(line)
            if sec_match:
                current_section = sec_match.group(1).strip()
                if current_section not in sections:
                    sections[current_section] = []
                continue

            match = stddev_pattern.match(line)
            if match:
                ns_val = int(match.group('ns'))
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(ns_val)
    return sections

filename_mp13 = 'mp13.txt'
filename_mp25 = 'mp25.txt'

# Extraire les données pour mp13 et mp25
mp13_data = parse_stddev_by_section(filename_mp13)
mp25_data = parse_stddev_by_section(filename_mp25)

# Calculer la moyenne des stddev par section et la moyenne totale pour mp13
mean_stddev_by_section_mp13 = []
all_values_mp13 = []
all_sections = sorted(set(mp13_data.keys()) | set(mp25_data.keys()))
for section in all_sections:
    vals = mp13_data.get(section, [])
    if vals:
        mean_val = np.mean(vals)
        mean_stddev_by_section_mp13.append(mean_val)
        all_values_mp13.extend(vals)
    else:
        mean_stddev_by_section_mp13.append(np.nan)
mean_stddev_total_mp13 = np.mean(all_values_mp13) if all_values_mp13 else np.nan

# Calculer la moyenne des stddev par section et la moyenne totale pour mp25
mean_stddev_by_section_mp25 = []
all_values_mp25 = []
for section in all_sections:
    vals = mp25_data.get(section, [])
    if vals:
        mean_val = np.mean(vals)
        mean_stddev_by_section_mp25.append(mean_val)
        all_values_mp25.extend(vals)
    else:
        mean_stddev_by_section_mp25.append(np.nan)
mean_stddev_total_mp25 = np.mean(all_values_mp25) if all_values_mp25 else np.nan

# Préparer les données pour le graphique
labels = all_sections + ['Total']
x = np.arange(len(labels))
width = 0.35

mp13_means = mean_stddev_by_section_mp13 + [mean_stddev_total_mp13]
mp25_means = mean_stddev_by_section_mp25 + [mean_stddev_total_mp25]

plt.figure(figsize=(max(12, len(labels)*0.6), 6))
bars1 = plt.bar(x - width/2, mp13_means, width, label='mp13', color='lightblue', alpha=0.7, edgecolor='black')
bars2 = plt.bar(x + width/2, mp25_means, width, label='mp25', color='salmon', alpha=0.7, edgecolor='black')

plt.xticks(x, labels, rotation=45, ha='right')
plt.ylabel('Moyenne des stddev (ns)')
plt.title('Moyenne des écarts types par type de test et total (mp13 vs mp25)')

# Ajouter les valeurs au-dessus des barres
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if np.isnan(height):
            continue
        if height < 1:
            text = '<1'
        else:
            text = f'{height:.1f}'
        plt.text(bar.get_x() + bar.get_width()/2, height, text, ha='center', va='bottom', fontsize=8)

plt.legend()
plt.tight_layout()

output_dir = 'stddev_comparison'
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, 'mean_stddev_comparison_mp13_mp25.png')
plt.savefig(filepath)
plt.close()
print(f"Graphique sauvegardé : {filepath}")
