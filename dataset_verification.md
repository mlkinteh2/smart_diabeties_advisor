# Dataset Analysis - Unit Verification

## Diabetes Dataset (PIMA Indian Diabetes)
**Source**: `predictions/ml/diabetes.csv`

### Columns Used for Training:
- **Age** (years): 21-81 → Training uses as-is
- **BMI** (kg/m²): 0-67.1 → Zeros imputed with median (32.0)
- **BloodPressure** (mmHg): 0-122 → Zeros imputed with median (72.0)
- **Glucose** (mg/dL): 0-199 → Zeros imputed with median (117.0)

### Training Preprocessing:
```python
# Zero imputation for: Glucose, BloodPressure, BMI
median_val = df[df[col] != 0][col].median()
df[col] = df[col].replace(0, median_val)
```

### Realistic Ranges (Post-imputation):
- Age: 21-81 (no imputation)
- BMI: 18.5-67.1 (zeros replaced)
- BP: 62-122 (zeros replaced, 25th percentile = 62)
- Glucose: 99-199 (zeros replaced, 25th percentile = 99)

---

## Kidney Dataset
**Source**: `predictions/ml/kidney.csv`

### Original Columns → Renamed:
- **Bp** → Blood Pressure (mmHg)
- **Sc** → Creatinine (mg/dL)
- **Pot** → Pottasium (mEq/L) [typo intentional]
- **Hemo** → Hemoglobin (g/dL)
- **Sod** → Sodium (mEq/L)
- **Bu** → Urea (mg/dL)
- **Al** → Albumin (0-5 categorical)

### Training Preprocessing:
```python
# Outlier removal
df1 = df1[df1['Pottasium'] <= 7]
df1 = df1[df1['Hemoglobin'] <= 20]
df1 = df1[df1['Blood Pressure'] >= 50]

# Winsorization
df1['Creatinine'] = df1['Creatinine'].clip(0, 15)
df1['Pottasium'] = df1['Pottasium'].clip(2, 7)
df1['Hemoglobin'] = df1['Hemoglobin'].clip(4, 20)
df1['Sodium'] = df1['Sodium'].clip(100, 180)
df1['Blood Pressure'] = df1['Blood Pressure'].clip(60, 180)
```

### Realistic Ranges (Post-cleaning):
- Creatinine: 0.4-15 (clipped at 15)
- Potassium: 2.0-7.0 (filtered ≤7, clipped 2-7)
- Hemoglobin: 4.0-20.0 (filtered ≤20, clipped 4-20)
- Sodium: 100-180 (clipped 100-180)
- BP: 50-180 (filtered ≥50, clipped 60-180)
- Urea: 1.5-391 (RAW, no clipping in training!)
- Albumin: 0-5 (categorical, no processing)

---

## Corrected Validation Ranges

### Diabetes (Match Training Imputation):
| Feature | Current Range | **Correct Range** | Unit |
|---------|---------------|-------------------|------|
| Age | 18-100 | **21-100** | years |
| BMI | 10-70 | **15-70** | kg/m² |
| Glucose | 50-400 | **70-400** | mg/dL |
| BP Systolic | 40-250 | **50-200** | mmHg |

### Kidney (Match Training Clipping):
| Feature | Current Range | **Correct Range** | Unit |
|---------|---------------|-------------------|------|
| Creatinine | 0.1-20 | **0.4-15** | mg/dL |
| Potassium | 1.5-10 | **2.0-7.0** | mEq/L |
| Hemoglobin | 3-25 | **4.0-20** | g/dL |
| Sodium | 100-180 | **100-180** ✓ | mEq/L |
| BP | 40-250 | **50-180** | mmHg |
| Urea | 5-500 | **5-400** | mg/dL |
| Albumin | 0-5 | **0-5** ✓ | categorical |

---

## Action Items

1. Update `views.py` validation to match training preprocessing
2. Update HTML5 min/max attributes
3. Verify units displayed in templates are correct
