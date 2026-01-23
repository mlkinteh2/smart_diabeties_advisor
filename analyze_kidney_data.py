import pandas as pd
import numpy as np

# Load and analyze the kidney dataset
k_data = pd.read_csv('predictions/ml/kidney.csv')

print("=" * 80)
print("KIDNEY DATASET ANALYSIS")
print("=" * 80)
print()

print(f"Total samples: {len(k_data)}")
print(f"Class distribution:")
print(k_data['Class'].value_counts().sort_index())
print()

# Analyze healthy vs diseased patients
diseased = k_data[k_data['Class'] == 1]
healthy = k_data[k_data['Class'] == 0]

print(f"\nDISEASED Patients (Class=1): {len(diseased)} samples")
print("─" * 80)
print(diseased[['Sc', 'Hemo', 'Bu', 'Sod', 'Pot']].describe())

print(f"\nHEALTHY Patients (Class=0): {len(healthy)} samples")
print("─" * 80)
print(healthy[['Sc', 'Hemo', 'Bu', 'Sod', 'Pot']].describe())

print("\n" + "=" * 80)
print("KEY DIFFERENCES (Mean values):")
print("=" * 80)
print(f"{'Metric':<20} {'Diseased (Class=1)':<20} {'Healthy (Class=0)':<20}")
print("─" * 60)
print(f"{'Creatinine (Sc)':<20} {diseased['Sc'].mean():>18.2f} {healthy['Sc'].mean():>18.2f}")
print(f"{'Hemoglobin (Hemo)':<20} {diseased['Hemo'].mean():>18.2f} {healthy['Hemo'].mean():>18.2f}")
print(f"{'Urea (Bu)':<20} {diseased['Bu'].mean():>18.2f} {healthy['Bu'].mean():>18.2f}")
print(f"{'Sodium (Sod)':<20} {diseased['Sod'].mean():>18.2f} {healthy['Sod'].mean():>18.2f}")
print(f"{'Potassium (Pot)':<20} {diseased['Pot'].mean():>18.2f} {healthy['Pot'].mean():>18.2f}")
