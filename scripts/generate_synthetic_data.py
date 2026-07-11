"""
Generate MUCH better synthetic datasets for hackathon demo.

1. Text: Diverse, varied symptom descriptions with real medical vocabulary
2. X-ray: Structurally distinct synthetic images (not just noise)
"""
import os
import random
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ═══════════════════════════════════════════════════════════════════════
# SYMPTOM TEXT DATA — Diverse templates per condition
# ═══════════════════════════════════════════════════════════════════════

SYMPTOM_TEMPLATES = {
    "Psoriasis": [
        "I have red, scaly patches on my elbows and knees that are very itchy",
        "My skin has thick silvery scales and dry cracked areas that sometimes bleed",
        "I've had persistent skin redness with flaky patches spreading on my scalp",
        "There are raised inflamed lesions on my skin covered with whitish scales",
        "My nails have become pitted and ridged and I have plaques on my arms",
        "Itchy dry patches on my torso with shedding skin flakes for weeks",
        "I noticed reddish spots with silvery buildup on my lower back and legs",
        "Burning sensation on scaly red patches near my hairline and behind ears",
    ],
    "Varicose veins": [
        "My legs have swollen twisted veins that are very visible and painful",
        "I get heavy aching legs especially after standing for long periods",
        "Bulging blue purple veins on my calves with occasional cramping at night",
        "My ankles swell by evening and I can see enlarged veins on my thighs",
        "Legs feel heavy and tired with visible knotted veins and skin discoloration",
        "I have throbbing pain in my legs with spider veins spreading on my shins",
        "Swollen veins on my lower legs with itching and a burning sensation",
        "My legs cramp at night and twisted veins are becoming more prominent",
    ],
    "Typhoid": [
        "I have sustained high fever for over a week with severe headache and fatigue",
        "Prolonged fever with stomach pain diarrhea and loss of appetite",
        "High temperature that keeps rising with abdominal discomfort and weakness",
        "I've had fever for days with constipation then diarrhea and rose spots on chest",
        "Persistent fever with body aches chills and no energy to do anything",
        "Fever that won't go down with poor appetite nausea and abdominal tenderness",
        "Week-long fever with coated tongue muscle pain and general malaise",
        "High grade fever with headache lethargy and greenish loose stools",
    ],
    "Chicken pox": [
        "I have itchy red blisters all over my body with mild fever",
        "Small fluid-filled blisters appeared on my chest face and back with itching",
        "Rash that started as red spots and turned into blisters spreading everywhere",
        "My child has itchy vesicles on the trunk and face with low grade fever",
        "Clusters of blisters at different stages with extreme itchiness and tiredness",
        "Red bumps that turned into tiny blisters with clear fluid and mild fever",
        "Widespread itchy rash with blisters crusting over and new ones appearing",
        "Fever followed by intensely itchy rash with small blisters all over body",
    ],
    "Impetigo": [
        "Red sores on my face around nose and mouth that burst and form crusts",
        "My child has honey-colored crusty sores spreading on the face and hands",
        "Blisters that ooze and form yellowish brown scabs near the mouth",
        "Itchy red sores with golden crusts on the skin around my nose",
        "Small blisters that break open and weep fluid forming thick crusts",
        "Spreading sores with yellow scabs on face that are mildly itchy",
        "Crusty skin lesions near mouth and chin that appeared after a scratch",
        "Red painful sores that became crusty and are spreading to other areas",
    ],
    "Dengue": [
        "Very high fever with severe headache pain behind the eyes and joint pain",
        "Sudden high fever with muscle aches bone pain and skin rash",
        "I feel terrible with high fever body aches and a flat red rash appearing",
        "Fever with intense joint pain nausea vomiting and fatigue",
        "High temperature with retro-orbital pain and bleeding gums",
        "Severe fever with break-bone pain rash and swollen lymph nodes",
        "Acute fever headache myalgia and petechial rash on arms",
        "High fever for three days with extreme fatigue joint pain and nausea",
    ],
    "Fungal infection": [
        "I have circular red patches on my skin with raised edges that are itchy",
        "Ring-shaped rash on my groin area with burning and peeling skin",
        "Itchy flaky patches between my toes with cracking and redness",
        "Red scaly circular lesions on my arms that spread outward",
        "My feet have peeling itchy skin between the toes with a bad smell",
        "Circular rash with clear center and red scaly border on my torso",
        "Itchy moist area in skin folds with reddish discoloration",
        "White patches on skin with flaking and itching especially after sweating",
    ],
    "Common Cold": [
        "I have a runny nose sneezing sore throat and mild cough",
        "Stuffy nose with clear watery discharge and scratchy throat",
        "Sneezing frequently with nasal congestion and slight body aches",
        "Mild sore throat with runny nose and feeling a bit tired",
        "Nasal congestion watery eyes and occasional sneezing fits",
        "I caught a cold with blocked nose coughing and mild headache",
        "Runny nose sore throat and general feeling of being unwell",
        "Persistent sneezing with congestion and post-nasal drip",
    ],
    "Pneumonia": [
        "Severe cough with greenish phlegm high fever and chest pain when breathing",
        "Difficulty breathing with productive cough fever and sharp chest pain",
        "High fever shaking chills and cough producing thick yellow mucus",
        "Chest tightness with painful breathing rapid heartbeat and cough with phlegm",
        "Persistent cough with rust-colored sputum fever and shortness of breath",
        "I can barely breathe with fever chills and coughing up thick mucus",
        "Sharp pain in chest when coughing high temperature and extreme fatigue",
        "Fever with productive cough breathlessness and pain on deep inspiration",
    ],
    "Dimorphic hemorrhoids(piles)": [
        "I have painful swelling near my anus with bleeding during bowel movements",
        "Itching and discomfort around the rectum with blood on toilet paper",
        "Painful lumps near the anus that bleed when I strain during defecation",
        "Rectal bleeding with itchy swollen tissue around the anal area",
        "Pain during bowel movements with bright red blood and anal swelling",
        "Uncomfortable pressure and itching near anus with occasional bleeding",
        "Swollen painful hemorrhoids that protrude during straining",
        "Burning sensation with blood in stool and tender lumps near rectum",
    ],
    "Arthritis": [
        "My joints are stiff and painful especially in the morning and it takes hours to loosen up",
        "Swollen painful joints in my hands and knees with reduced range of motion",
        "Joint pain and stiffness that gets worse with cold weather and inactivity",
        "My knees and fingers are swollen tender and difficult to move",
        "Chronic joint pain with morning stiffness lasting more than an hour",
        "Aching joints with swelling and warmth especially in wrists and ankles",
        "Progressive joint stiffness with pain on movement and joint deformity",
        "Bilateral joint swelling with tenderness and difficulty gripping objects",
    ],
    "Acne": [
        "I have pimples and blackheads on my face chin and forehead",
        "Painful red bumps and whiteheads breaking out on my cheeks and jawline",
        "My skin has cystic lesions and comedones mainly on forehead and nose",
        "Frequent breakouts with inflamed pimples and oily skin on my face",
        "Deep painful cysts under the skin with multiple blackheads on nose",
        "Persistent acne on face and back with scarring from old breakouts",
        "Red inflamed papules and pustules on cheeks with excess oil production",
        "Hormonal breakouts along jawline with deep nodular lesions",
    ],
    "Bronchial Asthma": [
        "I have wheezing and difficulty breathing especially at night and during exercise",
        "Tight chest with shortness of breath and whistling sound when exhaling",
        "Recurrent episodes of breathlessness with dry cough and wheezing",
        "My breathing gets worse with dust and cold air with chest tightness",
        "Chronic cough at night with wheezing and feeling of suffocation",
        "Episodes of difficulty breathing with audible wheeze triggered by allergens",
        "Shortness of breath with chest constriction and persistent dry cough",
        "Wheezing attacks with rapid breathing and inability to catch my breath",
    ],
    "Hypertension": [
        "I have frequent headaches dizziness and my blood pressure readings are high",
        "Persistent headaches with occasional nosebleeds and blurred vision",
        "Feeling of pressure in my head with fatigue and elevated BP readings",
        "Frequent dizziness headaches and shortness of breath on exertion",
        "My doctor said my blood pressure is very high and I get headaches daily",
        "Throbbing headache with visual disturbances and pounding heartbeat",
        "Chronic headaches with face flushing and anxiety about elevated pressure",
        "Dizziness with ringing in ears and consistently high blood pressure",
    ],
    "Migraine": [
        "Severe throbbing headache on one side with nausea and sensitivity to light",
        "Intense pulsating pain in my head with aura visual disturbances and vomiting",
        "Debilitating headache with light and sound sensitivity lasting hours",
        "One-sided head pain with zigzag visual patterns nausea and photophobia",
        "Recurring severe headaches preceded by flashing lights and numbness",
        "Pounding headache with extreme light sensitivity and need to lie in dark room",
        "Unilateral throbbing headache with nausea vomiting and phonophobia",
        "Severe head pain that worsens with movement and accompanied by aura",
    ],
    "Cervical spondylosis": [
        "Neck pain and stiffness with pain radiating down to my shoulders and arms",
        "Chronic neck pain with numbness and tingling in my fingers",
        "Stiff neck with grinding sensation and headaches starting from the back of head",
        "Pain in my neck spreading to arms with occasional muscle weakness",
        "Neck stiffness with reduced mobility and tingling in both hands",
        "Chronic neck pain worse in the morning with shoulder blade discomfort",
        "Neck pain with dizziness and radiating arm pain with numbness",
        "Grinding noise when turning neck with stiffness and arm weakness",
    ],
    "Jaundice": [
        "My skin and eyes have turned yellow with dark urine and pale stools",
        "Yellowing of eyes with fatigue nausea and abdominal pain on right side",
        "Yellow discoloration of skin with itching and clay-colored stools",
        "My urine is very dark and skin looks yellowish with loss of appetite",
        "Eyes are yellow with upper abdominal pain and general weakness",
        "Yellowish tint to skin and whites of eyes with nausea and fatigue",
        "Dark brown urine with jaundiced skin and tenderness below right ribs",
        "Progressive yellowing of skin with itching fatigue and poor appetite",
    ],
    "Malaria": [
        "I have cyclical high fever with chills sweating and severe headache",
        "Recurring fever every two days with shaking chills and body aches",
        "High fever with rigors profuse sweating and extreme fatigue",
        "Intermittent fever with chills nausea vomiting and muscle pain",
        "Fever spikes with violent shivering followed by drenching sweats",
        "Periodic high temperature with headache and enlarged spleen area pain",
        "Cyclical fever pattern with intense chills sweating and weakness",
        "High fever alternating with chills and sweats with body pain and nausea",
    ],
    "urinary tract infection": [
        "Burning sensation when urinating with frequent urge to go and cloudy urine",
        "Pain during urination with strong smelling urine and pelvic pressure",
        "I need to urinate constantly but only small amounts come out with burning",
        "Burning urination with blood in urine and lower abdominal pain",
        "Frequent painful urination with foul smelling cloudy urine",
        "Urgency to urinate with dysuria and suprapubic discomfort",
        "Stinging pain when peeing with dark cloudy urine and back pain",
        "Constant urge to urinate with burning sensation and mild fever",
    ],
    "allergy": [
        "I have watery eyes runny nose sneezing and itchy throat after exposure to dust",
        "Skin rash with hives itching and swelling after eating certain foods",
        "Sneezing fits with nasal congestion itchy eyes triggered by pollen",
        "Itchy red welts on skin with swelling and difficulty breathing",
        "Seasonal symptoms with runny nose itchy eyes and constant sneezing",
        "Allergic reaction with swollen lips itching and red blotchy skin",
        "Nasal congestion with itchy watery eyes and scratchy throat from pet dander",
        "Breaking out in hives with itching after contact with certain materials",
    ],
    "gastroesophageal reflux disease": [
        "Burning sensation in my chest after eating with acid taste in mouth",
        "Heartburn that gets worse when lying down with regurgitation of food",
        "Chronic chest burning with sour taste and difficulty swallowing",
        "Acid reflux causing burning throat especially after heavy meals",
        "Frequent heartburn with belching bloating and chest discomfort",
        "Burning in upper abdomen and chest with acidic taste especially at night",
        "Chest pain after meals with acid coming up into throat",
        "Persistent heartburn with globus sensation and epigastric burning",
    ],
    "drug reaction": [
        "I developed a rash and itching all over after starting a new medication",
        "Skin eruption with fever and swollen lymph nodes after taking antibiotics",
        "Red blotchy rash appeared hours after taking my new prescription",
        "Hives and swelling with itching that started after medication change",
        "Widespread rash with peeling skin and mouth ulcers from a drug",
        "Fever and skin rash with joint pain after starting new medicine",
        "Allergic skin reaction with blistering after taking painkillers",
        "Itchy raised welts with facial swelling following drug administration",
    ],
    "peptic ulcer disease": [
        "Burning stomach pain that gets worse when hungry and better after eating",
        "Gnawing pain in upper abdomen with bloating nausea and vomiting",
        "Epigastric pain that wakes me up at night with acid reflux",
        "Stomach pain relieved by food but returns hours later with bloating",
        "Burning abdominal pain with loss of appetite and unintentional weight loss",
        "Upper stomach pain worse on empty stomach with dark tarry stools",
        "Recurring gnawing abdominal pain with nausea and feeling of fullness",
        "Burning pain between meals with bloating belching and poor appetite",
    ],
    "diabetes": [
        "I'm always thirsty urinating frequently and losing weight despite eating well",
        "Constant fatigue with increased hunger frequent urination and blurry vision",
        "Extreme thirst with frequent trips to bathroom and slow healing wounds",
        "Unexplained weight loss with constant hunger tiredness and blurred vision",
        "Frequent urination especially at night with unquenchable thirst",
        "Tingling in hands and feet with excessive thirst and frequent urination",
        "Fatigue with polydipsia polyuria and recurrent infections",
        "Increased appetite with weight loss blurry vision and slow wound healing",
    ],
}

def generate_better_symptom_data():
    """Generate diverse text data with noise and variation."""
    dest_dir = PROJECT_ROOT / "data" / "raw" / "text"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "Symptom2Disease.csv"

    # Noise phrases to inject variety
    fillers = [
        "I've been feeling this way for about {} days",
        "This has been going on for {} weeks now",
        "It started {} days ago and hasn't improved",
        "I noticed this around {} days back",
    ]
    severity = [
        "it's quite severe", "it's mild but persistent", "it comes and goes",
        "it's getting progressively worse", "it's moderate in intensity",
        "the symptoms are worsening daily", "it fluctuates throughout the day",
    ]
    extras = [
        "I also feel generally unwell", "I've been more tired than usual",
        "My appetite has decreased", "I haven't been sleeping well because of this",
        "It's affecting my daily routine", "I'm quite worried about it",
        "I tried home remedies but nothing helps", "This is the first time I've had this",
        "I had something similar years ago", "My family member had similar symptoms",
    ]

    data = []
    for condition, templates in SYMPTOM_TEMPLATES.items():
        # Generate 50 samples per condition (50 * 24 = 1200 rows)
        for i in range(50):
            base = random.choice(templates)
            # Add noise: filler + severity + extra context
            parts = [base]
            if random.random() > 0.3:
                parts.append(random.choice(fillers).format(random.randint(1, 14)))
            if random.random() > 0.4:
                parts.append(random.choice(severity))
            if random.random() > 0.5:
                parts.append(random.choice(extras))
            # Randomly shuffle non-first parts
            body = parts[0]
            rest = parts[1:]
            random.shuffle(rest)
            text = ". ".join([body] + rest) + "."
            # Randomly lowercase or keep mixed case
            if random.random() > 0.5:
                text = text.lower()
            data.append({"label": condition, "text": text})

    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(dest_file, index=False)
    print(f"[TEXT] Generated {len(df)} samples across {df['label'].nunique()} classes -> {dest_file}")


# ═══════════════════════════════════════════════════════════════════════
# X-RAY IMAGE DATA — Structurally distinct synthetic images
# ═══════════════════════════════════════════════════════════════════════

def _make_normal_xray(size=224):
    """Create a synthetic 'NORMAL' chest X-ray-like image.
    Clear lung fields, visible rib structures, symmetric."""
    img = Image.new('RGB', (size, size), (20, 20, 25))
    draw = ImageDraw.Draw(img)

    # Body outline (thorax shape)
    draw.ellipse([30, 20, size-30, size-10], fill=(40, 40, 45), outline=(50, 50, 55))

    # Lung fields — clear, symmetric ovals
    draw.ellipse([45, 40, size//2-10, size-40], fill=(30, 30, 35))  # left lung
    draw.ellipse([size//2+10, 40, size-45, size-40], fill=(30, 30, 35))  # right lung

    # Spine / mediastinum (central bright line)
    draw.rectangle([size//2-8, 30, size//2+8, size-20], fill=(60, 60, 65))

    # Ribs — horizontal lines across lungs
    for y in range(55, size-50, 22):
        draw.line([(50, y), (size//2-15, y)], fill=(50, 50, 55), width=2)
        draw.line([(size//2+15, y), (size-50, y)], fill=(50, 50, 55), width=2)

    # Heart silhouette (left side)
    draw.ellipse([size//2-30, size//2-10, size//2+20, size//2+50], fill=(55, 55, 60))

    # Add slight noise
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 3, arr.shape).astype(np.float32)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return img


def _make_pneumonia_xray(size=224):
    """Create a synthetic 'PNEUMONIA' chest X-ray-like image.
    Opacities/consolidations in lung fields, hazier appearance."""
    img = Image.new('RGB', (size, size), (25, 25, 30))
    draw = ImageDraw.Draw(img)

    # Body outline
    draw.ellipse([30, 20, size-30, size-10], fill=(45, 45, 50), outline=(55, 55, 60))

    # Lung fields — hazy, less distinct
    draw.ellipse([45, 40, size//2-10, size-40], fill=(38, 38, 42))
    draw.ellipse([size//2+10, 40, size-45, size-40], fill=(38, 38, 42))

    # Spine
    draw.rectangle([size//2-8, 30, size//2+8, size-20], fill=(65, 65, 70))

    # Ribs — less visible through opacities
    for y in range(55, size-50, 22):
        draw.line([(50, y), (size//2-15, y)], fill=(45, 45, 50), width=1)
        draw.line([(size//2+15, y), (size-50, y)], fill=(45, 45, 50), width=1)

    # Heart
    draw.ellipse([size//2-30, size//2-10, size//2+20, size//2+50], fill=(60, 60, 65))

    # PNEUMONIA MARKERS: consolidation patches (bright opacities in lung fields)
    # Randomly place 2-4 opacities
    num_patches = random.randint(2, 4)
    for _ in range(num_patches):
        # Pick a random location in one of the lung fields
        side = random.choice(['left', 'right'])
        if side == 'left':
            cx = random.randint(60, size//2 - 25)
        else:
            cx = random.randint(size//2 + 25, size - 60)
        cy = random.randint(70, size - 70)
        rx = random.randint(15, 35)
        ry = random.randint(15, 35)
        opacity = random.randint(55, 80)
        draw.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=(opacity, opacity, opacity+5))

    # Add more noise (pneumonia images are hazier)
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 5, arr.shape).astype(np.float32)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    return img


def generate_better_xray_data():
    """Generate structurally distinct synthetic X-ray images."""
    base_dir = PROJECT_ROOT / "data" / "raw" / "xray"

    # Clean existing
    import shutil
    if base_dir.exists():
        shutil.rmtree(base_dir)

    counts = {"train": 80, "val": 15, "test": 15}

    for split, n_per_class in counts.items():
        for cls in ["NORMAL", "PNEUMONIA"]:
            img_dir = base_dir / split / cls
            img_dir.mkdir(parents=True, exist_ok=True)
            for i in range(n_per_class):
                if cls == "NORMAL":
                    img = _make_normal_xray()
                else:
                    img = _make_pneumonia_xray()
                img.save(img_dir / f"synth_{cls.lower()}_{i:04d}.jpg")

    total = sum(counts.values()) * 2
    print(f"[XRAY] Generated {total} images ({counts}) -> {base_dir}")


if __name__ == "__main__":
    print("=" * 60)
    print("Generating improved synthetic datasets...")
    print("=" * 60)
    generate_better_symptom_data()
    generate_better_xray_data()
    print("\nDone! Ready to retrain.")
