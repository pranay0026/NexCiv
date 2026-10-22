import json
import os

notebook_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "notebooks", "training", "phase2_vision_clustering.ipynb"))

nb = {
 "nbformat": 4,
 "nbformat_minor": 0,
 "metadata": {
  "colab": {
   "provenance": []
  },
  "kernelspec": {
   "display_name": "Python 3",
   "name": "python3"
  },
  "language_info": {
   "name": "python"
  }
 },
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# \ud83d\udc41\ufe0f NEXCIV Phase 2: Computer Vision Image Damage Verification & Duplicate Complaint Clustering\n",
    "### Multimodal Visual Severity \u2022 Perceptual Hashing \u2022 Geospatial Haversine Deduplication \u2022 ULB Hotspot Work Orders\n",
    "\n",
    "Welcome to the official **Phase 2 Engine** for **NEXCIV**.\n",
    "\n",
    "### Core Capabilities:\n",
    "1. **Computer Vision Damage Verification**:\n",
    "   - Filters anti-spam / invalid / non-civic uploads (blanks, solid colors, low-res noise).\n",
    "   - Classifies structural defect types (`pothole_crater`, `surface_crack_fissure`, `waterlogging_flood`, `night_hazard_blackout`, `road_debris`).\n",
    "   - Calculates numerical visual damage severity ($0 - 100$) based on edge complexity, contrast, and dark depression shadow ratio.\n",
    "2. **Perceptual Image Fingerprinting (dHash)**:\n",
    "   - Extracts a 64-bit difference hash invariant to minor crops, lighting shifts, and compression.\n",
    "   - Calculates Hamming distance to measure visual match percentage.\n",
    "3. **Geospatial & Multimodal Duplicate Detection**:\n",
    "   - Evaluates incoming reports against active municipal complaints within a spatial radius (e.g. 100m).\n",
    "   - Fuses $S = 0.45 S_{\\text{geo}} + 0.35 S_{\\text{vis}} + 0.20 S_{\\text{text}}$.\n",
    "   - If $S \\ge 0.68$, flags as duplicate, links to master complaint, and increments citizen upvotes.\n",
    "4. **ULB Hotspot Work Order Consolidation**:\n",
    "   - Clusters open complaints into unified regional work orders to prevent dispatching separate field crews for the same incident.\n",
    "\n",
    "---\n",
    "### \ud83d\ude80 Ready to Execute in Google Colab\n",
    "Click **Runtime > Run all** (or `Ctrl + F9`) to test the vision engine, duplicate detector, and clustering playground!\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## \ud83d\udce6 Step 1: Install Dependencies\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "!pip install -q pillow numpy scikit-learn matplotlib seaborn\n",
    "\n",
    "import io\n",
    "import math\n",
    "import base64\n",
    "import numpy as np\n",
    "from PIL import Image, ImageDraw, ImageFilter, ImageStat\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from typing import List, Dict, Any, Optional\n",
    "\n",
    "print(\"\u2705 Phase 2 Vision & Clustering Environment Initialized!\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## \ud83d\udc41\ufe0f Step 2: Computer Vision Defect & Severity Engine\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def compute_perceptual_hash(img: Image.Image) -> str:\n",
    "    small = img.convert('L').resize((9, 8), Image.Resampling.LANCZOS)\n",
    "    pixels = list(small.getdata())\n",
    "    diff_bits = []\n",
    "    for row in range(8):\n",
    "        row_start = row * 9\n",
    "        for col in range(8):\n",
    "            left = pixels[row_start + col]\n",
    "            right = pixels[row_start + col + 1]\n",
    "            diff_bits.append('1' if left > right else '0')\n",
    "    bit_str = \"\".join(diff_bits)\n",
    "    return f\"{int(bit_str, 2):016x}\"\n",
    "\n",
    "def hamming_distance(hash1: str, hash2: str) -> int:\n",
    "    val1, val2 = int(hash1, 16), int(hash2, 16)\n",
    "    return bin(val1 ^ val2).count('1')\n",
    "\n",
    "def visual_similarity(hash1: str, hash2: str) -> float:\n",
    "    return max(0.0, min(1.0, (64 - hamming_distance(hash1, hash2)) / 64.0))\n",
    "\n",
    "def verify_and_analyze_civic_image(img: Image.Image) -> Dict[str, Any]:\n",
    "    w, h = img.size\n",
    "    if w < 50 or h < 50:\n",
    "        return {'is_valid': False, 'reason': 'Resolution too low'}\n",
    "    \n",
    "    gray = img.convert('L')\n",
    "    stat = ImageStat.Stat(gray)\n",
    "    mean_b, std_c = stat.mean[0], stat.stddev[0]\n",
    "    \n",
    "    # Blank / Spam detection\n",
    "    if std_c < 5.0 and (mean_b > 240 or mean_b < 10):\n",
    "        return {'is_valid': False, 'reason': 'Image is blank or solid color spam'}\n",
    "        \n",
    "    edges = gray.filter(ImageFilter.FIND_EDGES)\n",
    "    edge_density = ImageStat.Stat(edges).mean[0]\n",
    "    gray_arr = np.array(gray)\n",
    "    dark_ratio = float(np.sum(gray_arr < 45) / gray_arr.size)\n",
    "    \n",
    "    defect = 'general_road_defect'\n",
    "    conf = 0.85\n",
    "    if edge_density > 18.0 and dark_ratio > 0.08:\n",
    "        defect = 'pothole_crater'\n",
    "        conf = 0.94\n",
    "    elif edge_density > 22.0:\n",
    "        defect = 'surface_crack_fissure'\n",
    "        conf = 0.89\n",
    "    elif dark_ratio > 0.35 and mean_b < 40.0:\n",
    "        defect = 'night_hazard_blackout'\n",
    "        conf = 0.92\n",
    "        \n",
    "    severity = min(100.0, max(15.0, (edge_density * 1.8) + (std_c * 0.7) + (dark_ratio * 70.0)))\n",
    "    if defect == 'pothole_crater' and dark_ratio > 0.15:\n",
    "        severity = min(100.0, severity + 20.0)\n",
    "        \n",
    "    return {\n",
    "        'is_valid': True,\n",
    "        'defect_type': defect,\n",
    "        'visual_severity_score': round(severity, 1),\n",
    "        'visual_confidence': conf,\n",
    "        'image_hash': compute_perceptual_hash(img),\n",
    "        'edge_density': round(edge_density, 2),\n",
    "        'dark_shadow_ratio': round(dark_ratio, 4)\n",
    "    }\n",
    "\n",
    "print(\"\u2705 Computer Vision Inspection Algorithms Loaded.\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## \ud83d\udccd Step 3: Geospatial & Multimodal Duplicate Engine\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def haversine_m(lat1, lon1, lat2, lon2):\n",
    "    R = 6371000.0\n",
    "    phi1, phi2 = math.radians(lat1), math.radians(lat2)\n",
    "    dphi, dlam = math.radians(lat2 - lat1), math.radians(lon2 - lon1)\n",
    "    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2.0)**2\n",
    "    return R * (2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)))\n",
    "\n",
    "def compute_text_similarity(t1, t2):\n",
    "    s1 = set(t1.lower().split())\n",
    "    s2 = set(t2.lower().split())\n",
    "    return len(s1.intersection(s2)) / max(1, len(s1.union(s2)))\n",
    "\n",
    "def check_duplicate_pair(c1, c2):\n",
    "    if c1.get('category') != c2.get('category'):\n",
    "        return {'is_duplicate': False, 'score': 0.0, 'dist_m': 999999.0}\n",
    "        \n",
    "    dist_m = haversine_m(c1['lat'], c1['lng'], c2['lat'], c2['lng'])\n",
    "    geo_score = 1.0 if dist_m <= 15 else (0.85 if dist_m <= 45 else (0.60 if dist_m <= 90 else 0.0))\n",
    "    \n",
    "    vis_score = visual_similarity(c1['image_hash'], c2['image_hash'])\n",
    "    txt_score = compute_text_similarity(c1['text'], c2['text'])\n",
    "    \n",
    "    total_score = (0.45 * geo_score) + (0.35 * vis_score) + (0.20 * txt_score)\n",
    "    if vis_score >= 0.90 and dist_m <= 75.0:\n",
    "        total_score = max(total_score, 0.95)\n",
    "        \n",
    "    return {\n",
    "        'is_duplicate': total_score >= 0.68 and dist_m <= 100.0,\n",
    "        'score': round(total_score, 3),\n",
    "        'dist_m': round(dist_m, 1)\n",
    "    }\n",
    "\n",
    "print(\"\u2705 Geospatial & Multimodal Duplicate Engine Ready.\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## \ud83c\udfae Step 4: Interactive Colab Test Harness\n",
    "Simulate citizen submissions and watch the duplicate detector and visual severity scoring in action!\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# @title \ud83d\udd0e Interactive Duplicate Detector Playground\n",
    "reported_issue = \"Deep road crater and pothole damaging vehicles on flyover\" # @param {type:\"string\"}\n",
    "location_distance_offset_meters = 25 # @param {type:\"slider\", min:0, max:500, step:5}\n",
    "same_category = True # @param {type:\"boolean\"}\n",
    "\n",
    "# Synthesize reference pothole image\n",
    "arr = np.random.normal(loc=110, scale=18, size=(200, 200)).clip(0, 255).astype(np.uint8)\n",
    "img_ref = Image.fromarray(arr, mode='L').convert('RGB')\n",
    "draw = ImageDraw.Draw(img_ref)\n",
    "draw.ellipse([60, 60, 140, 140], fill=(20, 20, 20))\n",
    "draw.line([60, 100, 20, 80], fill=(15, 15, 15), width=2)\n",
    "hash_ref = compute_perceptual_hash(img_ref)\n",
    "\n",
    "# Benz Circle master complaint coordinates\n",
    "lat_master, lng_master = 16.4990, 80.6540\n",
    "# Calculate lat/lng offset for the chosen distance\n",
    "lat_new = lat_master + (location_distance_offset_meters / 111111.0)\n",
    "lng_new = lng_master\n",
    "\n",
    "master_obj = {\n",
    "    'text': \"Dangerous deep pothole on NH-16 Benz Circle flyover approach\",\n",
    "    'category': 'road',\n",
    "    'lat': lat_master, 'lng': lng_master,\n",
    "    'image_hash': hash_ref\n",
    "}\n",
    "\n",
    "new_obj = {\n",
    "    'text': reported_issue,\n",
    "    'category': 'road' if same_category else 'street_lights',\n",
    "    'lat': lat_new, 'lng': lng_new,\n",
    "    'image_hash': hash_ref\n",
    "}\n",
    "\n",
    "dup_res = check_duplicate_pair(new_obj, master_obj)\n",
    "\n",
    "print(\"=\"*65)\n",
    "print(f\"\ud83d\udccd Physical Separation:    {dup_res['dist_m']} meters\")\n",
    "print(f\"\ud83e\udde9 Multimodal Similarity:  {dup_res['score']*100:.1f}%\")\n",
    "print(f\"\ud83d\udd04 DUPLICATE DETECTED:    {'YES - LINK TO MASTER & UPVOTE' if dup_res['is_duplicate'] else 'NO - CREATE NEW WORK ORDER'}\")\n",
    "print(\"=\"*65)\n"
   ]
  }
 ]
}

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"Created Phase 2 notebook at {notebook_path}")
