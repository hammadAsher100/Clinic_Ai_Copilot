@echo off
echo Adding model files to git...
git add -f ml/registry/cnn_pneumonia.h5
git add -f ml/registry/ann_heart_risk.h5
git add -f ml/registry/text_triage.h5
git add -f ml/registry/ann_feature_names.pkl
git add -f ml/registry/ann_num_indices.pkl
git add -f ml/registry/ann_scaler.pkl
git add -f ml/registry/text_label_encoder.pkl
git add -f ml/registry/tokenizer.pkl
git add -f ml/registry/.gitkeep
echo Done! Check status with: git status
