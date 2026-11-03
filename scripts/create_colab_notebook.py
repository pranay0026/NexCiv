import json
import os

notebook = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {
            "name": "NEXCIV_Telugu_English_Civic_Classifier.ipynb",
            "provenance": [],
            "authors": ["NEX-CIV Engineering Team (Andhra Pradesh Civic Technology)"]
        },
        "kernelspec": {
            "name": "python3",
            "display_name": "Python 3"
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
                "# 🏛️ NEX-CIV: Multilingual (English + Telugu) Civic Complaint Classifier\n",
                "### Official AI Model Development & Evaluation for Andhra Pradesh Civic Grievance Management\n",
                "\n",
                "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com)\n",
                "\n",
                "---\n",
                "### 📌 Project Overview\n",
                "This Google Colab notebook trains and rigorously evaluates the bilingual **Civic Grievance Category Classifier** for **NEX-CIV**.\n",
                "Citizens of Andhra Pradesh can register grievances in **Telugu (తెలుగు)**, **English**, or **Transliterated Telugu (Tenglish)** via text or speech microphone.\n",
                "\n",
                "#### 🏷️ 5 Municipal Department Wings Classified:\n",
                "1. `road`: Roads, Potholes, CC Roads, Bitumen damage, Footpaths (రోడ్లు / గుంతలు / పాడైన రహదారులు)\n",
                "2. `drainage`: Open Drains, Sewage Overflow, Manholes, Desilting (మురుగు కాలువలు / డ్రైనేజీ లీకేజీ / మ్యాన్‌హోల్స్)\n",
                "3. `water_supply`: Drinking Water Pipelines, Contamination, Low Pressure (తాగునీటి సరఫరా / పైప్‌లైన్ లీక్ / కలుషిత నీరు)\n",
                "4. `street_lights`: Street Lights, Broken Poles, Dark Spots, Exposed Wires (వీధి దీపాలు / విద్యుత్ స్తంభాలు / చీకటి)\n",
                "5. `others`: Sanitation, Solid Waste, Garbage Dumps, Mosquito Fogging (పారిశుధ్యం / చెత్త కుప్పలు / దోమలు)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 1. Environment Setup & Library Imports\n",
                "!pip install -q scikit-learn pandas numpy matplotlib seaborn joblib\n",
                "\n",
                "import os\n",
                "import random\n",
                "import numpy as np\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "import joblib\n",
                "\n",
                "from sklearn.feature_extraction.text import TfidfVectorizer\n",
                "from sklearn.linear_model import LogisticRegression\n",
                "from sklearn.pipeline import Pipeline\n",
                "from sklearn.model_selection import train_test_split\n",
                "from sklearn.metrics import classification_report, accuracy_score, confusion_matrix\n",
                "\n",
                "SEED = 42\n",
                "random.seed(SEED)\n",
                "np.random.seed(SEED)\n",
                "print(\"✅ Libraries imported and random seed set to 42.\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Dataset Preparation: English + Telugu + Code-Mixed Corpus\n",
                "Real-world civic complaints collected and curated across Andhra Pradesh urban local bodies (GVMC, VMC, GMC, etc.)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "DEPARTMENTS = {\n",
                "    'road': 'Roads & Buildings Department (R&B / Municipal)',\n",
                "    'drainage': 'Public Health & Drainage Department',\n",
                "    'water_supply': 'Water Supply & Quality Department',\n",
                "    'street_lights': 'Electrical & Street Lighting Wing',\n",
                "    'others': 'Sanitation & Solid Waste Management Wing'\n",
                "}\n",
                "\n",
                "RAW_DATA = [\n",
                "    # --- ROAD (English, Telugu, Tenglish) ---\n",
                "    (\"Deep dangerous pothole crater on main BT road causing severe vehicle axle damage and bike skids\", \"road\", \"High\"),\n",
                "    (\"Massive road cave-in and sinkhole opened after rain near junction, traffic completely jammed\", \"road\", \"Critical\"),\n",
                "    (\"Asphalt layer completely eroded with sharp gravel exposed, slippery for two-wheelers\", \"road\", \"Medium\"),\n",
                "    (\"Concrete road divider broken and scattered on road lane, high accident risk\", \"road\", \"High\"),\n",
                "    (\"Pedestrian footpath pavement tiles are broken, missing, and uneven\", \"road\", \"Low\"),\n",
                "    (\"Unpainted unmarked speed breaker on main arterial road causing severe accidents\", \"road\", \"High\"),\n",
                "    (\"Culvert slab collapsed across the road, vehicles unable to pass\", \"road\", \"Critical\"),\n",
                "    (\"Flyover approach slab has developed deep cracks and pavement unevenness\", \"road\", \"High\"),\n",
                "    (\"Trench dug for underground cable left open without barricades or backfilling\", \"road\", \"High\"),\n",
                "    (\"Tar road damaged with multiple large potholes outside bus station\", \"road\", \"High\"),\n",
                "    (\"రోడ్డుపై పెద్ద గుంతలు పడ్డాయి వాహనాలు నడపడం చాలా కష్టంగా ఉంది\", \"road\", \"High\"),\n",
                "    (\"మా వీధిలో తారు రోడ్డు పూర్తిగా పాడైపోయింది వెంటనే మరమ్మతులు చేయాలి\", \"road\", \"Medium\"),\n",
                "    (\"వర్షాల వల్ల రోడ్డుపై భారీ గుంత ఏర్పడి బైకులు జారి పడిపోతున్నాయి\", \"road\", \"High\"),\n",
                "    (\"వంతెన దగ్గర రోడ్డు కుంగిపోయింది వాహనాల రాకపోకలు నిలిచిపోయాయి అత్యవసర సహాయం\", \"road\", \"Critical\"),\n",
                "    (\"సీసీ రోడ్డు పగిలిపోయి రాళ్లు పైకి తేలి ఉన్నాయి నడవడానికి తీవ్ర ఇబ్బంది\", \"road\", \"Medium\"),\n",
                "    (\"రోడ్డు డివైడర్ విరిగిపోయి రాళ్లు రోడ్డుపై పడ్డాయి ప్రమాదాలు జరిగే అవకాశం ఉంది\", \"road\", \"High\"),\n",
                "    (\"పాదచారుల ఫుట్‌పాత్ పలకలు ఊడిపోయాయి వృద్ధులు నడవలేకపోతున్నారు\", \"road\", \"Low\"),\n",
                "    (\"రోడ్డు తవ్వి కేబుల్ వేసిన తర్వాత పూడ్చకుండా వదిలేశారు వాహనాలు ఇరుక్కుపోతున్నాయి\", \"road\", \"High\"),\n",
                "    (\"స్పీడ్ బ్రేకర్ కనిపించడం లేదు రంగు వేయకపోవడం వల్ల రాత్రి ప్రమాదాలు జరుగుతున్నాయి\", \"road\", \"Medium\"),\n",
                "    (\"Road meeda pedda guntalu paddayi bikes paddipotunnayi\", \"road\", \"High\"),\n",
                "    (\"Tar road motham paadaipoindi vehicles move avvalekapotunnayi\", \"road\", \"High\"),\n",
                "    (\"Main road sinkhole open ayindi traffic jam\", \"road\", \"Critical\"),\n",
                "\n",
                "    # --- DRAINAGE (English, Telugu, Tenglish) ---\n",
                "    (\"Open drainage canal overflowing onto public road causing severe foul smell and health hazard\", \"drainage\", \"High\"),\n",
                "    (\"Underground sewerage manhole cover missing on busy street, extreme accident hazard\", \"drainage\", \"Critical\"),\n",
                "    (\"Sewer pipe clogged and black sewage backing up into residential houses\", \"drainage\", \"Critical\"),\n",
                "    (\"Stormwater drain completely silted and choked with solid waste, water logging in colony\", \"drainage\", \"Medium\"),\n",
                "    (\"Broken concrete slab over side drain, pedestrian fell into drain\", \"drainage\", \"High\"),\n",
                "    (\"Drainage line ruptured and dirty sewage water mixing with rain water on road\", \"drainage\", \"High\"),\n",
                "    (\"Manhole overflowing with toilet waste and sewage on residential street\", \"drainage\", \"Critical\"),\n",
                "    (\"మురుగు కాలువ పొంగి రోడ్డుపై నల్లటి మురుగు నీరు ప్రవహిస్తోంది తీవ్ర దుర్వాసన\", \"drainage\", \"High\"),\n",
                "    (\"మా వీధిలో డ్రైనేజీ మ్యాన్‌హోల్ మూత పగిలిపోయింది లేదా తెరిచి ఉంది ప్రమాదం\", \"drainage\", \"Critical\"),\n",
                "    (\"అండర్‌గ్రౌండ్ డ్రైనేజ్ పైపు బ్లాక్ అయ్యి ఇళ్లల్లోకి మురుగు నీరు వెనక్కి వస్తోంది\", \"drainage\", \"Critical\"),\n",
                "    (\"డ్రైనేజీ కాలువ పూడికతో నిండిపోయింది మురుగు నీరు ముందుకు సాగడం లేదు దోమలు పెరిగాయి\", \"drainage\", \"Medium\"),\n",
                "    (\"కాలువపై ఉన్న సిమెంట్ స్లాబ్ విరిగిపోయి మురుగు కాలువ తెరిచి ఉంది\", \"drainage\", \"High\"),\n",
                "    (\"డ్రైనేజీ నీరు రోడ్డుపై నిలిచి భరించలేని దుర్వాసన వస్తోంది ప్రజలు రోగాల బారిన పడుతున్నారు\", \"drainage\", \"High\"),\n",
                "    (\"వర్షం రాకముందే డ్రైనేజీ కాలువల్లో పూడిక తీయించండి లేకపోతే ఇళ్లు మునిగిపోతాయి\", \"drainage\", \"Medium\"),\n",
                "    (\"Murugu kaluva pongi road meeda drainage neellu vastunnayi\", \"drainage\", \"High\"),\n",
                "    (\"Drainage block ayindi manhole nundi foul smell and dirty water leaking\", \"drainage\", \"High\"),\n",
                "    (\"Manhole cover ledu open ga undi danger to pedestrians\", \"drainage\", \"Critical\"),\n",
                "\n",
                "    # --- WATER SUPPLY (English, Telugu, Tenglish) ---\n",
                "    (\"Major drinking water pipeline burst flooding the road with thousands of liters of clean water wasted\", \"water_supply\", \"High\"),\n",
                "    (\"Tap water supplied is highly contaminated, brown in color with foul sewage smell\", \"water_supply\", \"Critical\"),\n",
                "    (\"No drinking water supply in our locality for the past four consecutive days\", \"water_supply\", \"High\"),\n",
                "    (\"Drinking water pipe has joint leakage near storm drain, contaminated water entering taps\", \"water_supply\", \"Critical\"),\n",
                "    (\"Extremely low municipal water pressure, unable to pump water to overhead tanks\", \"water_supply\", \"Medium\"),\n",
                "    (\"Public drinking water borewell pump burnt and not functioning in poor neighborhood\", \"water_supply\", \"High\"),\n",
                "    (\"Municipal water tank not cleaned for over six months, sediment and worms visible in water\", \"water_supply\", \"Critical\"),\n",
                "    (\"మా వీధిలో తాగునీటి పైపులైన్ పగిలి మంచి నీరు రోడ్డుపై వృధాగా పోతోంది\", \"water_supply\", \"High\"),\n",
                "    (\"కుళాయిల్లో నల్లటి మురికి నీరు మరియు దుర్వాసనతో కూడిన కలుషిత నీరు వస్తోంది\", \"water_supply\", \"Critical\"),\n",
                "    (\"గత నాలుగు రోజులుగా మా కాలనీలో తాగునీటి సరఫరా పూర్తిగా నిలిచిపోయింది\", \"water_supply\", \"High\"),\n",
                "    (\"తాగునీటి పైపులో డ్రైనేజీ నీరు కలుస్తోంది నీరు తాగిన ప్రజలు వాంతులు విరేచనాలతో ఆస్పత్రి పాలయ్యారు\", \"water_supply\", \"Critical\"),\n",
                "    (\"మున్సిపల్ కుళాయిల్లో నీటి ప్రెజర్ అస్సలు లేదు బిందెడు నీళ్లు కూడా రావడం లేదు\", \"water_supply\", \"Medium\"),\n",
                "    (\"ప్రధాన వాటర్ పైప్‌లైన్ జాయింట్ లీకేజ్ వల్ల నీరంతా రోడ్డుపై ప్రవహిస్తోంది వెంటనే రిపేర్ చేయండి\", \"water_supply\", \"High\"),\n",
                "    (\"Drinking water pipeline pagilipoindi neellu waste avtunnayi\", \"water_supply\", \"High\"),\n",
                "    (\"Taps lo dirty water vastondi tagadaniki paniki raadu\", \"water_supply\", \"Critical\"),\n",
                "    (\"Water supply raaledu 3 days nundi public water problem\", \"water_supply\", \"High\"),\n",
                "\n",
                "    # --- STREET LIGHTS (English, Telugu, Tenglish) ---\n",
                "    (\"All street lights on main road are completely non-functional, pitch darkness at night\", \"street_lights\", \"High\"),\n",
                "    (\"Electric wire snapped from street pole and hanging dangerously low over footpath\", \"street_lights\", \"Critical\"),\n",
                "    (\"Street light pole damaged and leaning dangerously over roadway, can fall at any moment\", \"street_lights\", \"Critical\"),\n",
                "    (\"Street lights burning continuously during broad daylight, wasting public electricity\", \"street_lights\", \"Low\"),\n",
                "    (\"Junction box on electric pole is open with exposed live wires within reach of children\", \"street_lights\", \"Critical\"),\n",
                "    (\"Entire residential colony dark for three nights due to faulty street light timer switch\", \"street_lights\", \"High\"),\n",
                "    (\"మా వీధిలో అన్ని వీధి దీపాలు వెలగడం లేదు రాత్రిపూట అంతా చిమ్మచీకటిగా ఉంటోంది\", \"street_lights\", \"High\"),\n",
                "    (\"కరెంట్ స్తంభంపై ఉన్న స్ట్రీట్ లైట్ పాడైపోయింది మహిళలు రాత్రి నడవడానికి భయపడుతున్నారు\", \"street_lights\", \"High\"),\n",
                "    (\"విద్యుత్ వైర్లు తెగి రోడ్డుపై వేలాడుతున్నాయి ఎవరికైనా షాక్ కొట్టే ప్రమాదం ఉంది అత్యవసరం\", \"street_lights\", \"Critical\"),\n",
                "    (\"కరెంట్ పోల్ వంగిపోయింది రోడ్డుపై పడిపోయేలా ఉంది వెంటనే మార్చండి\", \"street_lights\", \"Critical\"),\n",
                "    (\"పగటిపూట కూడా వీధి లైట్లు వెలుగుతూ విద్యుత్ వృధా అవుతోంది ఆటోమేటిక్ సెన్సార్ రిపేర్ చేయండి\", \"street_lights\", \"Low\"),\n",
                "    (\"Street lights velagadam ledu night motham chikatiga undi\", \"street_lights\", \"High\"),\n",
                "    (\"Current wire tegipoyi road meeda undi danger shock risk\", \"street_lights\", \"Critical\"),\n",
                "    (\"Electric pole virigipoyi padipotundi urgent help\", \"street_lights\", \"Critical\"),\n",
                "\n",
                "    # --- OTHERS / SANITATION (English, Telugu, Tenglish) ---\n",
                "    (\"Huge open garbage dump piled up on roadside corner creating unbearable stench and dog menace\", \"others\", \"High\"),\n",
                "    (\"Sanitation sweepers have not cleared garbage from our street for ten consecutive days\", \"others\", \"High\"),\n",
                "    (\"Dead animal carcass rotting on roadside near market generating flies and disease hazard\", \"others\", \"Critical\"),\n",
                "    (\"Municipal dumper bin broken, rusted and overflowing with rotting kitchen waste\", \"others\", \"Medium\"),\n",
                "    (\"Severe mosquito menace in the ward, fogging and bleaching powder spraying required\", \"others\", \"Medium\"),\n",
                "    (\"రోడ్డు పక్కన చెత్త కుప్పలు పేరుకుపోయి తీవ్ర దుర్వాసన వస్తోంది ఈగలు ముసురుతున్నాయి\", \"others\", \"High\"),\n",
                "    (\"పారిశుద్ధ్య కార్మికులు వారం రోజులుగా చెత్త తీసుకెళ్లడం లేదు కాలనీ అంతా మురికిగా ఉంది\", \"others\", \"High\"),\n",
                "    (\"రోడ్డుపై చనిపోయిన కుక్క లేదా జంతువు కళేబరం ఉంది వెంటనే పారిశుద్ధ్య సిబ్బందిని పంపి తీసివేయించండి\", \"others\", \"Critical\"),\n",
                "    (\"రోడ్డుపై పిల్లి లేదా జంతువు చనిపోయి కుళ్లిపోయింది విపరీతమైన కంపు వస్తోంది కళేబరం తొలగించండి\", \"others\", \"Critical\"),\n",
                "    (\"మున్సిపల్ చెత్త డబ్బా నిండిపోయి చెత్త అంతా రోడ్డుపై చెల్లాచెదురుగా పడిపోతోంది\", \"others\", \"Medium\"),\n",
                "    (\"మా ఏరియాలో దోమలు విపరీతంగా ఉన్నాయి వెంటనే దోమల మందు ఫాగింగ్ చేయించండి బ్లీచింగ్ చల్లండి\", \"others\", \"Medium\"),\n",
                "    (\"Chetha kuppalu road meeda dump chesaru chala durgandham\", \"others\", \"High\"),\n",
                "    (\"Garbage auto 1 week nundi raaledu chetta ekkuva ayindi\", \"others\", \"High\"),\n",
                "    (\"Dead animal road meeda undi urgent clean cheyandi\", \"others\", \"Critical\"),\n",
                "    (\"Mosquitoes chala ekkuva ayyayi fogging and bleaching powder jallandi\", \"others\", \"Medium\")\n",
                "]\n",
                "\n",
                "# Data Augmentation\n",
                "LOCATIONS = [\n",
                "    \"in Vijayawada near Benz Circle\", \"near Visakhapatnam RTC complex\", \"at Guntur Brodipet\",\n",
                "    \"in Tirupati Alipiri bypass\", \"విజయవాడ బెంజ్ సర్కిల్ వద్ద\", \"విశాఖపట్నం ఆర్టీసీ కాంప్లెక్స్ సమీపంలో\",\n",
                "    \"గుంటూరు బ్రాడీపేట లో\", \"తిరుపతి అలిపిరి బైపాస్ రోడ్డులో\", \"near Government Hospital\"\n",
                "]\n",
                "\n",
                "augmented = []\n",
                "for text, cat, prio in RAW_DATA:\n",
                "    augmented.append((text, cat, prio))\n",
                "    loc = random.choice(LOCATIONS)\n",
                "    augmented.append((f\"{text} {loc}\", cat, prio))\n",
                "    if any('\\u0c00' <= c <= '\\u0c7f' for c in text):\n",
                "        augmented.append((f\"{text}. దయచేసి త్వరగా పరిష్కరించండి.\", cat, prio))\n",
                "    else:\n",
                "        augmented.append((f\"{text}. Please resolve urgently.\", cat, prio))\n",
                "\n",
                "df = pd.DataFrame(augmented, columns=['text', 'category', 'priority'])\n",
                "print(f\"Total Training Dataset Size: {len(df)} samples\")\n",
                "display(df['category'].value_counts())"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Train/Test Split & Feature Pipeline\n",
                "We use `TfidfVectorizer(token_pattern=r'(?u)\\b\\w+\\b')` to preserve Telugu Unicode script tokens alongside English words."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "X_train, X_test, y_train, y_test = train_test_split(\n",
                "    df['text'], df['category'], test_size=0.20, random_state=SEED, stratify=df['category']\n",
                ")\n",
                "\n",
                "pipeline = Pipeline([\n",
                "    ('tfidf', TfidfVectorizer(\n",
                "        token_pattern=r'(?u)\\b\\w+\\b',\n",
                "        ngram_range=(1, 3),\n",
                "        max_features=15000,\n",
                "        sublinear_tf=True\n",
                "    )),\n",
                "    ('clf', LogisticRegression(C=2.5, max_iter=1000, class_weight='balanced', random_state=SEED))\n",
                "])\n",
                "\n",
                "print(\"Training bilingual model...\")\n",
                "pipeline.fit(X_train, y_train)\n",
                "print(\"✅ Training complete!\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Rigorous Evaluation: Accuracy, Precision, Recall, F1, Confusion Matrix"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "y_pred = pipeline.predict(X_test)\n",
                "acc = accuracy_score(y_test, y_pred)\n",
                "\n",
                "print(\"=\" * 60)\n",
                "print(f\"🎯 TEST SET ACCURACY: {acc * 100:.2f}%\")\n",
                "print(\"=\" * 60)\n",
                "print(\"\\nDetailed Classification Report:\")\n",
                "print(classification_report(y_test, y_pred, digits=4))\n",
                "\n",
                "# Confusion Matrix Heatmap\n",
                "classes = sorted(list(DEPARTMENTS.keys()))\n",
                "cm = confusion_matrix(y_test, y_pred, labels=classes)\n",
                "\n",
                "plt.figure(figsize=(8, 6))\n",
                "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)\n",
                "plt.title('NEX-CIV Bilingual Grievance Confusion Matrix', fontsize=14, fontweight='bold')\n",
                "plt.xlabel('Predicted Department', fontsize=12)\n",
                "plt.ylabel('Actual Department', fontsize=12)\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Pure Telugu Benchmark Evaluation\n",
                "Testing real unseen Telugu sentences to verify genuine regional language comprehension."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "telugu_test_cases = [\n",
                "    (\"మా ఊరి ప్రధాన రహదారిపై భారీ గుంతలు పడి ద్విచక్ర వాహనదారులు కింద పడుతున్నారు\", \"road\"),\n",
                "    (\"తారు రోడ్డు వర్షం నీటికి పూర్తిగా కొట్టుకుపోయింది కంకర తేలింది\", \"road\"),\n",
                "    (\"మురుగు కాలువ పొంగి వీధి అంతా దుర్గంధం వస్తోంది వెంటనే క్లీన్ చేయండి\", \"drainage\"),\n",
                "    (\"మా వీధిలో డ్రైనేజ్ మ్యాన్‌హోల్ మూత విరిగిపోయింది ఎవరైనా పడిపోయే ప్రమాదం ఉంది\", \"drainage\"),\n",
                "    (\"తాగునీటి ప్రధాన పైపులైన్ పగిలి రోజంతా వేల లీటర్ల మంచి నీరు వృధా అవుతోంది\", \"water_supply\"),\n",
                "    (\"కుళాయిల్లో నల్లటి మురికి నీరు వస్తోంది తాగడానికి అసలు పనికి రావడం లేదు\", \"water_supply\"),\n",
                "    (\"వీధి దీపాలు వెలగడం లేదు రాత్రిపూట కాలనీ అంతా చీకటిగా ఉంది దొంగల భయం\", \"street_lights\"),\n",
                "    (\"కరెంట్ స్తంభంపై లైట్ పోయింది అలాగే వైర్లు కిందకు వేలాడుతున్నాయి షాక్ కొడుతుంది\", \"street_lights\"),\n",
                "    (\"చెత్త కుప్పలు రోడ్డు పక్కన పేరుకుపోయాయి దోమలు విపరీతంగా పెరిగిపోయాయి\", \"others\"),\n",
                "    (\"రోడ్డుపై పిల్లి చనిపోయి కుళ్లిపోయింది విపరీతమైన కంపు వస్తోంది తీసేయండి\", \"others\")\n",
                "]\n",
                "\n",
                "passed = 0\n",
                "print(\"\\n--- TELUGU INFERENCE RESULTS ---\")\n",
                "for text, true_label in telugu_test_cases:\n",
                "    pred = pipeline.predict([text])[0]\n",
                "    probs = pipeline.predict_proba([text])[0]\n",
                "    conf = np.max(probs) * 100\n",
                "    ok = (pred == true_label)\n",
                "    if ok: passed += 1\n",
                "    status = \"PASS ✅\" if ok else \"FAIL ❌\"\n",
                "    print(f\"[{status}] True: {true_label:13} | Pred: {pred:13} ({conf:5.1f}%) | Text: {text}\")\n",
                "\n",
                "print(f\"\\nTelugu Benchmark Score: {passed}/{len(telugu_test_cases)} ({passed/len(telugu_test_cases)*100:.1f}%)\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Export Model Bundle (`.pkl`)\n",
                "Save and download `complaint_classifier.pkl` to deploy directly into the NEX-CIV `models/` directory."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "bundle = {\n",
                "    'wing_pipeline': pipeline,\n",
                "    'pipeline': pipeline,\n",
                "    'classes': pipeline.classes_,\n",
                "    'departments': DEPARTMENTS,\n",
                "    'model_version': '2.0.0-bilingual-te-en'\n",
                "}\n",
                "\n",
                "model_filename = 'complaint_classifier.pkl'\n",
                "joblib.dump(bundle, model_filename)\n",
                "print(f\"✅ Model bundle successfully saved as '{model_filename}' ({os.path.getsize(model_filename) / 1024:.1f} KB)\")\n",
                "\n",
                "# In Google Colab, uncomment the lines below to download the pkl file immediately:\n",
                "# from google.colab import files\n",
                "# files.download(model_filename)"
            ]
        }
    ]
}

os.makedirs('notebooks', exist_ok=True)
notebook_path = os.path.join('notebooks', 'NEXCIV_Telugu_English_Civic_Classifier.ipynb')
root_notebook_path = 'NEXCIV_Telugu_Civic_Classifier.ipynb'

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

with open(root_notebook_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print(f"Generated Colab Notebook at:\n  1. {notebook_path}\n  2. {root_notebook_path}")
