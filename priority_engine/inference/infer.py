"""
NEX-CIV Multimodal Inference Module
Fuses:
1. Multilingual Text (Telugu & English NLP)
2. Computer Vision & Defect Image Analysis
3. Geospatial Zone & Sensitive Corridor Vulnerability
4. Statutory SLA & Civic Impact Meta
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd

SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent / "saved_models"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MULTIMODAL_MODEL_PATH = MODELS_DIR / "nexciv_multimodal_unified_model.pkl"
LIGHTGBM_MODEL_PATH = MODELS_DIR / "nexciv_lightgbm_priority_model.pkl"

_MULTIMODAL_PACKAGE = None
_LIGHTGBM_PACKAGE = None


def get_models():
    global _MULTIMODAL_PACKAGE, _LIGHTGBM_PACKAGE
    if _LIGHTGBM_PACKAGE is None:
        p = LIGHTGBM_MODEL_PATH if LIGHTGBM_MODEL_PATH.exists() else (SAVED_MODELS_DIR / "nexciv_lightgbm_priority_model.pkl")
        if p.exists():
            try:
                _LIGHTGBM_PACKAGE = joblib.load(p)
            except Exception as e:
                print(f"[INFERENCE] Error loading LightGBM model: {e}")

    if _LIGHTGBM_PACKAGE is None and _MULTIMODAL_PACKAGE is None:
        p = MULTIMODAL_MODEL_PATH if MULTIMODAL_MODEL_PATH.exists() else (SAVED_MODELS_DIR / "nexciv_multimodal_unified_model.pkl")
        if p.exists():
            try:
                _MULTIMODAL_PACKAGE = joblib.load(p)
            except Exception as e:
                print(f"[INFERENCE] Error loading Multimodal model: {e}")

    return _MULTIMODAL_PACKAGE, _LIGHTGBM_PACKAGE


def predict_complaint_priority(
    text: str,
    safety_risk: float = 50.0,
    public_health_risk: float = 50.0,
    public_impact: float = 50.0,
    infrastructure_criticality: float = 50.0,
    sla_urgency: float = 50.0,
    is_emergency: bool = False,
    category: str = "road",
    estimated_citizens_affected: float = 50.0,
    statutory_sla_days: float = 3.0,
    image_input: Optional[Any] = None,
    zone: Optional[str] = None,
    ward: Optional[str] = None,
    municipality: Optional[str] = "ELR",
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> Dict[str, Any]:
    """
    Runs full multimodal inference across Text, Image, Geospatial Zone, and Civic features.
    """
    mm_pkg, lgb_pkg = get_models()
    pred_priority_score = None
    pred_dept = category
    zone_type = "residential"
    vuln_multiplier = 1.0
    vis_sev = 50.0
    has_image = False

    # 1. PRIMARY: USE RETRAINED LEAK-FREE LIGHTGBM MODEL
    if lgb_pkg is not None and lgb_pkg.get("target_leakage_free"):
        try:
            model = lgb_pkg["model"]
            vec = lgb_pkg["vectorizer"]
            clean_t = text or ""
            text_vec = vec.transform([clean_t]).toarray()
            
            depts = lgb_pkg.get("departments", ["road", "drainage", "water_supply", "street_lights", "others"])
            dept_vec = np.array([[1.0 if category.lower() == d else 0.0 for d in depts]])

            t_low = clean_t.lower()
            zone_keywords = {
                "hospital": ["hospital", "clinic", "dispensary", "casualty", "icu", "trauma", "ఆసుపత్రి", "దవాఖాన"],
                "school": ["school", "college", "university", "campus", "students", "పాఠశాల", "బడి", "కళాశాల"],
                "highway": ["highway", "expressway", "flyover", "arterial", "nh-16", "nh-65", "రహదారి", "ఫ్లైఓవర్"],
                "transit": ["bus stand", "railway", "rtc", "pnbs", "బస్ స్టాండ్", "రైల్వే"]
            }
            if any(k in t_low for k in zone_keywords["hospital"]) or (zone and "hospital" in zone.lower()) or (zone and "kgh" in zone.lower()):
                zone_type = "hospital"
                vuln_multiplier = 1.50
            elif any(k in t_low for k in zone_keywords["school"]):
                zone_type = "school"
                vuln_multiplier = 1.3
            elif any(k in t_low for k in zone_keywords["highway"]):
                zone_type = "highway"
                vuln_multiplier = 1.2
            elif any(k in t_low for k in zone_keywords["transit"]):
                zone_type = "transit_hub"
                vuln_multiplier = 1.25

            zone_vec = np.array([[
                1.0 if any(k in t_low for k in zone_keywords["hospital"]) else 0.0,
                1.0 if any(k in t_low for k in zone_keywords["school"]) else 0.0,
                1.0 if any(k in t_low for k in zone_keywords["highway"]) else 0.0,
                1.0 if any(k in t_low for k in zone_keywords["transit"]) else 0.0
            ]])

            hazard_keywords = [
                "live wire", "exposed wire", "sparking", "shock", "కరెంట్ వైర్", "విద్యుత్",
                "open manhole", "manhole without cover", "మ్యాన్‌హోల్",
                "cave-in", "sinkhole", "road collapse", "కుంగిపోయింది",
                "contaminated water", "sewage in drinking water", "కలుషిత నీరు",
                "flash flood", "water entering houses", "ముంపు ప్రమాదం"
            ]
            high_risk_keywords = [
                "deep crater", "major pothole", "పెద్ద గుంత",
                "drainage overflow", "sewage overflow", "మురుగు పొంగుతోంది",
                "pipeline broken", "పైప్‌లైన్ పగిలింది",
                "all streetlights off", "total darkness", "చీకటి"
            ]
            hazard_vec = np.array([[
                1.0 if any(k in t_low for k in hazard_keywords) else 0.0,
                1.0 if any(k in t_low for k in high_risk_keywords) else 0.0
            ]])

            has_image = bool(image_input)
            proof_vec = np.array([[1.0 if has_image else 0.0]])
            X_input = np.hstack([text_vec, dept_vec, zone_vec, hazard_vec, proof_vec])
            pred_priority_score = float(model.predict(X_input)[0])
        except Exception as ex:
            print(f"[INFERENCE] LightGBM primary inference exception: {ex}")
    if mm_pkg is not None:
        try:
            from priority_engine.multimodal_fusion import (
                extract_vision_features_from_image,
                synthesize_vision_features_for_defect,
                resolve_zone_features
            )

            # Modality 1: Text
            tfidf = mm_pkg["tfidf"]
            text_vec = tfidf.transform([text or ""]).toarray()

            # Modality 2: Vision / Image
            if image_input:
                vf = extract_vision_features_from_image(image_input)
                has_image = bool(vf.get("has_image_proof", 0.0))
            else:
                vf = synthesize_vision_features_for_defect(category, 3 if is_emergency else 2)
            vis_sev = vf['visual_severity_score']
            vision_vec = np.array([[
                vf['visual_severity_score'],
                vf['edge_density'],
                vf['contrast_ratio'],
                vf['brightness_level'],
                vf['has_image_proof']
            ]])

            # Modality 3: Geospatial Zone
            zf = resolve_zone_features(
                text=text or "",
                location_name=zone,
                ward=ward,
                municipality=municipality,
                lat=lat,
                lng=lng
            )
            zone_type = zf['zone_type']
            vuln_multiplier = zf['vulnerability_multiplier']

            zone_dummies_cols = mm_pkg["zone_dummies_columns"]
            zone_vec = np.array([[1 if c == f"zone_{zone_type}" else 0 for c in zone_dummies_cols]])

            muni_dummies_cols = mm_pkg["muni_dummies_columns"]
            muni_code = zf['municipality_code']
            muni_vec = np.array([[1 if c == f"muni_{muni_code}" else 0 for c in muni_dummies_cols]])

            spatial_vec = np.column_stack([
                zone_vec,
                [[zf['vulnerability_multiplier']]],
                [[zf['latitude']]],
                [[zf['longitude']]],
                [[zf['ward_num']]],
                muni_vec
            ])

            # Modality 4: Civic Metadata
            cat_dummies_cols = mm_pkg["cat_dummies_columns"]
            cat_vec = np.array([[1 if c == f"cat_{category}" else 0 for c in cat_dummies_cols]])
            log_citizens = np.log1p(np.array([[float(estimated_citizens_affected)]]))

            civic_vec = np.column_stack([
                [[float(safety_risk)]],
                [[float(public_health_risk)]],
                log_citizens,
                [[float(infrastructure_criticality)]],
                [[float(statutory_sla_days)]],
                [[1 if is_emergency else 0]],
                cat_vec
            ])

            X_fused = np.hstack([text_vec, vision_vec, spatial_vec, civic_vec])

            # Priority prediction
            pred_priority_score = float(mm_pkg["priority_model"].predict(X_fused)[0])

            # Cadre Department prediction (without cat_dummies)
            civic_no_cat = np.column_stack([
                [[float(safety_risk)]],
                [[float(public_health_risk)]],
                log_citizens,
                [[float(infrastructure_criticality)]],
                [[float(statutory_sla_days)]],
                [[1 if is_emergency else 0]]
            ])
            X_no_cat = np.hstack([text_vec, vision_vec, spatial_vec, civic_no_cat])
            pred_dept_ml = str(mm_pkg["dept_model"].predict(X_no_cat)[0])
            pred_dept = category if (category and category in ["road", "street_lights", "drainage", "water_supply"]) else pred_dept_ml

        except Exception as e:
            print(f"[INFERENCE] Multimodal pipeline note, falling back to LightGBM text: {e}")

    # 2. LIGHTGBM PRE-TRIAGE MODEL (LEAKAGE-FREE)
    if pred_priority_score is None and lgb_pkg is not None:
        try:
            model = lgb_pkg["model"]
            if lgb_pkg.get("target_leakage_free"):
                # Clean pre-triage feature pipeline
                vec = lgb_pkg["vectorizer"]
                clean_t = text or ""
                text_vec = vec.transform([clean_t]).toarray()
                
                # Department one-hot
                depts = lgb_pkg.get("departments", ["road", "drainage", "water_supply", "street_lights", "others"])
                dept_vec = np.array([[1.0 if category.lower() == d else 0.0 for d in depts]])

                # Zone indicators
                t_low = clean_t.lower()
                zone_keywords = {
                    "hospital": ["hospital", "clinic", "dispensary", "casualty", "icu", "trauma", "ఆసుపత్రి", "దవాఖాన"],
                    "school": ["school", "college", "university", "campus", "students", "పాఠశాల", "బడి", "కళాశాల"],
                    "highway": ["highway", "expressway", "flyover", "arterial", "nh-16", "nh-65", "రహదారి", "ఫ్లైఓవర్"],
                    "transit": ["bus stand", "railway", "rtc", "pnbs", "బస్ స్టాండ్", "రైల్వే"]
                }
                zone_vec = np.array([[
                    1.0 if any(k in t_low for k in zone_keywords["hospital"]) else 0.0,
                    1.0 if any(k in t_low for k in zone_keywords["school"]) else 0.0,
                    1.0 if any(k in t_low for k in zone_keywords["highway"]) else 0.0,
                    1.0 if any(k in t_low for k in zone_keywords["transit"]) else 0.0
                ]])

                # Hazard indicators
                hazard_keywords = [
                    "live wire", "exposed wire", "sparking", "shock", "కరెంట్ వైర్", "విద్యుత్",
                    "open manhole", "manhole without cover", "మ్యాన్‌హోల్",
                    "cave-in", "sinkhole", "road collapse", "కుంగిపోయింది",
                    "contaminated water", "sewage in drinking water", "కలుషిత నీరు",
                    "flash flood", "water entering houses", "ముంపు ప్రమాదం"
                ]
                high_risk_keywords = [
                    "deep crater", "major pothole", "పెద్ద గుంత",
                    "drainage overflow", "sewage overflow", "మురుగు పొంగుతోంది",
                    "pipeline broken", "పైప్‌లైన్ పగిలింది",
                    "all streetlights off", "total darkness", "చీకటి"
                ]
                hazard_vec = np.array([[
                    1.0 if any(k in t_low for k in hazard_keywords) else 0.0,
                    1.0 if any(k in t_low for k in high_risk_keywords) else 0.0
                ]])

                proof_vec = np.array([[1.0 if image_input else 0.0]])
                X_input = np.hstack([text_vec, dept_vec, zone_vec, hazard_vec, proof_vec])
                pred_priority_score = float(model.predict(X_input)[0])
            else:
                tfidf = lgb_pkg["tfidf"]
                cat_feature_names = lgb_pkg["cat_feature_names"]
                text_vec = tfidf.transform([text or ""]).toarray()
                cat_col = f"cat_{category}"
                cat_vec = np.array([[1 if c == cat_col else 0 for c in cat_feature_names]])
                log_citizens = np.log1p(np.array([[float(estimated_citizens_affected)]]))
                tabular = np.column_stack([
                    [[float(safety_risk)]],
                    [[float(public_health_risk)]],
                    log_citizens,
                    [[float(infrastructure_criticality)]],
                    [[float(statutory_sla_days)]],
                    [[1 if is_emergency else 0]],
                    cat_vec
                ])
                X_input = np.hstack([tabular, text_vec])
                pred_priority_score = float(model.predict(X_input)[0])
        except Exception as ex:
            print(f"[INFERENCE] LightGBM inference exception: {ex}")
            pred_priority_score = 95.0 if is_emergency else 65.0

    if pred_priority_score is None:
        pred_priority_score = 95.0 if is_emergency else 65.0

    # Emergency safeguard: never allow an emergency hazard to score below 95.0
    if is_emergency:
        pred_priority_score = max(95.0, pred_priority_score)

    pred_priority_score = round(max(0.0, min(100.0, pred_priority_score)), 2)

    if pred_priority_score >= 80.0 or is_emergency:
        tier = "Critical"
    elif pred_priority_score >= 60.0:
        tier = "High"
    elif pred_priority_score >= 40.0:
        tier = "Medium"
    else:
        tier = "Low"

    return {
        "predicted_severity_level": 3 if is_emergency else 2,
        "predicted_priority_score": pred_priority_score,
        "predicted_priority_tier": tier,
        "predicted_department": pred_dept,
        "zone_classification": zone_type,
        "vulnerability_multiplier": vuln_multiplier,
        "visual_damage_severity": vis_sev,
        "has_image_proof": has_image,
        "is_emergency_override": is_emergency,
        "model_version": "3.4.0-MULTIMODAL-FUSION-PROD"
    }
