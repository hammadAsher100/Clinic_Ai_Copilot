"""
LLM service — calls Groq API for clinical narrative generation.

╔══════════════════════════════════════════════════════════════════════╗
║  IMPORTANT: This service performs REASONING / SUMMARIZATION ONLY.  ║
║  It is NOT the predictive engine.  All diagnostic predictions come  ║
║  from the dedicated CNN, ANN, and BiLSTM models in ml/.            ║
║  The LLM receives already-computed structured outputs and produces  ║
║  a plain-language clinical narrative for the report.                ║
╚══════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from api.core.config import settings

logger = logging.getLogger("api")

SYSTEM_PROMPT = """You are a clinical summarization assistant integrated into a decision-support co-pilot.

Your role is STRICTLY limited to:
1. Summarizing structured prediction outputs from dedicated ML models (CNN, ANN, BiLSTM)
2. Writing plain-language clinical narratives for medical reports
3. Highlighting key findings and risk factors

You are NOT a diagnostic engine. The predictions you receive were produced by:
- CNN (MobileNetV2): Chest X-ray pneumonia detection
- ANN: Heart disease risk assessment from clinical features
- BiLSTM: Symptom-to-condition classification

Never override, re-diagnose, or contradict the model outputs. Your job is to translate
them into a coherent narrative that a clinician can review, edit, and approve."""


async def generate_narrative(
    image_result: Optional[dict] = None,
    tabular_result: Optional[dict] = None,
    text_result: Optional[dict] = None,
    patient_info: Optional[dict] = None,
) -> str:
    """Generate a clinical narrative from structured model outputs.

    Parameters
    ----------
    image_result : dict, optional
        CNN output: {prediction, confidence, gradcam_path}
    tabular_result : dict, optional
        ANN output: {prediction, confidence, shap_values}
    text_result : dict, optional
        BiLSTM output: {condition, confidence, top_3}
    patient_info : dict, optional
        Basic patient demographics

    Returns
    -------
    str — plain-language clinical narrative.
    """
    # Build the structured findings prompt
    findings = []

    if patient_info:
        findings.append(f"**Patient**: {patient_info.get('name', 'Anonymous')}, "
                        f"Age: {patient_info.get('age', 'N/A')}, "
                        f"Sex: {patient_info.get('sex', 'N/A')}")

    if image_result:
        findings.append(
            f"**Chest X-Ray Analysis (CNN — MobileNetV2)**:\n"
            f"  - Prediction: {image_result.get('prediction', 'N/A')}\n"
            f"  - Confidence: {image_result.get('confidence', 0):.1%}\n"
            f"  - Grad-CAM heatmap generated: {'Yes' if image_result.get('gradcam_path') else 'No'}"
        )

    if tabular_result:
        shap_summary = ""
        if tabular_result.get("shap_values"):
            top_features = sorted(
                tabular_result["shap_values"].items(),
                key=lambda x: abs(x[1]), reverse=True,
            )[:5]
            shap_summary = "\n  - Top contributing features: " + ", ".join(
                f"{k} ({v:+.3f})" for k, v in top_features
            )

        findings.append(
            f"**Heart Disease Risk Assessment (ANN)**:\n"
            f"  - Prediction: {tabular_result.get('prediction', 'N/A')}\n"
            f"  - Confidence: {tabular_result.get('confidence', 0):.1%}"
            f"{shap_summary}"
        )

    if text_result:
        top3_str = ""
        if text_result.get("top_3"):
            top3_str = "\n  - Differential: " + ", ".join(
                f"{d['condition']} ({d['confidence']:.1%})"
                for d in text_result["top_3"]
            )

        findings.append(
            f"**Symptom Classification (BiLSTM)**:\n"
            f"  - Primary Condition: {text_result.get('condition', 'N/A')}\n"
            f"  - Confidence: {text_result.get('confidence', 0):.1%}"
            f"{top3_str}"
        )

    if not findings:
        return "No model predictions available to summarize."

    user_prompt = (
        "Based on the following structured model outputs from our clinical AI co-pilot, "
        "write a concise clinical narrative summary suitable for a medical report. "
        "Include key findings, risk factors, and any recommendations for the reviewing clinician.\n\n"
        + "\n\n".join(findings)
    )

    # ── Call Groq API ────────────────────────────────────────────────────
    if not settings.groq_api_key:
        logger.warning("Groq API key not configured — returning template narrative")
        return _fallback_narrative(image_result, tabular_result, text_result)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.groq_api_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.groq_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 800,
                },
            )
            response.raise_for_status()
            data = response.json()
            narrative = data["choices"][0]["message"]["content"]
            logger.info("LLM narrative generated successfully (%d chars)", len(narrative))
            return narrative

    except httpx.HTTPStatusError as e:
        logger.error("Groq API HTTP error: %s", e)
        return _fallback_narrative(image_result, tabular_result, text_result)
    except httpx.TimeoutException:
        logger.error("Groq API request timed out")
        return _fallback_narrative(image_result, tabular_result, text_result)
    except Exception as e:
        logger.error("Unexpected LLM error: %s", e)
        return _fallback_narrative(image_result, tabular_result, text_result)


def _fallback_narrative(
    image_result: Optional[dict] = None,
    tabular_result: Optional[dict] = None,
    text_result: Optional[dict] = None,
) -> str:
    """Generate a template-based narrative when the LLM API is unavailable."""
    parts = ["## Clinical AI Co-Pilot — Summary Report\n"]

    if image_result:
        parts.append(
            f"**Chest X-Ray Analysis**: The CNN model (MobileNetV2) classified the chest X-ray as "
            f"**{image_result.get('prediction', 'N/A')}** with a confidence of "
            f"{image_result.get('confidence', 0):.1%}. "
            f"A Grad-CAM heatmap has been generated to highlight the regions of interest.\n"
        )

    if tabular_result:
        parts.append(
            f"**Heart Disease Risk Assessment**: Based on the clinical features provided, "
            f"the ANN model assessed the patient's risk as "
            f"**{tabular_result.get('prediction', 'N/A')}** with a confidence of "
            f"{tabular_result.get('confidence', 0):.1%}. "
            f"SHAP analysis has been performed to identify key contributing factors.\n"
        )

    if text_result:
        parts.append(
            f"**Symptom Classification**: Based on the reported symptoms, the BiLSTM model "
            f"identified **{text_result.get('condition', 'N/A')}** as the most likely condition "
            f"with a confidence of {text_result.get('confidence', 0):.1%}.\n"
        )

    parts.append(
        "\n*Note: This summary was generated from a template because the LLM API was "
        "unavailable. All predictions are from dedicated deep-learning models, not LLM-generated.*"
    )

    return "\n".join(parts)
