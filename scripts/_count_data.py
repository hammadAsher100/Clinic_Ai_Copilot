from pathlib import Path
dirs = [
    'data/raw/xray/train/NORMAL',
    'data/raw/xray/train/PNEUMONIA',
    'data/raw/xray/val/NORMAL',
    'data/raw/xray/val/PNEUMONIA',
    'data/raw/xray/test/NORMAL',
    'data/raw/xray/test/PNEUMONIA',
]
for d in dirs:
    p = Path(d)
    if p.exists():
        print(f"{d}: {len(list(p.glob('*')))} files")
    else:
        print(f"{d}: MISSING")

# Also check text data
tp = Path('data/raw/text/Symptom2Disease.csv')
if tp.exists():
    import pandas as pd
    df = pd.read_csv(tp)
    print(f"\nText dataset: {len(df)} rows, {df.columns.tolist()}")
    if 'label' in df.columns:
        print(f"Classes: {df['label'].nunique()}")
        print(df['label'].value_counts().head(10))
else:
    print(f"\nText dataset: MISSING")
