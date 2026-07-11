"""
Generates synthetic data for testing the pipeline when Kaggle is unavailable.
"""
import os
import pandas as pd
import numpy as np
from PIL import Image
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def generate_synthetic_symptom_data():
    dest_dir = PROJECT_ROOT / "data" / "raw" / "text"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "Symptom2Disease.csv"
    
    if dest_file.exists():
        print("[OK] Symptom data exists.")
        return
        
    print("[DOWN] Generating synthetic Symptom2Disease.csv...")
    
    conditions = [
        "Psoriasis", "Varicose veins", "Typhoid", "Chicken pox", "Impetigo",
        "Dengue", "Fungal infection", "Common Cold", "Pneumonia", "Dimorphic hemorrhoids(piles)",
        "Arthritis", "Acne", "Bronchial Asthma", "Hypertension", "Migraine",
        "Cervical spondylosis", "Jaundice", "Malaria", "urinary tract infection", "allergy",
        "gastroesophageal reflux disease", "drug reaction", "peptic ulcer disease", "diabetes"
    ]
    
    data = []
    for i, condition in enumerate(conditions):
        for _ in range(20): # 20 samples per condition
            symptom_text = f"I have been feeling terrible. My symptoms are consistent with {condition}. I have pain and discomfort."
            data.append({"label": condition, "text": symptom_text})
            
    df = pd.DataFrame(data)
    df.to_csv(dest_file, index=False)
    print(f"[OK] Saved synthetic symptom data to {dest_file}")


def generate_synthetic_xray_data():
    base_dir = PROJECT_ROOT / "data" / "raw" / "xray"
    
    if (base_dir / "train").exists():
        print("[OK] X-ray data exists.")
        return
        
    print("[DOWN] Generating synthetic X-ray data...")
    splits = ["train", "val", "test"]
    classes = ["NORMAL", "PNEUMONIA"]
    
    for split in splits:
        num_images = 10 if split == "train" else 2
        for cls in classes:
            img_dir = base_dir / split / cls
            img_dir.mkdir(parents=True, exist_ok=True)
            
            for i in range(num_images):
                # Create a 224x224 RGB image (random noise to simulate X-ray texture)
                noise = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
                img = Image.fromarray(noise)
                img.save(img_dir / f"synthetic_{i}.jpg")
                
    print("[OK] Saved synthetic X-ray data.")


if __name__ == "__main__":
    print("Generating synthetic datasets...")
    generate_synthetic_symptom_data()
    generate_synthetic_xray_data()
    print("Done!")
