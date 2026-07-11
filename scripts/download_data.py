import os

def check_data():
    print("Checking dataset availability...")
    paths = [
        "data/raw/xray/train",
        "data/raw/tabular/heart.csv",
        "data/raw/text/Symptom2Disease.csv"
    ]
    all_exist = True
    for p in paths:
        if not os.path.exists(p):
            print(f"Missing: {p}")
            all_exist = False
    
    if not all_exist:
        print("Note: To download actual Kaggle datasets, please configure Kaggle API keys.")
        print("Run `python scripts/generate_synthetic_data.py` to generate synthetic data instead.")
    else:
        print("All raw datasets found.")

if __name__ == "__main__":
    check_data()
