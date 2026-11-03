import sys
import os
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DEPARTMENTS = {
    'road': {
        'name': 'Roads & Buildings Department (R&B / Municipal)',
        'code': 'road',
        'short': 'Roads & Buildings',
        'head': 'Superintending Engineer (R&B / Municipal Corporation)'
    },
    'drainage': {
        'name': 'Public Health & Drainage Department',
        'code': 'drainage',
        'short': 'Drainage & Sewerage',
        'head': 'Executive Engineer (Public Health & Sewerage)'
    },
    'water_supply': {
        'name': 'Water Supply & Quality Department',
        'code': 'water_supply',
        'short': 'Water Supply Board',
        'head': 'Chief Water Works Engineer (CPWS / Municipal)'
    },
    'street_lights': {
        'name': 'Electrical & Street Lighting Wing',
        'code': 'street_lights',
        'short': 'Electrical & Lighting',
        'head': 'Executive Engineer (APEPDCL / APSPDCL / Municipal)'
    },
    'others': {
        'name': 'Sanitation & Solid Waste Management Wing',
        'code': 'others',
        'short': 'Sanitation & SWM',
        'head': 'Chief Municipal Health Officer (CMHO)'
    }
}

# Rich Bilingual Dataset: English + Telugu (తెలుగు) + Telugu Transliteration (Manglish/Tenglish)
RAW_DATA = [
    # ==================== ROAD (రోడ్లు / గుంతలు) ====================
    # English
    ("Deep dangerous pothole crater on main BT road causing severe vehicle axle damage and bike skids", "road", "High"),
    ("Massive road cave-in and sinkhole opened after rain near junction, traffic completely jammed", "road", "Critical"),
    ("Asphalt layer completely eroded with sharp gravel exposed, slippery for two-wheelers", "road", "Medium"),
    ("Concrete road divider broken and scattered on road lane, high accident risk", "road", "High"),
    ("Pedestrian footpath pavement tiles are broken, missing, and uneven", "road", "Low"),
    ("Unpainted unmarked speed breaker on main arterial road causing severe accidents", "road", "High"),
    ("Culvert slab collapsed across the road, vehicles unable to pass", "road", "Critical"),
    ("Flyover approach slab has developed deep cracks and pavement unevenness", "road", "High"),
    ("Trench dug for underground cable left open without barricades or backfilling", "road", "High"),
    ("Tar road damaged with multiple large potholes outside bus station", "road", "High"),
    ("Yellow and black paint on road divider has completely faded, repaint required", "road", "Low"),
    ("Loose gravel and sand scattered across fast lane on national highway bypass", "road", "Medium"),
    ("Road shoulder damaged and eroded due to heavy truck traffic", "road", "Medium"),
    ("CC road cracked into multiple pieces near residential colony entrance", "road", "Medium"),
    ("Dangerous dip and depression on road surface causing sudden shock to drivers", "road", "Medium"),
    
    # Telugu (తెలుగు లిపి)
    ("రోడ్డుపై పెద్ద గుంతలు పడ్డాయి వాహనాలు నడపడం చాలా కష్టంగా ఉంది", "road", "High"),
    ("మా వీధిలో తారు రోడ్డు పూర్తిగా పాడైపోయింది వెంటనే మరమ్మతులు చేయాలి", "road", "Medium"),
    ("వర్షాల వల్ల రోడ్డుపై భారీ గుంత ఏర్పడి బైకులు జారి పడిపోతున్నాయి", "road", "High"),
    ("వంతెన దగ్గర రోడ్డు కుంగిపోయింది వాహనాల రాకపోకలు నిలిచిపోయాయి అత్యవసర సహాయం", "road", "Critical"),
    ("సీసీ రోడ్డు పగిలిపోయి రాళ్లు పైకి తేలి ఉన్నాయి నడవడానికి తీవ్ర ఇబ్బంది", "road", "Medium"),
    ("రోడ్డు డివైడర్ విరిగిపోయి రాళ్లు రోడ్డుపై పడ్డాయి ప్రమాదాలు జరిగే అవకాశం ఉంది", "road", "High"),
    ("పాదచారుల ఫుట్‌పాత్ పలకలు ఊడిపోయాయి వృద్ధులు నడవలేకపోతున్నారు", "road", "Low"),
    ("రోడ్డు తవ్వి కేబుల్ వేసిన తర్వాత పూడ్చకుండా వదిలేశారు వాహనాలు ఇరుక్కుపోతున్నాయి", "road", "High"),
    ("స్పీడ్ బ్రేకర్ కనిపించడం లేదు రంగు వేయకపోవడం వల్ల రాత్రి ప్రమాదాలు జరుగుతున్నాయి", "road", "Medium"),
    ("మెయిన్ రోడ్డుపై తారు కొట్టుకుపోయి కంకర తేలింది ద్విచక్ర వాహనాలు జారుతున్నాయి", "road", "High"),
    ("బైపాస్ రోడ్డుపై పెద్ద గుంతలు పడి కార్ల టైర్లు పగిలిపోతున్నాయి", "road", "High"),
    ("రోడ్డు మలుపు వద్ద కల్వర్టు స్లాబ్ విరిగిపోయింది వెంటనే మరమ్మతు చేయించండి", "road", "Critical"),
    ("కాలనీ రోడ్డు అంతా గతుకులమయంగా మారింది ఆటోలు కూడా రావడం లేదు", "road", "Medium"),
    ("రోడ్డు మధ్యలో పెద్ద పగుళ్లు ఏర్పడ్డాయి తక్షణమే బీటీ ప్యాచ్ వర్క్ చేయాలి", "road", "Medium"),
    ("వర్షపు నీటి ప్రవాహానికి రోడ్డు కొట్టుకుపోయింది తాత్కాలిక రోడ్డు వేయండి", "road", "Critical"),

    # Telugu Transliteration (Tenglish)
    ("Road meeda pedda guntalu paddayi bikes paddipotunnayi", "road", "High"),
    ("Tar road motham paadaipoindi vehicles move avvalekapotunnayi", "road", "High"),
    ("Main road sinkhole open ayindi traffic jam", "road", "Critical"),
    ("Speed breaker ki paint ledu accident risk chala ekkuva", "road", "Medium"),
    ("Footpath tiles virigipoyi pedestrian ki chala problem ga undi", "road", "Low"),
    ("Road tavvi poodchakunda vadilesaru repair cheyandi", "road", "High"),

    # ==================== DRAINAGE (మురుగు కాలువలు / డ్రైనేజీ) ====================
    # English
    ("Open drainage canal overflowing onto public road causing severe foul smell and health hazard", "drainage", "High"),
    ("Underground sewerage manhole cover missing on busy street, extreme accident hazard", "drainage", "Critical"),
    ("Sewer pipe clogged and black sewage backing up into residential houses", "drainage", "Critical"),
    ("Stormwater drain completely silted and choked with solid waste, water logging in colony", "drainage", "Medium"),
    ("Broken concrete slab over side drain, pedestrian fell into drain", "drainage", "High"),
    ("Foul smell and sewage stagnation due to lack of regular desilting in roadside gutter", "drainage", "Medium"),
    ("Drainage line ruptured and dirty sewage water mixing with rain water on road", "drainage", "High"),
    ("Manhole overflowing with toilet waste and sewage on residential street", "drainage", "Critical"),
    ("Side drain constructed without proper gradient, stagnant black water breeding mosquitoes", "drainage", "Medium"),
    ("Commercial restaurant dumping oil and grease into municipal drain causing complete blockage", "drainage", "Medium"),
    ("Drain slab broken by heavy vehicle, open gutter exposing sewage", "drainage", "Medium"),
    ("Sullage drain overflowing into school entrance preventing children from entering", "drainage", "High"),

    # Telugu (తెలుగు లిపి)
    ("మురుగు కాలువ పొంగి రోడ్డుపై నల్లటి మురుగు నీరు ప్రవహిస్తోంది తీవ్ర దుర్వాసన", "drainage", "High"),
    ("మా వీధిలో డ్రైనేజీ మ్యాన్‌హోల్ మూత పగిలిపోయింది లేదా తెరిచి ఉంది ప్రమాదం", "drainage", "Critical"),
    ("అండర్‌గ్రౌండ్ డ్రైనేజ్ పైపు బ్లాక్ అయ్యి ఇళ్లల్లోకి మురుగు నీరు వెనక్కి వస్తోంది", "drainage", "Critical"),
    ("డ్రైనేజీ కాలువ పూడికతో నిండిపోయింది మురుగు నీరు ముందుకు సాగడం లేదు దోమలు పెరిగాయి", "drainage", "Medium"),
    ("కాలువపై ఉన్న సిమెంట్ స్లాబ్ విరిగిపోయి మురుగు కాలువ తెరిచి ఉంది", "drainage", "High"),
    ("డ్రైనేజీ నీరు రోడ్డుపై నిలిచి భరించలేని దుర్వాసన వస్తోంది ప్రజలు రోగాల బారిన పడుతున్నారు", "drainage", "High"),
    ("వర్షం రాకముందే డ్రైనేజీ కాలువల్లో పూడిక తీయించండి లేకపోతే ఇళ్లు మునిగిపోతాయి", "drainage", "Medium"),
    ("మురుగు కాలువ జామ్ అయి నీరు రోడ్డుపైకి పొంగిపొర్లుతోంది వెంటనే సూపర్ సక్కర్ పంపండి", "drainage", "High"),
    ("మ్యాన్‌హోల్ నుండి మురుగు నీరు ఉబికి వస్తోంది పరిసరాలు అపరిశుభ్రంగా మారాయి", "drainage", "High"),
    ("కాలువలో ప్లాస్టిక్ వ్యర్థాలు పేరుకుపోయి మురుగు నీటి ప్రవాహం ఆగిపోయింది", "drainage", "Medium"),
    ("డ్రైనేజీ వ్యవస్థ సరిగ్గా లేక చిన్న వర్షానికే కాలనీ మురుగు నీటితో నిండిపోతుంది", "drainage", "High"),
    ("ఓపెన్ డ్రైనేజ్ వల్ల దోమలు విపరీతంగా పెరిగి డెంగ్యూ జ్వరాలు వస్తున్నాయి", "drainage", "High"),

    # Telugu Transliteration (Tenglish)
    ("Murugu kaluva pongi road meeda drainage neellu vastunnayi", "drainage", "High"),
    ("Drainage block ayindi manhole nundi foul smell and dirty water leaking", "drainage", "High"),
    ("Manhole cover ledu open ga undi danger to pedestrians", "drainage", "Critical"),
    ("Drainage pudika teeyali mosquitoes ekkuva ayyayi", "drainage", "Medium"),
    ("Underground sewage pipe leak ayi road motham dirty ayindi", "drainage", "High"),

    # ==================== WATER SUPPLY (తాగునీటి సరఫరా) ====================
    # English
    ("Major drinking water pipeline burst flooding the road with thousands of liters of clean water wasted", "water_supply", "High"),
    ("Tap water supplied is highly contaminated, brown in color with foul sewage smell", "water_supply", "Critical"),
    ("No drinking water supply in our locality for the past four consecutive days", "water_supply", "High"),
    ("Drinking water pipe has joint leakage near storm drain, contaminated water entering taps", "water_supply", "Critical"),
    ("Extremely low municipal water pressure, unable to pump water to overhead tanks", "water_supply", "Medium"),
    ("Public drinking water borewell pump burnt and not functioning in poor neighborhood", "water_supply", "High"),
    ("Water distribution valve damaged by road contractors, water supply stopped in entire ward", "water_supply", "High"),
    ("Drinking water smells like chemical chlorine excess and causing burning sensation", "water_supply", "High"),
    ("Public roadside water tap tap broken, continuous water leakage and wastage", "water_supply", "Medium"),
    ("Water supply timings irregular, water released at midnight without prior notice", "water_supply", "Low"),
    ("Municipal water tank not cleaned for over six months, sediment and worms visible in water", "water_supply", "Critical"),
    ("Air lock in water pipeline preventing water from reaching tail-end houses in the street", "water_supply", "Medium"),

    # Telugu (తెలుగు లిపి)
    ("మా వీధిలో తాగునీటి పైపులైన్ పగిలి మంచి నీరు రోడ్డుపై వృధాగా పోతోంది", "water_supply", "High"),
    ("కుళాయిల్లో నల్లటి మురికి నీరు మరియు దుర్వాసనతో కూడిన కలుషిత నీరు వస్తోంది", "water_supply", "Critical"),
    ("గత నాలుగు రోజులుగా మా కాలనీలో తాగునీటి సరఫరా పూర్తిగా నిలిచిపోయింది", "water_supply", "High"),
    ("తాగునీటి పైపులో డ్రైనేజీ నీరు కలుస్తోంది నీరు తాగిన ప్రజలు వాంతులు విరేచనాలతో ఆస్పత్రి పాలయ్యారు", "water_supply", "Critical"),
    ("మున్సిపల్ కుళాయిల్లో నీటి ప్రెజర్ అస్సలు లేదు బిందెడు నీళ్లు కూడా రావడం లేదు", "water_supply", "Medium"),
    ("ప్రధాన వాటర్ పైప్‌లైన్ జాయింట్ లీకేజ్ వల్ల నీరంతా రోడ్డుపై ప్రవహిస్తోంది వెంటనే రిపేర్ చేయండి", "water_supply", "High"),
    ("వీధి చివర ఉన్న పబ్లిక్ వాటర్ ట్యాప్ విరిగిపోయి నిరంతరం నీరు కారుతోంది", "water_supply", "Medium"),
    ("ఓవర్‌హెడ్ వాటర్ ట్యాంక్ శుభ్రం చేయక పురుగులు వస్తున్నాయి స్వచ్ఛమైన నీరు అందించండి", "water_supply", "Critical"),
    ("నీటి సరఫరా వాల్వ్ పాడైపోయింది మా వీధికి నీరు అందడం లేదు", "water_supply", "High"),
    ("తాగునీటి బోర్ వెల్ మోటార్ కాలిపోయింది ప్రజలు నీటి కోసం తీవ్ర ఇబ్బందులు పడుతున్నారు", "water_supply", "High"),
    ("మురికి వాసనతో నీరు వస్తోంది క్లోరినేషన్ సరిగ్గా చేయడం లేదు తనిఖీ చేయండి", "water_supply", "High"),
    ("తాగునీరు వచ్చే సమయాలు సరిగ్గా లేవు అర్ధరాత్రి నీరు వదులుతున్నారు", "water_supply", "Low"),

    # Telugu Transliteration (Tenglish)
    ("Drinking water pipeline pagilipoindi neellu waste avtunnayi", "water_supply", "High"),
    ("Taps lo dirty water vastondi tagadaniki paniki raadu", "water_supply", "Critical"),
    ("Water supply raaledu 3 days nundi public water problem", "water_supply", "High"),
    ("Low water pressure valla second floor ki neellu ekkadam ledu", "water_supply", "Medium"),
    ("Water lo foul smell vastondi drainage water mix ayyindi emo", "water_supply", "Critical"),

    # ==================== STREET LIGHTS (వీధి దీపాలు / విద్యుత్) ====================
    # English
    ("All street lights on main road are completely non-functional, pitch darkness at night", "street_lights", "High"),
    ("Electric wire snapped from street pole and hanging dangerously low over footpath", "street_lights", "Critical"),
    ("Street light pole damaged and leaning dangerously over roadway, can fall at any moment", "street_lights", "Critical"),
    ("Street lights burning continuously during broad daylight, wasting public electricity", "street_lights", "Low"),
    ("LED street light fixture flickering continuously and making loud buzzing noise", "street_lights", "Low"),
    ("Junction box on electric pole is open with exposed live wires within reach of children", "street_lights", "Critical"),
    ("Entire residential colony dark for three nights due to faulty street light timer switch", "street_lights", "High"),
    ("Underground cable fault caused blackout of all street lights in ward 12", "street_lights", "High"),
    ("Street light bulb fused and not replaced for the past two weeks", "street_lights", "Medium"),
    ("Solar street light panel broken and battery stolen, light dead", "street_lights", "Medium"),
    ("Sparking and short circuit occurring near transformer pole at night", "street_lights", "Critical"),

    # Telugu (తెలుగు లిపి)
    ("మా వీధిలో అన్ని వీధి దీపాలు వెలగడం లేదు రాత్రిపూట అంతా చిమ్మచీకటిగా ఉంటోంది", "street_lights", "High"),
    ("కరెంట్ స్తంభంపై ఉన్న స్ట్రీట్ లైట్ పాడైపోయింది మహిళలు రాత్రి నడవడానికి భయపడుతున్నారు", "street_lights", "High"),
    ("విద్యుత్ వైర్లు తెగి రోడ్డుపై వేలాడుతున్నాయి ఎవరికైనా షాక్ కొట్టే ప్రమాదం ఉంది అత్యవసరం", "street_lights", "Critical"),
    ("కరెంట్ పోల్ వంగిపోయింది రోడ్డుపై పడిపోయేలా ఉంది వెంటనే మార్చండి", "street_lights", "Critical"),
    ("పగటిపూట కూడా వీధి లైట్లు వెలుగుతూ విద్యుత్ వృధా అవుతోంది ఆటోమేటిక్ సెన్సార్ రిపేర్ చేయండి", "street_lights", "Low"),
    ("వీధి స్తంభం వద్ద జంక్షన్ బాక్స్ మూత లేకుండా తెరిచి ఉంది పిల్లలు ఆడుకునే చోట లైవ్ వైర్లు ఉన్నాయి", "street_lights", "Critical"),
    ("ఎల్ఈడీ వీధి దీపాలు బ్లింక్ అవుతున్నాయి లేదా వెలగడం లేదు కొత్త బల్బులు వేయండి", "street_lights", "Medium"),
    ("ట్రాన్స్‌ఫార్మర్ వద్ద స్పార్క్ వస్తోంది వీధి లైట్లు ఒక్కసారిగా ఆగిపోయాయి", "street_lights", "Critical"),
    ("కాలనీలో చీకటి వల్ల రాత్రిపూట దొంగతనాలు మరియు అసాంఘిక కార్యకలాపాలు జరుగుతున్నాయి లైట్లు వేయండి", "street_lights", "High"),
    ("కొత్తగా వేసిన విద్యుత్ స్తంభానికి లైట్లు అమర్చలేదు చీకటిగా ఉంది", "street_lights", "Medium"),
    ("వర్షం వల్ల కరెంట్ పోల్ కి ఎర్త్ కొడుతోంది స్తంభం ముట్టుకుంటే షాక్ వస్తోంది", "street_lights", "Critical"),

    # Telugu Transliteration (Tenglish)
    ("Street lights velagadam ledu night motham chikatiga undi", "street_lights", "High"),
    ("Current wire tegipoyi road meeda undi danger shock risk", "street_lights", "Critical"),
    ("Electric pole virigipoyi padipotundi urgent help", "street_lights", "Critical"),
    ("Street light fuse poyindi bulb replace cheyandi", "street_lights", "Medium"),
    ("Pagalanta lights velugutune unnayi power waste", "street_lights", "Low"),

    # ==================== OTHERS / SANITATION (పారిశుధ్యం / చెత్త) ====================
    # English
    ("Huge open garbage dump piled up on roadside corner creating unbearable stench and dog menace", "others", "High"),
    ("Sanitation sweepers have not cleared garbage from our street for ten consecutive days", "others", "High"),
    ("Dead animal carcass rotting on roadside near market generating flies and disease hazard", "others", "Critical"),
    ("Municipal dumper bin broken, rusted and overflowing with rotting kitchen waste", "others", "Medium"),
    ("Severe mosquito menace in the ward, fogging and bleaching powder spraying required", "others", "Medium"),
    ("Construction debris and concrete rubble illegally dumped on public road blocking half lane", "others", "Medium"),
    ("Vacant open plot turned into illegal garbage dumping ground with overgrown bushes and snakes", "others", "Medium"),
    ("Fish and meat waste dumped openly on road near weekly bazaar creating intolerable stink", "others", "High"),
    ("Plastic waste, polythene covers, and bottles littered all across the public park and walking track", "others", "Low"),
    ("Sanitary workers burning plastic and dry leaves on street causing toxic smoke and breathing issues", "others", "High"),
    ("Commercial poultry shop dumping chicken feathers and waste directly on roadside", "others", "High"),
    ("Bio-medical waste discarded openly near private nursing home", "others", "Critical"),

    # Telugu (తెలుగు లిపి)
    ("రోడ్డు పక్కన చెత్త కుప్పలు పేరుకుపోయి తీవ్ర దుర్వాసన వస్తోంది ఈగలు ముసురుతున్నాయి", "others", "High"),
    ("పారిశుద్ధ్య కార్మికులు వారం రోజులుగా చెత్త తీసుకెళ్లడం లేదు కాలనీ అంతా మురికిగా ఉంది", "others", "High"),
    ("రోడ్డుపై చనిపోయిన కుక్క లేదా జంతువు కళేబరం ఉంది వెంటనే పారిశుద్ధ్య సిబ్బందిని పంపి తీసివేయించండి", "others", "Critical"),
    ("రోడ్డుపై పిల్లి లేదా జంతువు చనిపోయి కుళ్లిపోయింది విపరీతమైన కంపు వస్తోంది కళేబరం తొలగించండి", "others", "Critical"),
    ("చనిపోయిన జంతువులు రోడ్డు పక్కన పడి కుళ్లిపోతున్నాయి తీవ్ర దుర్గంధం మరియు వ్యాధులు", "others", "Critical"),
    ("మున్సిపల్ చెత్త డబ్బా నిండిపోయి చెత్త అంతా రోడ్డుపై చెల్లాచెదురుగా పడిపోతోంది", "others", "Medium"),
    ("మా ఏరియాలో దోమలు విపరీతంగా ఉన్నాయి వెంటనే దోమల మందు ఫాగింగ్ చేయించండి బ్లీచింగ్ చల్లండి", "others", "Medium"),
    ("భవన నిర్మాణ వ్యర్థాలు మరియు మట్టి రోడ్డుపై పోసి వదిలేశారు వాహనాల రాకపోకలకు ఆటంకం", "others", "Medium"),
    ("ఖాళీ స్థలంలో చెత్త మరియు పిచ్చి మొక్కలు పెరిగి పాములు పురుగులు వస్తున్నాయి శుభ్రం చేయించండి", "others", "Medium"),
    ("చేపల మరియు మాంసం మార్కెట్ వ్యర్థాలు రోడ్డుపై వేయడం వల్ల భరించలేని కంపు వస్తోంది", "others", "High"),
    ("చెత్తను రోడ్డుపై కాల్చడం వల్ల దట్టమైన పొగ వచ్చి శ్వాస తీసుకోవడం కష్టంగా ఉంది", "others", "High"),
    ("పార్క్ లో మరియు వాకింగ్ ట్రాక్ పై ప్లాస్టిక్ కవర్లు బాటిళ్లు పడి ఉన్నాయి క్లీన్ చేయండి", "others", "Low"),
    ("ఇంటింటికి వచ్చి చెత్త సేకరించే ఆటో రావడం లేదు చెత్త ఇళ్లల్లోనే ఉండిపోతుంది", "others", "Medium"),
    ("డ్రైనేజీ పూడిక తీసిన తర్వాత ఆ మట్టిని రోడ్డు పక్కనే వదిలేశారు ఎండిపోయి దుమ్ము లేస్తోంది", "others", "Medium"),

    # Telugu Transliteration (Tenglish)
    ("Chetha kuppalu road meeda dump chesaru chala durgandham", "others", "High"),
    ("Garbage auto 1 week nundi raaledu chetta ekkuva ayindi", "others", "High"),
    ("Dead animal road meeda undi urgent clean cheyandi", "others", "Critical"),
    ("Mosquitoes chala ekkuva ayyayi fogging and bleaching powder jallandi", "others", "Medium"),
    ("Construction waste road block chesindi remove cheyandi", "others", "Medium"),
]

# Data Augmentation to simulate varied citizen phrasings and locations
LOCATIONS = [
    "in Vijayawada near Benz Circle", "near Visakhapatnam RTC complex", "at Guntur Brodipet",
    "in Tirupati Alipiri bypass", "near Kakinada port road", "in Nellore trunk road",
    "విజయవాడ బెంజ్ సర్కిల్ వద్ద", "విశాఖపట్నం ఆర్టీసీ కాంప్లెక్స్ సమీపంలో", "గుంటూరు బ్రాడీపేట లో",
    "తిరుపతి అలిపిరి బైపాస్ రోడ్డులో", "కర్నూలు పాత బస్టాండ్ వద్ద", "రాజమండ్రి కోటిపల్లి బస్టాండ్ దగ్గర",
    "near Government General Hospital GGH", "outside ZP High School gate", "near Railway Station"
]

augmented_samples = []
for text, cat, prio in RAW_DATA:
    augmented_samples.append((text, cat, prio))
    # Add variations with location phrases
    loc = random.choice(LOCATIONS)
    augmented_samples.append((f"{text} {loc}", cat, prio))
    # Add polite/urgent request variations
    if any('\u0c00' <= char <= '\u0c7f' for char in text):
        augmented_samples.append((f"{text}. దయచేసి త్వరగా పరిష్కరించండి.", cat, prio))
        augmented_samples.append((f"మునిసిపల్ అధికారులకు విజ్ఞప్తి: {text}", cat, prio))
    else:
        augmented_samples.append((f"{text}. Please resolve immediately.", cat, prio))
        augmented_samples.append((f"Urgent civic complaint: {text}", cat, prio))

df = pd.DataFrame(augmented_samples, columns=['text', 'category', 'priority'])
print(f"Total Augmented Training Samples: {len(df)}")
print(f"Category Distribution:\n{df['category'].value_counts()}\n")

# Train / Test Split
X = df['text']
y_cat = df['category']
y_prio = df['priority']

X_train, X_test, y_train, y_test, p_train, p_test = train_test_split(
    X, y_cat, y_prio, test_size=0.20, random_state=SEED, stratify=y_cat
)

print(f"Training on {len(X_train)} samples, Testing on {len(X_test)} samples...\n")

# Category Pipeline: Multilingual TF-IDF + Calibrated Logistic Regression
# token_pattern=r'(?u)\b\w+\b' handles Telugu Unicode words and English alphanumeric words
vectorizer = TfidfVectorizer(
    token_pattern=r'(?u)\b\w+\b',
    ngram_range=(1, 3),
    max_features=15000,
    sublinear_tf=True
)

cat_clf = LogisticRegression(C=2.5, max_iter=1000, class_weight='balanced', random_state=SEED)
cat_pipeline = Pipeline([
    ('tfidf', vectorizer),
    ('clf', cat_clf)
])

cat_pipeline.fit(X_train, y_train)

# Priority Pipeline (for internal routing / employee dashboard)
prio_clf = LogisticRegression(C=1.5, max_iter=1000, class_weight='balanced', random_state=SEED)
prio_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(token_pattern=r'(?u)\b\w+\b', ngram_range=(1, 2), max_features=8000)),
    ('clf', prio_clf)
])
prio_pipeline.fit(X_train, p_train)

# ==================== COMPREHENSIVE EVALUATION ====================
y_pred = cat_pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print("=" * 60)
print(f"BILINGUAL CATEGORY CLASSIFIER ACCURACY: {acc * 100:.2f}%")
print("=" * 60)
print("\nClassification Report (English + Telugu):")
print(classification_report(y_test, y_pred, digits=4))

print("\nConfusion Matrix:")
classes = sorted(list(DEPARTMENTS.keys()))
cm = confusion_matrix(y_test, y_pred, labels=classes)
cm_df = pd.DataFrame(cm, index=[f"True_{c}" for c in classes], columns=[f"Pred_{c}" for c in classes])
print(cm_df)

# ==================== DEDICATED TELUGU SCRIPT TEST SUITE ====================
print("\n" + "=" * 60)
print("EVALUATING DEDICATED PURE TELUGU SCRIPT TEST SUITE")
print("=" * 60)

telugu_benchmarks = [
    # Road
    ("మా ఊరి ప్రధాన రహదారిపై భారీ గుంతలు పడి ద్విచక్ర వాహనదారులు కింద పడుతున్నారు", "road"),
    ("తారు రోడ్డు వర్షం నీటికి పూర్తిగా కొట్టుకుపోయింది కంకర తేలింది", "road"),
    ("ఫ్లైఓవర్ రోడ్డు పక్కన కల్వర్టు విరిగిపోయింది వాహనాలు వెళ్లడం కష్టం", "road"),
    
    # Drainage
    ("మురుగు కాలువ పొంగి వీధి అంతా దుర్గంధం వస్తోంది వెంటనే క్లీన్ చేయండి", "drainage"),
    ("మా వీధిలో డ్రైనేజ్ మ్యాన్‌హోల్ మూత విరిగిపోయింది ఎవరైనా పడిపోయే ప్రమాదం ఉంది", "drainage"),
    ("అండర్‌గ్రౌండ్ డ్రైనేజ్ పైపు బ్లాక్ అయింది నీరు ముందుకు సాగడం లేదు", "drainage"),

    # Water Supply
    ("తాగునీటి ప్రధాన పైపులైన్ పగిలి రోజంతా వేల లీటర్ల మంచి నీరు వృధా అవుతోంది", "water_supply"),
    ("కుళాయిల్లో నల్లటి మురికి నీరు వస్తోంది తాగడానికి అసలు పనికి రావడం లేదు", "water_supply"),
    ("గత ఐదు రోజులుగా మా ఏరియాలో మునిసిపల్ తాగునీరు రాలేదు", "water_supply"),

    # Street Lights
    ("వీధి దీపాలు వెలగడం లేదు రాత్రిపూట కాలనీ అంతా చీకటిగా ఉంది దొంగల భయం", "street_lights"),
    ("కరెంట్ స్తంభంపై లైట్ పోయింది అలాగే వైర్లు కిందకు వేలాడుతున్నాయి షాక్ కొడుతుంది", "street_lights"),
    ("పగటి సమయంలో కూడా వీధి లైట్లు ఆపకుండా వెలుగుతున్నాయి విద్యుత్ ఆదా చేయండి", "street_lights"),

    # Others / Sanitation
    ("చెత్త కుప్పలు రోడ్డు పక్కన పేరుకుపోయాయి దోమలు విపరీతంగా పెరిగిపోయాయి", "others"),
    ("రోడ్డుపై పిల్లి చనిపోయి కుళ్లిపోయింది విపరీతమైన కంపు వస్తోంది తీసేయండి", "others"),
    ("పారిశుద్ధ్య కార్మికులు వారం నుంచి చెత్త సేకరించడం లేదు వీధి అంతా కంపు", "others")
]

telugu_correct = 0
for text, true_cat in telugu_benchmarks:
    pred_cat = cat_pipeline.predict([text])[0]
    probs = cat_pipeline.predict_proba([text])[0]
    conf = float(np.max(probs)) * 100
    is_match = (pred_cat == true_cat)
    if is_match:
        telugu_correct += 1
    mark = "PASS" if is_match else "FAIL"
    print(f"[{mark}] Pred: {pred_cat:13} (Conf: {conf:5.1f}%) | True: {true_cat:13} | Text: {text[:50]}...")

telugu_acc = (telugu_correct / len(telugu_benchmarks)) * 100
print(f"\nDedicated Telugu Benchmark Accuracy: {telugu_acc:.1f}% ({telugu_correct}/{len(telugu_benchmarks)} passed)")

# Save Model Bundle
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "complaint_classifier")
os.makedirs(MODEL_DIR, exist_ok=True)

bundle = {
    'wing_pipeline': cat_pipeline,
    'pipeline': cat_pipeline,
    'prio_pipeline': prio_pipeline,
    'priority_pipeline': prio_pipeline,
    'classes': cat_pipeline.classes_,
    'languages_supported': ['en', 'te', 'te-Latn'],
    'departments': DEPARTMENTS,
    'model_version': '2.0.0-bilingual-te-en',
    'accuracy': float(acc),
    'telugu_accuracy': float(telugu_acc)
}

save_path_1 = os.path.join(MODEL_DIR, "nexciv_multimodal_priority_model.pkl")
save_path_2 = os.path.join(MODEL_DIR, "complaint_classifier.pkl")

joblib.dump(bundle, save_path_1)
joblib.dump(bundle, save_path_2)

print(f"\nSaved Bilingual AI Model to:\n  1. {save_path_1}\n  2. {save_path_2}")
print("\n>>> MODEL TRAINING & SERIOUS EVALUATION COMPLETED SUCCESSFULLY!")
