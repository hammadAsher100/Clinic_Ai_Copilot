"""
Enhanced Visualization Script using Plotly

Generates interactive and professional visualizations for the hackathon presentation.
Creates both static images (PNG) and interactive HTML files.
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc, classification_report
)
import keras

# Set up paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Suppress TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from ml.text_model.preprocess import load_raw_data as load_text_data, preprocess_and_split as preprocess_text
from ml.ann.preprocess import load_raw_data as load_ann_data, preprocess_and_split as preprocess_ann
from ml.cnn.preprocess import get_test_generator

REGISTRY_DIR = PROJECT_ROOT / "ml" / "registry"
OUTPUT_DIR = PROJECT_ROOT / "evaluation_results"
OUTPUT_DIR.mkdir(exist_ok=True)



def create_metrics_comparison_chart(cnn_metrics, ann_metrics, text_metrics):
    """Create a comparison chart of all models' metrics."""
    print("\n📊 Creating Metrics Comparison Chart...")
    
    # Prepare data
    models = []
    accuracy_vals = []
    precision_vals = []
    recall_vals = []
    f1_vals = []
    
    if cnn_metrics:
        models.append('CNN<br>(Pneumonia)')
        accuracy_vals.append(cnn_metrics['accuracy'] * 100)
        precision_vals.append(cnn_metrics['precision'] * 100)
        recall_vals.append(cnn_metrics['recall'] * 100)
        f1_vals.append(cnn_metrics['f1'] * 100)
    
    if ann_metrics:
        models.append('ANN<br>(Heart Disease)')
        accuracy_vals.append(ann_metrics['accuracy'] * 100)
        precision_vals.append(ann_metrics['precision'] * 100)
        recall_vals.append(ann_metrics['recall'] * 100)
        f1_vals.append(ann_metrics['f1'] * 100)
    
    if text_metrics:
        models.append('BiLSTM<br>(Symptoms)')
        accuracy_vals.append(text_metrics['accuracy'] * 100)
        precision_vals.append(text_metrics['precision_macro'] * 100)
        recall_vals.append(text_metrics['recall_macro'] * 100)
        f1_vals.append(text_metrics['f1_macro'] * 100)
    
    # Create grouped bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Accuracy',
        x=models,
        y=accuracy_vals,
        marker_color='#1f77b4',
        text=[f'{v:.1f}%' for v in accuracy_vals],
        textposition='outside',
    ))
    
    fig.add_trace(go.Bar(
        name='Precision',
        x=models,
        y=precision_vals,
        marker_color='#ff7f0e',
        text=[f'{v:.1f}%' for v in precision_vals],
        textposition='outside',
    ))
    
    fig.add_trace(go.Bar(
        name='Recall',
        x=models,
        y=recall_vals,
        marker_color='#2ca02c',
        text=[f'{v:.1f}%' for v in recall_vals],
        textposition='outside',
    ))
    
    fig.add_trace(go.Bar(
        name='F1-Score',
        x=models,
        y=f1_vals,
        marker_color='#d62728',
        text=[f'{v:.1f}%' for v in f1_vals],
        textposition='outside',
    ))
    
    fig.update_layout(
        title={
            'text': 'Model Performance Comparison<br><sub>All Models on Held-Out Test Sets</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Model Type',
        yaxis_title='Score (%)',
        yaxis=dict(range=[0, 110]),
        barmode='group',
        template='plotly_white',
        height=500,
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Save
    fig.write_html(str(OUTPUT_DIR / "metrics_comparison_interactive.html"))
    fig.write_image(str(OUTPUT_DIR / "metrics_comparison.png"), width=1200, height=600)
    print(f"   ✅ Saved: metrics_comparison.png")
    print(f"   ✅ Saved: metrics_comparison_interactive.html")



def create_ann_roc_plotly(y_test, y_proba):
    """Create interactive ROC curve for ANN model."""
    print("\n📈 Creating ANN ROC Curve (Plotly)...")
    
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    roc_auc_val = auc(fpr, tpr)
    
    fig = go.Figure()
    
    # ROC curve
    fig.add_trace(go.Scatter(
        x=fpr,
        y=tpr,
        mode='lines',
        name=f'ROC Curve (AUC = {roc_auc_val:.3f})',
        line=dict(color='#2ca02c', width=3),
        hovertemplate='<b>FPR</b>: %{x:.3f}<br><b>TPR</b>: %{y:.3f}<extra></extra>'
    ))
    
    # Random classifier line
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Random Classifier',
        line=dict(color='navy', width=2, dash='dash'),
        hovertemplate='<b>Random</b><extra></extra>'
    ))
    
    # Add shaded area under curve
    fig.add_trace(go.Scatter(
        x=fpr,
        y=tpr,
        fill='tozeroy',
        fillcolor='rgba(44, 160, 44, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title={
            'text': f'ANN Heart Disease Model - ROC Curve<br><sub>AUC = {roc_auc_val:.3f}</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        template='plotly_white',
        height=600,
        width=800,
        font=dict(size=14),
        hovermode='x unified',
        legend=dict(x=0.7, y=0.1)
    )
    
    fig.update_xaxes(range=[0, 1], gridcolor='lightgray')
    fig.update_yaxes(range=[0, 1.05], gridcolor='lightgray')
    
    # Save
    fig.write_html(str(OUTPUT_DIR / "ann_roc_curve_interactive.html"))
    fig.write_image(str(OUTPUT_DIR / "ann_roc_curve_plotly.png"), width=1000, height=750)
    print(f"   ✅ Saved: ann_roc_curve_plotly.png")
    print(f"   ✅ Saved: ann_roc_curve_interactive.html")



def create_ann_confusion_matrix_plotly(y_test, y_pred):
    """Create interactive confusion matrix for ANN model."""
    print("\n🎯 Creating ANN Confusion Matrix (Plotly)...")
    
    cm = confusion_matrix(y_test, y_pred)
    
    # Calculate percentages
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
    
    labels = ['No Disease', 'Disease']
    
    # Create annotations
    annotations = []
    for i in range(len(labels)):
        for j in range(len(labels)):
            annotations.append(
                dict(
                    text=f'<b>{cm[i, j]}</b><br>({cm_percent[i, j]:.1f}%)',
                    x=labels[j],
                    y=labels[i],
                    showarrow=False,
                    font=dict(size=16, color='white' if cm[i, j] > cm.max() / 2 else 'black')
                )
            )
    
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=labels,
        y=labels,
        colorscale='Greens',
        showscale=True,
        hovertemplate='<b>True</b>: %{y}<br><b>Predicted</b>: %{x}<br><b>Count</b>: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        annotations=annotations,
        title={
            'text': 'ANN Heart Disease Model - Confusion Matrix<br><sub>Test Set Performance</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Predicted Label',
        yaxis_title='True Label',
        template='plotly_white',
        height=600,
        width=700,
        font=dict(size=14)
    )
    
    fig.update_xaxes(side='bottom')
    fig.update_yaxes(autorange='reversed')
    
    # Save
    fig.write_html(str(OUTPUT_DIR / "ann_confusion_matrix_interactive.html"))
    fig.write_image(str(OUTPUT_DIR / "ann_confusion_matrix_plotly.png"), width=900, height=750)
    print(f"   ✅ Saved: ann_confusion_matrix_plotly.png")
    print(f"   ✅ Saved: ann_confusion_matrix_interactive.html")


def create_model_architecture_diagram():
    """Create a visual diagram of the system architecture."""
    print("\n🏗️  Creating System Architecture Diagram...")
    
    fig = go.Figure()
    
    # Define layers
    layers = [
        {'name': 'Frontend', 'y': 5, 'color': '#1f77b4', 'desc': 'HTML/CSS/JS'},
        {'name': 'FastAPI Backend', 'y': 4, 'color': '#ff7f0e', 'desc': 'REST API'},
        {'name': 'Inference Service', 'y': 3, 'color': '#2ca02c', 'desc': 'Model Orchestration'},
        {'name': 'ML Models', 'y': 2, 'color': '#d62728', 'desc': 'CNN | ANN | BiLSTM'},
        {'name': 'Database', 'y': 1, 'color': '#9467bd', 'desc': 'PostgreSQL'},
    ]

    
    # Add layer boxes
    for layer in layers:
        fig.add_trace(go.Scatter(
            x=[0.5],
            y=[layer['y']],
            mode='markers+text',
            marker=dict(size=100, color=layer['color'], symbol='square'),
            text=f"<b>{layer['name']}</b><br>{layer['desc']}",
            textposition='middle center',
            textfont=dict(size=12, color='white'),
            showlegend=False,
            hovertemplate=f"<b>{layer['name']}</b><br>{layer['desc']}<extra></extra>"
        ))
    
    # Add arrows
    for i in range(len(layers) - 1):
        fig.add_annotation(
            x=0.5, y=layers[i]['y'],
            ax=0.5, ay=layers[i+1]['y'],
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor='gray'
        )
    
    fig.update_layout(
        title={
            'text': 'Clinical AI Co-Pilot - System Architecture',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22}
        },
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 1]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 6]),
        template='plotly_white',
        height=700,
        width=500,
        font=dict(size=14)
    )
    
    # Save
    fig.write_html(str(OUTPUT_DIR / "architecture_diagram_interactive.html"))
    fig.write_image(str(OUTPUT_DIR / "architecture_diagram.png"), width=600, height=900)
    print(f"   ✅ Saved: architecture_diagram.png")
    print(f"   ✅ Saved: architecture_diagram_interactive.html")


def create_performance_dashboard(cnn_metrics, ann_metrics, text_metrics):
    """Create a comprehensive dashboard with multiple metrics."""
    print("\n📊 Creating Performance Dashboard...")
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Model Accuracy', 'Precision vs Recall', 
                        'F1-Score Comparison', 'Test Set Sizes'),
        specs=[[{'type': 'bar'}, {'type': 'scatter'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    models = []
    accuracy_vals = []
    precision_vals = []
    recall_vals = []
    f1_vals = []
    test_sizes = []
    
    if cnn_metrics:
        models.append('CNN')
        accuracy_vals.append(cnn_metrics['accuracy'] * 100)
        precision_vals.append(cnn_metrics['precision'] * 100)
        recall_vals.append(cnn_metrics['recall'] * 100)
        f1_vals.append(cnn_metrics['f1'] * 100)
        test_sizes.append(cnn_metrics['test_size'])
    
    if ann_metrics:
        models.append('ANN')
        accuracy_vals.append(ann_metrics['accuracy'] * 100)
        precision_vals.append(ann_metrics['precision'] * 100)
        recall_vals.append(ann_metrics['recall'] * 100)
        f1_vals.append(ann_metrics['f1'] * 100)
        test_sizes.append(ann_metrics['test_size'])
    
    if text_metrics:
        models.append('BiLSTM')
        accuracy_vals.append(text_metrics['accuracy'] * 100)
        precision_vals.append(text_metrics['precision_macro'] * 100)
        recall_vals.append(text_metrics['recall_macro'] * 100)
        f1_vals.append(text_metrics['f1_macro'] * 100)
        test_sizes.append(text_metrics['test_size'])
    
    colors = ['#1f77b4', '#2ca02c', '#9467bd']

    
    # Plot 1: Accuracy
    fig.add_trace(
        go.Bar(x=models, y=accuracy_vals, marker_color=colors,
               text=[f'{v:.1f}%' for v in accuracy_vals], textposition='outside',
               name='Accuracy', showlegend=False),
        row=1, col=1
    )
    
    # Plot 2: Precision vs Recall scatter
    for i, model in enumerate(models):
        fig.add_trace(
            go.Scatter(x=[precision_vals[i]], y=[recall_vals[i]], mode='markers+text',
                      marker=dict(size=20, color=colors[i]),
                      text=model, textposition='top center',
                      name=model, showlegend=False),
            row=1, col=2
        )
    
    # Plot 3: F1-Score
    fig.add_trace(
        go.Bar(x=models, y=f1_vals, marker_color=colors,
               text=[f'{v:.1f}%' for v in f1_vals], textposition='outside',
               name='F1-Score', showlegend=False),
        row=2, col=1
    )
    
    # Plot 4: Test Set Sizes
    fig.add_trace(
        go.Bar(x=models, y=test_sizes, marker_color=colors,
               text=[f'{v}' for v in test_sizes], textposition='outside',
               name='Test Size', showlegend=False),
        row=2, col=2
    )
    
    # Update axes
    fig.update_yaxes(title_text="Accuracy (%)", row=1, col=1, range=[0, 110])
    fig.update_xaxes(title_text="Precision (%)", row=1, col=2)
    fig.update_yaxes(title_text="Recall (%)", row=1, col=2)
    fig.update_yaxes(title_text="F1-Score (%)", row=2, col=1, range=[0, 110])
    fig.update_xaxes(title_text="Model", row=2, col=2)
    fig.update_yaxes(title_text="Samples", row=2, col=2)
    
    fig.update_layout(
        title={
            'text': 'Clinical AI Co-Pilot - Performance Dashboard<br><sub>Comprehensive Model Evaluation</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22}
        },
        template='plotly_white',
        height=800,
        width=1400,
        font=dict(size=12)
    )
    
    # Save
    fig.write_html(str(OUTPUT_DIR / "performance_dashboard_interactive.html"))
    fig.write_image(str(OUTPUT_DIR / "performance_dashboard.png"), width=1600, height=900)
    print(f"   ✅ Saved: performance_dashboard.png")
    print(f"   ✅ Saved: performance_dashboard_interactive.html")


def create_feature_importance_mock():
    """Create a mock SHAP-style feature importance chart."""
    print("\n🔍 Creating Feature Importance Visualization...")
    
    # Mock feature importance (based on typical heart disease factors)
    features = ['Cholesterol', 'Age', 'Max Heart Rate', 'ST Depression', 
                'Chest Pain Type', 'Blood Pressure', 'Exercise Angina']
    importance = [0.45, 0.32, -0.28, 0.25, 0.22, 0.18, 0.15]
    colors_list = ['red' if x > 0 else 'blue' for x in importance]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=features,
        x=importance,
        orientation='h',
        marker_color=colors_list,
        text=[f'{abs(v):.2f}' for v in importance],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Impact: %{x:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Heart Disease Model - Feature Importance<br><sub>SHAP Values (Example)</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Impact on Prediction',
        yaxis_title='Clinical Feature',
        template='plotly_white',
        height=500,
        width=900,
        font=dict(size=14)
    )
    
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="gray")
    
    # Add annotations
    fig.add_annotation(
        x=0.3, y=6.5,
        text="← Increases Risk",
        showarrow=False,
        font=dict(size=12, color="red")
    )
    
    fig.add_annotation(
        x=-0.2, y=6.5,
        text="Decreases Risk →",
        showarrow=False,
        font=dict(size=12, color="blue")
    )
    
    # Save
    fig.write_html(str(OUTPUT_DIR / "feature_importance_interactive.html"))
    fig.write_image(str(OUTPUT_DIR / "feature_importance.png"), width=1100, height=600)
    print(f"   ✅ Saved: feature_importance.png")
    print(f"   ✅ Saved: feature_importance_interactive.html")



def load_models_and_generate():
    """Load models, generate predictions, and create all visualizations."""
    
    print("\n" + "="*80)
    print("ENHANCED PLOTLY VISUALIZATION GENERATOR")
    print("="*80)
    
    # Load ANN model and data
    print("\n📦 Loading ANN Model and Data...")
    ann_model = keras.models.load_model(str(REGISTRY_DIR / "ann_heart_risk.h5"))
    df = load_ann_data(str(PROJECT_ROOT / "data" / "raw" / "tabular" / "heart.csv"))
    X_train, X_test, y_train, y_test, feature_names = preprocess_ann(df, save_artifacts=False)
    
    print(f"   Test samples: {len(X_test)}")
    
    # Get predictions
    y_proba = ann_model.predict(X_test, verbose=0).ravel()
    y_pred = (y_proba >= 0.5).astype(int)
    
    # Compute metrics for all models
    cnn_metrics = None
    ann_metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(auc(*roc_curve(y_test, y_proba)[:2])),
        "test_size": len(X_test)
    }
    
    text_metrics = None
    
    # Try to load other models
    try:
        print("\n📦 Loading CNN Model...")
        cnn_model = keras.models.load_model(str(REGISTRY_DIR / "cnn_pneumonia.h5"))
        test_gen = get_test_generator(str(PROJECT_ROOT / "data" / "raw" / "xray"))
        test_gen.reset()
        y_proba_cnn = cnn_model.predict(test_gen, verbose=0).ravel()
        y_true_cnn = test_gen.classes
        y_pred_cnn = (y_proba_cnn >= 0.5).astype(int)
        
        cnn_metrics = {
            "accuracy": float(accuracy_score(y_true_cnn, y_pred_cnn)),
            "precision": float(precision_score(y_true_cnn, y_pred_cnn, zero_division=0)),
            "recall": float(recall_score(y_true_cnn, y_pred_cnn, zero_division=0)),
            "f1": float(f1_score(y_true_cnn, y_pred_cnn, zero_division=0)),
            "test_size": len(y_true_cnn)
        }
        print(f"   ✅ CNN loaded successfully")
    except Exception as e:
        print(f"   ⚠️  CNN not available: {e}")
    
    try:
        print("\n📦 Loading BiLSTM Model...")
        text_model = keras.models.load_model(str(REGISTRY_DIR / "text_triage.h5"))
        df_text = load_text_data(str(PROJECT_ROOT / "data" / "raw" / "text" / "Symptom2Disease.csv"))
        X_train_t, X_test_t, y_train_t, y_test_t, num_classes, class_names = preprocess_text(df_text, save_artifacts=False)
        
        y_proba_text = text_model.predict(X_test_t, verbose=0)
        y_pred_text = np.argmax(y_proba_text, axis=1)
        
        text_metrics = {
            "accuracy": float(accuracy_score(y_test_t, y_pred_text)),
            "precision_macro": float(precision_score(y_test_t, y_pred_text, average='macro', zero_division=0)),
            "recall_macro": float(recall_score(y_test_t, y_pred_text, average='macro', zero_division=0)),
            "f1_macro": float(f1_score(y_test_t, y_pred_text, average='macro', zero_division=0)),
            "test_size": len(X_test_t)
        }
        print(f"   ✅ BiLSTM loaded successfully")
    except Exception as e:
        print(f"   ⚠️  BiLSTM not available: {e}")
    
    # Generate all visualizations
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    create_ann_roc_plotly(y_test, y_proba)
    create_ann_confusion_matrix_plotly(y_test, y_pred)
    create_metrics_comparison_chart(cnn_metrics, ann_metrics, text_metrics)
    create_performance_dashboard(cnn_metrics, ann_metrics, text_metrics)
    create_feature_importance_mock()
    create_model_architecture_diagram()
    
    print("\n" + "="*80)
    print("✅ ALL VISUALIZATIONS GENERATED")
    print("="*80)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("\nGenerated files:")
    print("  - metrics_comparison.png (& .html)")
    print("  - ann_roc_curve_plotly.png (& .html)")
    print("  - ann_confusion_matrix_plotly.png (& .html)")
    print("  - performance_dashboard.png (& .html)")
    print("  - feature_importance.png (& .html)")
    print("  - architecture_diagram.png (& .html)")
    print("\n💡 Tip: Open .html files in browser for interactive exploration!")
    print("\n")


if __name__ == "__main__":
    load_models_and_generate()
