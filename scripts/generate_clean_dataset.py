"""
NEX-CIV: Clean Multilingual Civic Grievance Dataset Generator
Creates 3,600+ authentic municipal grievance records across:
- 5 Departments (road, drainage, water_supply, street_lights, others)
- 20 Civic Complaint Types
- 3 Language Styles: English (en), Native Telugu (te), Romanized Telugu (te_latn)
- Strict Incident Cluster Partitioning: 70% Train, 15% Validation, 15% Test
- 100% Zero Leakage between splits
"""

import os
import sys
import random
import unicodedata
import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

AP_MUNICIPALITIES = [
    {'name': 'Vijayawada Municipal Corporation (VMC)', 'district': 'NTR', 'code': 'VMC'},
    {'name': 'Greater Visakhapatnam Municipal Corporation (GVMC)', 'district': 'Visakhapatnam', 'code': 'GVMC'},
    {'name': 'Guntur Municipal Corporation (GMC)', 'district': 'Guntur', 'code': 'GMC'},
    {'name': 'Tirupati Municipal Corporation (TMC)', 'district': 'Tirupati', 'code': 'TMC'},
    {'name': 'Eluru Municipal Corporation', 'district': 'Eluru', 'code': 'ELR'},
    {'name': 'Kakinada Municipal Corporation', 'district': 'Kakinada', 'code': 'KKD'},
    {'name': 'Kurnool Municipal Corporation', 'district': 'Kurnool', 'code': 'KMC'},
    {'name': 'Nellore Municipal Corporation', 'district': 'SPSR Nellore', 'code': 'NMC'}
]

TAXONOMY = {
    'potholes': {'dept': 'road', 'code': 'C01', 'is_emg': False, 'sev': 3},
    'damaged_roads': {'dept': 'road', 'code': 'C02', 'is_emg': False, 'sev': 3},
    'footpath_damage': {'dept': 'road', 'code': 'C03', 'is_emg': False, 'sev': 2},
    'road_obstruction': {'dept': 'road', 'code': 'C04', 'is_emg': False, 'sev': 2},
    'drainage_overflow': {'dept': 'drainage', 'code': 'C05', 'is_emg': False, 'sev': 3},
    'blocked_drainage': {'dept': 'drainage', 'code': 'C06', 'is_emg': False, 'sev': 2},
    'open_manhole': {'dept': 'drainage', 'code': 'C07', 'is_emg': True, 'sev': 4},
    'sewage_leakage': {'dept': 'drainage', 'code': 'C08', 'is_emg': False, 'sev': 3},
    'no_water_supply': {'dept': 'water_supply', 'code': 'C09', 'is_emg': False, 'sev': 3},
    'water_contamination': {'dept': 'water_supply', 'code': 'C10', 'is_emg': True, 'sev': 4},
    'pipeline_leakage': {'dept': 'water_supply', 'code': 'C11', 'is_emg': False, 'sev': 3},
    'low_water_pressure': {'dept': 'water_supply', 'code': 'C12', 'is_emg': False, 'sev': 2},
    'street_light_failure': {'dept': 'street_lights', 'code': 'C13', 'is_emg': False, 'sev': 2},
    'damaged_electric_pole': {'dept': 'street_lights', 'code': 'C14', 'is_emg': True, 'sev': 4},
    'exposed_electrical_wires': {'dept': 'street_lights', 'code': 'C15', 'is_emg': True, 'sev': 4},
    'garbage_accumulation': {'dept': 'others', 'code': 'C16', 'is_emg': False, 'sev': 2},
    'garbage_collection_failure': {'dept': 'others', 'code': 'C17', 'is_emg': False, 'sev': 2},
    'dead_animal_removal': {'dept': 'others', 'code': 'C18', 'is_emg': True, 'sev': 3},
    'public_sanitation_issue': {'dept': 'others', 'code': 'C19', 'is_emg': False, 'sev': 2},
    'other_civic_issue': {'dept': 'others', 'code': 'C20', 'is_emg': False, 'sev': 2}
}

# 15 distinct incident clusters per complaint type (300 distinct clusters total)
# Each cluster contains:
# - multiple natural English formulations
# - multiple natural Native Telugu formulations
# - multiple natural Romanized Telugu (Telugu-Latin) formulations
# - code-mixed / informal variations

RAW_INCIDENTS = {
    # ==================== ROADS (road) ====================
    'potholes': [
        {
            'cluster_id': 'CL_RD_POT_01',
            'en': ["Deep crater formed on main arterial road causing two-wheeler skids", "Severe potholes on the main road, bikes are slipping at night", "Huge crater in middle of road after monsoon showers, please patch"],
            'te': ["ప్రధాన రహదారిపై భారీ గుంతలు పడ్డాయి బైకులు జారి పడుతున్నాయి", "రోడ్డు మధ్యలో పెద్ద గుంత ఏర్పడింది వాహనదారులు తీవ్ర ఇబ్బంది పడుతున్నారు", "నిన్న రాత్రి బైకర్ గుంతలో పడి గాయపడ్డాడు వెంటనే ప్యాచ్ వర్క్ చేయండి"],
            'te_latn': ["Main road meeda pedda guntalu paddayi bikes slip avtunnayi", "Road madhyalo huge crater valla night time accidents jarugutunnayi", "Road paina gundalu paddayi patch work urgent ga cheyandi"]
        },
        {
            'cluster_id': 'CL_RD_POT_02',
            'en': ["Flyover approach descent has hazardous potholes, speed control impossible", "Dangerous potholes at the flyover down-ramp leading to sudden braking", "Vehicles losing control while coming down flyover due to cluster of potholes"],
            'te': ["ఫ్లైఓవర్ దిగే ర్యాంప్ వద్ద ప్రమాదకర గుంతలు పడ్డాయి బ్రేకులు వేయలేకపోతున్నారు", "వంతెన దిగువన రోడ్డు ఛిద్రమైంది వాహనాలు అదుపుతప్పుతున్నాయి", "ఫ్లైఓవర్ సర్వీస్ రోడ్డు అంతా గోతులతో నిండిపోయింది ప్రమాదాలు జరుగుతున్నాయి"],
            'te_latn': ["Flyover dige ramp daggara hazardous potholes paddayi control avvatledu", "Bridge slope paina dangerous guntalu valla vehicles skid avtunnayi", "Flyover down ramp service road lo pedda potholes repair fast"]
        },
        {
            'cluster_id': 'CL_RD_POT_03',
            'en': ["Colony bus route road completely deteriorated with water-filled potholes", "Monsoon rain filled colony potholes making depth deceptive for commuters", "Auto-rickshaws getting overturned due to hidden deep potholes on transit route"],
            'te': ["కాలనీ బస్సు రూట్ రోడ్డుపై నీటితో నిండిన గుంతలు ఉన్నాయి ఆటోలు బోల్తా పడుతున్నాయి", "వర్షపు నీరు చేరి గుంతల లోతు తెలియడం లేదు ప్రయాణికులు పడిపోతున్నారు", "బస్సు రూట్ లో రోడ్డు అంతా గోతులమయంగా మారింది మరమ్మతులు చేపట్టాలి"],
            'te_latn': ["Colony bus route road motham water filled guntalu auto overturn ayindi", "Rain water valla potholes depth teliyatledu two wheelers fall avtunnaru", "Bus transit line lo deep potholes repair cheyandi"]
        },
        {
            'cluster_id': 'CL_RD_POT_04',
            'en': ["Multiple small potholes merged into a massive road trench near market", "Market entry road is riddled with deep cavities damaging vehicle suspensions", "Road surface craters outside vegetable rythu bazaar creating total chaos"],
            'te': ["మార్కెట్ ప్రవేశ రహదారి వద్ద గుంతలు కలిసిపోయి పెద్ద కందకంగా మారింది", "రైతు బజార్ ఎదురుగా రోడ్డుపై వరుస గుంతలు ఏర్పడి ట్రాఫిక్ నిలిచిపోయింది", "మార్కెట్ వీధి రోడ్డు గుంతలతో దెబ్బతింది వాహనాలు పాడవుతున్నాయి"],
            'te_latn': ["Market entry daggara anni guntalu kalisi pedda trench la marindi", "Rythu bazaar eduruga road meeda multiple potholes traffic blocked", "Market road lo vehicle suspensions break avtunnayi craters valla"]
        },
        {
            'cluster_id': 'CL_RD_POT_05',
            'en': ["Fresh asphalt laid last month already washed away leaving jagged holes", "Substandard road patch work eroded after single shower leaving sharp edges", "Quality check required for new road: sharp pit holes emerged within weeks"],
            'te': ["మొన్న వేసిన తారు రోడ్డు వర్షానికి కొట్టుకుపోయి వాడిగల గుంతలు పడ్డాయి", "నాసిరకం ప్యాచ్ వర్క్ వల్ల రోడ్డుపై మళ్లీ గుంతలు తేలాయి నాణ్యత పరిశీలించండి", "కొత్తగా వేసిన రోడ్డుపై నెలలోనే గుంతలు ఏర్పడ్డాయి విచారణ చేపట్టాలి"],
            'te_latn': ["Last month vesina tar road rain ki kottukupoyi sharp guntalu vachayi", "Low quality patch work single rain ke wash out ayindi investigate cheyandi", "Kotha road meeda within weeks deep holes paddayi"]
        },
        {
            'cluster_id': 'CL_RD_POT_06',
            'en': ["School zone road has dangerous potholes where school buses get stuck", "Potholes right in front of primary school gate posing danger to students", "School vans struggling to navigate craters on school lane repair urgently"],
            'te': ["స్కూలు గేటు ఎదురుగా ఉన్న రోడ్డుపై ప్రమాదకర గుంతలు పడ్డాయి బస్సులు దిగబడుతున్నాయి", "పాఠశాల వీధిలో గోతులు ఏర్పడి విద్యార్థులు నడవడానికి ఇబ్బంది పడుతున్నారు", "స్కూల్ వ్యాన్లు గుంతల్లో ఇరుక్కుపోతున్నాయి తక్షణమే బాగు చేయించండి"],
            'te_latn': ["School gate eduruga dangerous guntalu paddayi buses stuck avtunnayi", "School lane lo deep craters students walking ki chala risk repair soon", "Pillala school daggara road pothole fill cheyandi urgent"]
        },
        {
            'cluster_id': 'CL_RD_POT_07',
            'en': ["Hospital emergency ambulance corridor blocked by series of potholes", "Ambulances facing severe jolts carrying trauma patients due to bad road craters", "Critical patients getting injured inside emergency vans on hospital route holes"],
            'te': ["ఆసుపత్రి ఎమర్జెన్సీ దారిలో గుంతలు ఉండటంతో అంబులెన్సులు వేగంగా వెళ్లలేకపోతున్నాయి", "రోగులను తీసుకెళ్లే అంబులెన్సులు రోడ్డు గుంతల వల్ల కుదుపులకు గురవుతున్నాయి", "హాస్పిటల్ అప్రోచ్ రోడ్డులోని గోతులను తక్షణమే పూడ్చాలి"],
            'te_latn': ["Hospital emergency ambulance route lo series of potholes valla late avtundi", "Ambulance trauma patients chala suffer avtunnaru road craters valla", "Hospital daggara road meeda guntalu ventane patch cheyandi"]
        },
        {
            'cluster_id': 'CL_RD_POT_08',
            'en': ["Unmarked speed bump with eroded edges functioning like an inverted pothole", "Damaged speed breaker concrete exposed causing bike accidents", "Broken speed breaker on colony main road has deep gap around it"],
            'te': ["స్పీడ్ బ్రేకర్ పక్కన రోడ్డు కుంగిపోయి లోతైన గుంత ఏర్పడింది", "విరిగిపోయిన స్పీడ్ బ్రేకర్ వల్ల రాత్రి పూట వాహనాలు అదుపు తప్పుతున్నాయి", "స్పీడ్ బ్రేకర్ మరమ్మతులు చేపట్టి గుంతలు పూడ్చండి"],
            'te_latn': ["Speed breaker pakka road sink ayi deep pothole formed", "Broken speed breaker iron rods and gaps valla night fall danger", "Speed bump edges damaged repair immediately"]
        },
        {
            'cluster_id': 'CL_RD_POT_09',
            'en': ["Railway station approach road full of cavities causing missed trains", "Commuters getting delayed due to deep potholes near railway terminal", "Luggage carriers and autos unable to move smoothly on station road"],
            'te': ["రైల్వే స్టేషన్ అప్రోచ్ రోడ్డుపై గోతులు ఏర్పడి ప్రయాణికులు తీవ్ర ఇబ్బందులు పడుతున్నారు", "స్టేషన్ రోడ్డులో గుంతల వల్ల ట్రాఫిక్ స్తంభించి రైళ్లు తప్పుతున్నాయి", "రైల్వే టెర్మినల్ రోడ్డును వెంటనే బీటీ ప్యాచ్ వర్క్ చేయించాలి"],
            'te_latn': ["Railway station approach road lo pedda guntalu traffic jam misses trains", "Station route lo autos vellalekapotunnayi craters clear cheyandi", "Railway terminal road repairs urgent"]
        },
        {
            'cluster_id': 'CL_RD_POT_10',
            'en': ["Ring road intersection has uneven sinkholes after water main excavation", "Trench dug across road left half-filled with loose stones creating pit", "Utility pipeline cutting left unpaved on bypass turning into mud crater"],
            'te': ["రింగ్ రోడ్డు జంక్షన్ వద్ద పైపులైన్ తవ్వి పూడ్చకుండా వదిలేయడంతో గుంత ఏర్పడింది", "పైపుల కోసం రోడ్డు తవ్విన తర్వాత సరిగ్గా మూయలేదు వాహనాలు కూరుకుపోతున్నాయి", "రోడ్డు కటింగ్ చేసిన చోట కంకర తేలి భారీ గుంతగా మారింది"],
            'te_latn': ["Ring road intersection utility trench cut chesi vadilesaru pothole formed", "Pipeline excavation tarvata road patch cheyaledu pit formed", "Road cutting place lo vehicles struck avtunnayi repair fast"]
        },
        {
            'cluster_id': 'CL_RD_POT_11',
            'en': ["Industrial estate transit lane has deep asphalt craters from heavy lorries", "Overloaded trucks broke the road surface creating wheel-deep potholes", "Heavy vehicle corridor road bitumen collapsed into deep furrows"],
            'te': ["భారీ లారీల రాకపోకల వల్ల పారిశ్రామిక వాడ రోడ్డుపై చక్రాల లోతు గుంతలు పడ్డాయి", "ఓవర్‌లోడ్ వాహనాలతో తారు రోడ్డు కుంగిపోయి పెద్ద గోతులు ఏర్పడ్డాయి", "ఇండస్ట్రియల్ ఏరియా రోడ్డు ధ్వంసమైంది మరమ్మతులు వెంటనే జరపాలి"],
            'te_latn': ["Heavy lorries valla industrial road meeda wheel-deep guntalu paddayi", "Trucks weight ki asphalt crumbles ayi craters vachayi", "Industrial estate transit route road repair cheyandi"]
        },
        {
            'cluster_id': 'CL_RD_POT_12',
            'en': ["Narrow residential street has jagged crater blocking two-way car passage", "Residential lane potholes force cars to drive on private verges", "Colony cross road pothole causes regular bumper scrapes and traffic standoff"],
            'te': ["కాలనీ సందులో రోడ్డు మధ్య గుంత పడటంతో కార్లు ఎదురెదురుగా వెళ్లలేకపోతున్నాయి", "వీధి రోడ్డుపై గోతుల వల్ల ఇళ్ల ప్రహరీ గోడల పక్కగా నడవాల్సి వస్తోంది", "సందులోని గుంతను తక్షణమే మెటల్ వేసి పూడ్చాలి"],
            'te_latn': ["Colony cross road lo narrow street pothole car bumpers scraping", "Residential lane guntalu valla traffic stuck in cross lines", "Colony sandu lo road hole fill cheyandi"]
        },
        {
            'cluster_id': 'CL_RD_POT_13',
            'en': ["Bridge expansion joint pothole causing tyre blowouts at high speeds", "Metal joint on canal bridge has exposed gap and pothole on approach", "Commuters complaining of rim damage from bridge entry cavity"],
            'te': ["వంతెన ఎక్స్‌పాన్షన్ జాయింట్ వద్ద గుంత ఏర్పడి వాహనాల టైర్లు పగిలిపోతున్నాయి", "కెనాల్ బ్రిడ్జి అప్రోచ్ వద్ద ఇనుప జాయింట్ పైకి తేలి గుంత పడింది", "బ్రిడ్జి ఎంట్రీ వద్ద ప్రమాదకర గోతిని వెంటనే సరిచేయండి"],
            'te_latn': ["Bridge expansion joint daggara pothole valla tire burst avtundi", "Canal bridge approach lo gap and hole rim damage happening", "Bridge entry road pothole repair cheyandi safety hazard"]
        },
        {
            'cluster_id': 'CL_RD_POT_14',
            'en': ["Potholes hidden under muddy water after light shower on bypass", "Muddy puddle on bypass concealing knee-deep road crater", "Motorcycles falling daily into disguised mud-filled road depression"],
            'te': ["బైపాస్ రోడ్డుపై బురద నీటి కింద గుంతలు దాగి ఉండటంతో బైకర్లు పడిపోతున్నారు", "చిన్న వర్షానికే గుంతల్లో నీరు నిలిచి లోతు కనిపించకుండా పోయింది", "బైపాస్ పై బురద గుంతల వల్ల నిత్యం ప్రమాదాలు జరుగుతున్నాయి"],
            'te_latn': ["Bypass road mud water kindha potholes unnay teliyaka falling", "Muddy puddle concealing deep crater daily bikes slipping", "Bypass road depressions clear chesi BT patch veyandi"]
        },
        {
            'cluster_id': 'CL_RD_POT_15',
            'en': ["Ghat road bend has deep cavity near cliff edge safety barrier", "Dangerous pothole on hill road hairpin curve affecting steering", "Sharp turn pothole forces vehicles onto oncoming lane on hillside road"],
            'te': ["ఘాట్ రోడ్డు మలుపు వద్ద లోతైన గుంత పడటంతో స్టీరింగ్ అదుపు తప్పుతోంది", "కొండ దారిలో ప్రమాదకర మలుపు వద్ద గోతి ఏర్పడింది రక్షణ గోడ పక్కనే ప్రమాదం", "ఘాట్ రోడ్డులోని గుంతలను యుద్ధప్రాతిపదికన పూడ్చాలి"],
            'te_latn': ["Ghat road bend daggara deep hole valla steering control miss avtundi", "Hill road curve lo pothole forces vehicles into opposite lane", "Ghat section turning point lo road pit fix cheyandi immediately"]
        }
    ],

    'damaged_roads': [
        {
            'cluster_id': 'CL_RD_DMG_01',
            'en': ["Entire tar road peeled off completely leaving dusty broken stone path", "Bitumen layer entirely eroded by rain, road reduced to bare dirt and gravel", "Asphalt washed out on colony main street, transit is extremely jarring"],
            'te': ["తారు రోడ్డు పూర్తిగా కొట్టుకుపోయి రాళ్ల దారిగా మారింది ప్రయాణం నరకంగా ఉంది", "వర్షాలకు తారు లేచిపోయి కంకర తేలింది నడవడానికి వీల్లేకుండా పోయింది", "మా వీధిలో రోడ్డు ఉపరితలం పూర్తిగా ఛిద్రమైంది కొత్త రోడ్డు వేయాలి"],
            'te_latn': ["Tar road motham peel ayindi bare gravel path la marindi", "Bitumen layer wash out ayi kankara thelindi walking chala kashtam", "Colony main street road surface entirely eroded reconstruct cheyandi"]
        },
        {
            'cluster_id': 'CL_RD_DMG_02',
            'en': ["Cement concrete road has developed massive longitudinal fractures", "CC road cracked into multiple jagged slabs with exposed iron rebar", "Reinforced concrete road cracked down the center, edges tilting dangerously"],
            'te': ["సిమెంట్ రోడ్డు మధ్యలో భారీ పగుళ్లు వచ్చి ఇనుప కడ్డీలు పైకి తేలాయి", "సీసీ రోడ్డు ముక్కలైపోయి స్లాబ్‌లు పైకి లేచాయి వాహనాలకు ప్రమాదం", "కాంక్రీట్ రోడ్డు పగుళ్ల వల్ల ద్విచక్ర వాహనాల టైర్లు కోసుకుపోతున్నాయి"],
            'te_latn': ["Cement CC road center lo pedda fractures vachayi iron rods bayataki vachayi", "CC road broken into slabs edges tilt ayyayi danger", "Concrete road cracked down middle reconstruction required"]
        },
        {
            'cluster_id': 'CL_RD_DMG_03',
            'en': ["Major sinkhole cavity formed beneath asphalt, road about to collapse", "Underground soil erosion caused asphalt to cave in by four feet", "Road surface hollowed out underneath, danger of cave-in during traffic hours"],
            'te': ["రోడ్డు కింద మట్టి కొట్టుకుపోయి భారీ సింక్‌హోల్ ఏర్పడింది ఎప్పుడైనా కూలిపోవచ్చు", "తారు రోడ్డు లోపల కుంగిపోయింది వాహనాలు వెళ్తే రోడ్డు కుప్పకూలే ప్రమాదం ఉంది", "రోడ్డు మధ్యలో నేల కుంగి పెద్ద అగాధం ఏర్పడింది అత్యవసర బారికేడ్లు పెట్టండి"],
            'te_latn': ["Road kindha soil erosion valla asphalt cave-in ayindi sinkhole", "Road surface hollowed out underground huge risk of collapse", "Main road sinking 4 feet down emergency barricades needed"]
        },
        {
            'cluster_id': 'CL_RD_DMG_04',
            'en': ["Substandard road construction quality bitumen melting and rippling", "Road surface has formed heavy waves and ruts under normal vehicle heat", "Wavy uneven road surface causing high speed vehicles to violently bounce"],
            'te': ["నాసిరకం రోడ్డు పనుల వల్ల తారు కరిగిపోయి రోడ్డు అంతా అలల మాదిరిగా మారింది", "రోడ్డు సమతలంగా లేక ఎగుడుదిగుడుగా తయారైంది వాహనాలు ఎగిరిపడుతున్నాయి", "నాణ్యత లేని కాంట్రాక్ట్ పని వల్ల రోడ్డు తారు లేచిపోయింది రీ-టెండర్ వేయాలి"],
            'te_latn': ["Substandard road work bitumen melting and uneven waves formed", "Road surface flat ga ledu wavy ruts valla vehicles bouncing", "Uneven road quality issue re-tarring cheyandi"]
        },
        {
            'cluster_id': 'CL_RD_DMG_05',
            'en': ["Road washed out alongside irrigation canal embankment", "Canal bank erosion has taken away half the road width into the water", "Canal bund road fractured and collapsing into the waterway"],
            'te': ["కాలువ గట్టు కోతకు గురై సగం రోడ్డు నీటిలో కొట్టుకుపోయింది", "కాలువ పక్కనున్న రోడ్డు కుంగిపోయింది రాకపోకలు నిలిచిపోయాయి", "గట్టు రోడ్డు కూలిపోకుండా రివెట్‌మెంట్ కట్టి రోడ్డు పునర్నిర్మించాలి"],
            'te_latn': ["Canal bank erosion valla half of the road water lo collapse ayindi", "Irrigation canal bund road washed out transit dangerous", "Canal side road broken completely repair retaining wall"]
        }
    ],

    'footpath_damage': [
        {
            'cluster_id': 'CL_RD_FTP_01',
            'en': ["Pedestrian paver blocks uprooted and shattered along shopping street", "Broken paver tiles on municipal footpath causing senior citizens to fall", "Footpath pavement broken into loose stones forcing pedestrians onto roadway"],
            'te': ["పాదచారుల ఫుట్‌పాత్ పేవర్‌బ్లాక్స్ ఊడిపోయాయి వృద్ధులు కిందపడి గాయపడుతున్నారు", "షాపింగ్ వీధిలో ఫుట్‌పాత్ టైల్స్ పగిలి నడవడానికి వీల్లేకుండా ఉంది", "కాలిబాట రాళ్లు లేచిపోయి పాదచారులు రోడ్డుపైనే నడవాల్సి వస్తోంది సరిచేయండి"],
            'te_latn': ["Pedestrian footpath paver blocks virigipoyi loose stones vachayi", "Footpath tiles broken senior citizens slip ayi padipotunnaru", "Footpath damaged forcing people to walk on busy road"]
        },
        {
            'cluster_id': 'CL_RD_FTP_02',
            'en': ["Concrete slabs over stormwater drain footpath missing or broken", "Drain covering slab collapsed along footpath creating open pit for walkers", "Dangerous cavity on pedestrian walkway due to broken concrete cover"],
            'te': ["ఫుట్‌పాత్ పై వేసిన సిమెంట్ స్లాబ్‌లు విరిగిపోయి లోతైన కాలువ కనిపిస్తోంది", "నడిచే దారిలోని స్లాబ్ కూలిపోయింది నడుస్తున్నప్పుడు పిల్లలు పడిపోయే ప్రమాదం ఉంది", "పాదచారుల బాటపై ఉన్న డ్రైనేజీ కప్పు స్లాబ్‌లను తక్షణమే మార్చాలి"],
            'te_latn': ["Footpath cement slabs broken open drain exposed pedestrians risk", "Walkway concrete slab collapsed deep pit danger for kids", "Footpath drain covering slab replace cheyandi urgent"]
        },
        {
            'cluster_id': 'CL_RD_FTP_03',
            'en': ["Commercial shops have encroached and broken municipal footpath", "Ramps built illegally by shopkeepers destroying continuous footpath grade", "Unauthorized private stairs erected over public sidewalk blocking pedestrians"],
            'te': ["దుకాణదారులు ఫుట్‌పాత్‌ను ఆక్రమించి విరగ్గొట్టారు ర్యాంప్‌లు కట్టేశారు", "కమర్షియల్ షాపుల వారు ఫుట్‌పాత్ ధ్వంసం చేసి ప్రైవేట్ మెట్లు కట్టారు", "పాదచారుల కాలిబాట ఆక్రమణలు తొలగించి ఫుట్‌పాత్‌ను పునరుద్ధరించండి"],
            'te_latn': ["Commercial shops encroached footpath and constructed illegal ramps", "Footpath broken by shop owners walking track blocked", "Sidewalk encroachment clear chesi footpath repair cheyandi"]
        }
    ],

    'road_obstruction': [
        {
            'cluster_id': 'CL_RD_OBS_01',
            'en': ["Large fallen tree branch blocking both lanes of municipal transit road", "Gale winds knocked down heavy banyan bough across road halting traffic", "Fallen tree across street preventing cars and ambulances from passing"],
            'te': ["పెద్ద చెట్టు కొమ్మ విరిగి ప్రధాన రహదారిపై పడింది రెండు దారులు మూసుకుపోయాయి", "గాలివానకు చెట్టు నేలకూలి రోడ్డుపై పడటంతో ట్రాఫిక్ పూర్తిగా స్తంభించింది", "రోడ్డుకు అడ్డంగా పడిన చెట్టు కొమ్మలను క్రేన్ తెప్పించి తొలగించండి"],
            'te_latn': ["Pedda chettu komma virigi road paina padindi traffic stopped", "Fallen tree blocking two lanes ambulances and cars unable to pass", "Tree bough across street clear cheyandi municipal squad"]
        },
        {
            'cluster_id': 'CL_RD_OBS_02',
            'en': ["Building construction material dumped on road blocking half the street", "Piles of sand and gravel unloaded on public asphalt causing accidents", "Illegal dumping of construction aggregate taking up entire lane"],
            'te': ["భవన నిర్మాణ ఇసుక మరియు కంకర రోడ్డుపై పోశారు ఒక లైన్ పూర్తిగా మూసుకుపోయింది", "రోడ్డుపై అక్రమంగా ఇసుక కుప్పలు పోయడంతో బైకులు జారి పడుతున్నాయి", "రోడ్డుపై నిల్వ ఉంచిన నిర్మాణ సామగ్రిని వెంటనే జప్తు చేసి తొలగించండి"],
            'te_latn': ["Construction sand and kankara road meeda dump chesaru lane blocked", "Sand pile on public road causing two-wheeler skids clear it", "Building materials road encroachment remove cheyandi"]
        },
        {
            'cluster_id': 'CL_RD_OBS_03',
            'en': ["Abandoned junk vehicle left rusting on road corner for months", "Unclaimed accident vehicle blocking junction visibility and traffic turn", "Old scrap auto chassis dumped on street narrowing public corridor"],
            'te': ["పాత తుక్కు వాహనాన్ని రోడ్డు మూలలో నెలల తరబడి వదిలేశారు ట్రాఫిక్ ఇబ్బంది", "నిరుపయోగంగా పడి ఉన్న పాత వాహనం వల్ల రోడ్డుపై మలుపు కనిపించడం లేదు", "రోడ్డుపై వదిలేసిన స్క్రాప్ వాహనాన్ని మున్సిపల్ క్రేన్ తో తరలించండి"],
            'te_latn': ["Abandoned scrap vehicle road corner lo vadilesaru months nundi", "Old junk car blocking road junction visibility tow away", "Unclaimed vehicle street obstruction remove urgently"]
        }
    ],

    # ==================== DRAINAGE (drainage) ====================
    'drainage_overflow': [
        {
            'cluster_id': 'CL_DR_OVF_01',
            'en': ["Black foul sewage water overflowing from open canal onto residential road", "Drainage canal overflowing with dark sludge, terrible stench in entire colony", "Raw sewage spilling out of open roadside gutter inundating front entrances"],
            'te': ["మురుగు కాలువ పొంగి నల్లటి మురుగు నీరు రోడ్డుపై ప్రవహిస్తోంది తీవ్ర దుర్వాసన", "కాలనీలోని డ్రైనేజీ నిండిపోయి ఇళ్ల ముందర నల్లటి బురద నీరు నిలిచిపోయింది", "డ్రైనేజీ పొంగి దుర్గంధం వస్తోంది ప్రజలు రోగాల బారిన పడుతున్నారు శుభ్రం చేయండి"],
            'te_latn': ["Drainage canal overflow ayi black sewage water road paina flow avtundi", "Foul smell and dirty sewage entering house gates drainage overflowing", "Colony drainage pongipoyi road motham gutter la marindi"]
        },
        {
            'cluster_id': 'CL_DR_OVF_02',
            'en': ["Light rain caused storm sewer to back up and flood commercial market", "Slightest rainfall leads to drainage chamber backflow entering ground-floor shops", "Stormwater drain overwhelmed, foul water standing two feet deep in bazaar"],
            'te': ["చిన్న వర్షానికే డ్రైనేజీ పొంగి మార్కెట్ లోని దుకాణాల్లోకి మురుగు నీరు చేరుతోంది", "వర్షపు నీటి కాలువ వెనక్కి తన్ని వ్యాపార సముదాయాల్లోకి మురుగు పారుతోంది", "మార్కెట్ లో మురుగు నీరు నిలిచి వ్యాపారులు తీవ్ర నష్టాలు ఎదుర్కొంటున్నారు"],
            'te_latn': ["Chinna rain ke drainage chamber overflow ayi shops loki vastundi", "Market area lo foul water standing 2 feet deep customer transit blocked", "Storm sewer backflow clean chesi clearing suction pettandi"]
        },
        {
            'cluster_id': 'CL_DR_OVF_03',
            'en': ["Underground sewer manhole spewing toilet wastewater onto colony street", "Sewerage pipeline geyser erupted pushing fecal effluent across the road", "Underground chamber overflow bubbling up through road joint fissures"],
            'te': ["అండర్‌గ్రౌండ్ డ్రైనేజ్ మ్యాన్‌హోల్ నుంచి టాయిలెట్ వ్యర్థాలు రోడ్డుపైకి ఉబికి వస్తున్నాయి", "సీవరేజ్ లైన్ పొంగి మురుగు నీరు ఫౌంటెన్ లా రోడ్డుపై చిమ్ముతోంది తీవ్ర కంపు", "కాలుష్య నియంత్రణ సిబ్బంది వచ్చి వెంటనే సక్కర్ మెషిన్ తో క్లియర్ చేయాలి"],
            'te_latn': ["Underground drainage manhole nundi toilet waste water reverse road paina", "Sewerage chamber bubbling up foul effluent everywhere emergency", "Underground sewer line overflow super sucker machine pampandi"]
        }
    ],

    'blocked_drainage': [
        {
            'cluster_id': 'CL_DR_BLK_01',
            'en': ["Stormwater drain choked with single-use plastic bottles and polythene", "Plastic debris and trash blocking the canal culvert preventing all outflow", "Drains heavily choked with plastic waste, stagnant water breeding mosquitoes"],
            'te': ["డ్రైనేజీ కాలువలో ప్లాస్టిక్ సీసాలు కవర్లు పేరుకుపోయి నీరు ముందుకు సాగడం లేదు", "కాలువ పూడికతో మూసుకుపోయింది నిల్వ నీటిలో లక్షలాది దోమలు పుడుతున్నాయి", "కల్వర్టు కింద ప్లాస్టిక్ చెత్త అడ్డుపడింది మునిసిపల్ సిబ్బందితో పూడిక తీయించండి"],
            'te_latn': ["Drainage canal lo plastic bottles and garbage block ayi water flow stopped", "Choked drain stagnant black water mosquitoes chala ekkuva ayyayi", "Canal culvert lo plastic waste block clear cheyandi immediately"]
        },
        {
            'cluster_id': 'CL_DR_BLK_02',
            'en': ["Years of uncleaned silt and mud hardened inside main residential drain", "Drain bed elevated with solid silt deposit causing water to stagnate", "Desiltation not carried out for twelve months, drain capacity reduced to zero"],
            'te': ["కాలువలో సంవత్సరాలుగా పూడికతీయకపోవడంతో మట్టి గడ్డకట్టి నీటి మార్గం మూసుకుపోయింది", "డ్రైనేజీ కాలువ పూడికతో నిండిపోయింది మురుగు బయటకు వెళ్లడం లేదు", "శానిటరీ ఇన్‌స్పెక్టర్ పరిశీలించి జేసీబీతో పూడికతీత పనులు ప్రారంభించాలి"],
            'te_latn': ["Drainage lo years nundi silt and mud deposit ayi water stagnation", "Desiltation cheyaledu 1 year nundi canal capacity completely zero", "Colony drainage canal desilting JCB machine pampandi"]
        },
        {
            'cluster_id': 'CL_DR_BLK_03',
            'en': ["Construction cement slurry dumped into roadside gutter blocking flow", "Hardened concrete debris inside municipal drain choked all colony drainage", "Building contractors washed mortar into drain creating rock-solid block"],
            'te': ["భవన నిర్మాణ సిమెంట్ వ్యర్థాలు కాలువలో పోయడంతో సిమెంట్ గడ్డకట్టి కాలువ మూసుకుపోయింది", "డ్రైనేజీలో కాంక్రీట్ చెత్త వేయడం వల్ల మురుగు నీటి ప్రవాహం పూర్తిగా ఆగిపోయింది", "కాలువను ధ్వంసం చేసిన కాంట్రాక్టర్ పై చర్యలు తీసుకుని బ్లాక్ తొలగించండి"],
            'te_latn': ["Construction cement slurry drain lo dump chesaru concrete block ayindi", "Hardened mortar inside municipal gutter completely choked flow", "Contractor cement waste block in drainage clear immediately"]
        }
    ],

    'open_manhole': [
        {
            'cluster_id': 'CL_DR_MNH_01',
            'en': ["Open uncovered manhole on pedestrian path, extreme life-safety death trap", "Manhole lid missing on street right outside primary school, children at risk", "Deep open sewer pit with zero warning barricades on dark colony street"],
            'te': ["పాదచారుల దారిలో మ్యాన్‌హోల్ మూత లేకుండా తెరిచి ఉంది ప్రాణాపాయం పొంచి ఉంది", "స్కూలు బయటే డ్రైనేజీ గుంత తెరిచి ఉంది పిల్లలు పడిపోయే ప్రమాదం ఉంది", "రాత్రి సమయంలో ఎవరైనా పడితే చనిపోతారు వెంటనే కొత్త సిమెంట్ మూత వేయండి"],
            'te_latn': ["Open manhole on pedestrian path no cover extreme life safety hazard", "School bayate manhole lid ledu kids play area danger cement lid veyandi", "Deep open sewer pit in colony night time death trap fit cover urgently"]
        },
        {
            'cluster_id': 'CL_DR_MNH_02',
            'en': ["Heavy vehicle fractured cement manhole lid leaving gaping jagged hole", "Truck ran over manhole breaking concrete slab, vehicle wheels falling in", "Cracked manhole frame unstable, slab slips whenever two-wheelers ride over"],
            'te': ["భారీ వాహనం తగిలి మ్యాన్‌హోల్ మూత విరిగిపోయింది లోపలికి రంధ్రం పడింది", "డ్రైనేజీ చాంబర్ మూత పగుళ్లు ఇచ్చి వాహనాల టైర్లు గుంతలో ఇరుక్కుపోతున్నాయి", "విరిగిన మ్యాన్‌హోల్ స్లాబ్ ను తొలగించి దృఢమైన ఐరన్ లేదా సీసీ కవర్ అమర్చండి"],
            'te_latn': ["Heavy vehicle hit chesi manhole cement lid break ayindi vehicle wheels stuck", "Manhole cover cracked open hole vehicle accidents happening", "Replace broken manhole frame with heavy duty cast iron lid"]
        },
        {
            'cluster_id': 'CL_DR_MNH_03',
            'en': ["Drainage cleaning crew removed manhole slab yesterday and left without covering", "Sanitation workers opened sewer chamber and left site without safety barriers", "Open manhole left unattended after desilting work in middle of traffic road"],
            'te': ["నిన్న కాలువ క్లీన్ చేయడానికి మ్యాన్‌హోల్ మూత తీసి అలాగే వదిలేసి వెళ్ళిపోయారు", "మునిసిపల్ సిబ్బంది మ్యాన్‌హోల్ తెరిచి బారికేడ్ పెట్టకుండా నిర్లక్ష్యంగా వదిలారు", "రోడ్డు మధ్యలో తెరిచి ఉన్న మ్యాన్‌హోల్ ను తక్షణమే మూసివేయించాలి"],
            'te_latn': ["Cleaning crew manhole lid remove chesi unattended vadilesaru danger", "Sanitation workers left open sewer chamber without barricades on road", "Open manhole road middle lo undi immediately cover pettandi"]
        }
    ],

    'sewage_leakage': [
        {
            'cluster_id': 'CL_DR_SWG_01',
            'en': ["Underground sewer main pipe fractured leaking sewage onto drinking pipeline", "Sewage leaking underground and contaminating nearby clean water distribution lines", "Cross contamination hazard: burst sewer pipe seeping into groundwater"],
            'te': ["భూగర్భ సీవరేజ్ పైపు పగిలి పక్కనే ఉన్న తాగునీటి పైపుల్లోకి మురుగు నీరు కలుస్తోంది", "సీవరేజ్ లైన్ పగిలి రోడ్డు కింద నుండి మురికి నీరు పైకి ఉబికి వస్తోంది", "తాగునీరు కలుషితం కాకముందే సీవరేజ్ పైపు లీకేజీని అరికట్టండి"],
            'te_latn': ["Underground sewer line leak ayi adjacent drinking water pipe contamination danger", "Burst sewer pipe seeping filthy water onto colony road and foundation", "Sewage pipeline fracture urgent repair required disease outbreak risk"]
        },
        {
            'cluster_id': 'CL_DR_SWG_02',
            'en': ["Sewage chamber joint eroded, continuous toxic liquid pooling by houses", "Joint between drainage pipes separated, continuous foul effluent leaking", "Sewage seepage penetrating residential compound walls causing structural rot"],
            'te': ["డ్రైనేజీ పైపుల జాయింట్ ఊడిపోయి మురుగు నీరు నిరంతరం ఇళ్ల గోడల పక్కగా కారుతోంది", "మురుగునీటి సీపేజ్ వల్ల కాంపౌండ్ వాల్స్ దెబ్బతిని భవనాలు బీటలు వారుతున్నాయి", "డ్రైనేజీ చాంబర్ జాయింట్ ను రిపేర్ చేసి లీకేజీని శాశ్వతంగా ఆపండి"],
            'te_latn': ["Drainage pipe joint disconnected continuous sewage pooling near houses", "Sewage seepage entering house compound walls damage happening", "Sewer chamber joint cement sealing repair cheyandi"]
        }
    ],

    # ==================== WATER SUPPLY (water_supply) ====================
    'no_water_supply': [
        {
            'cluster_id': 'CL_WS_NOW_01',
            'en': ["Zero municipal drinking water supply in our ward for past five days", "No tap water since Monday, residents forced to buy private water tankers", "Complete water outage in colony for over 96 hours, severe humanitarian crisis"],
            'te': ["గత ఐదు రోజులుగా మా వార్డులో మునిసిపల్ తాగునీటి సరఫరా పూర్తిగా నిలిచిపోయింది", "కుళాయిల్లో బొట్టు నీరు రావడం లేదు ప్రైవేట్ వాటర్ కొనుక్కోలేక ప్రజలు అల్లాడుతున్నారు", "నాలుగు రోజులుగా నీళ్లు లేక కాలనీ ప్రజలు తీవ్ర ఇబ్బందులు పడుతున్నారు ట్యాంకర్లు పంపండి"],
            'te_latn': ["Past 5 days nundi municipal drinking water supply zero taps completely dry", "One drop water kuda ravadam ledu colony people suffering buy private tankers", "No water supply since 4 days emergency water tanker supply cheyandi"]
        },
        {
            'cluster_id': 'CL_WS_NOW_02',
            'en': ["Public borewell motor burnt out, low-income slum layout left without water", "Community water pump burned due to voltage spike, taps totally dead", "Submersible water motor failed in municipal water pump house repair immediately"],
            'te': ["మునిసిపల్ బోరు మోటారు కాలిపోయింది పేదల కాలనీలో నీరందక అవస్థలు పడుతున్నారు", "వోల్టేజ్ సమస్యతో వాటర్ పంప్ మోటార్ పాడైంది కుళాయిలకు నీరు చేరడం లేదు", "వాటర్ వర్క్స్ అధికారులు స్పందించి కొత్త మోటారు అమర్చాలి లేదా రిపేర్ చేయాలి"],
            'te_latn': ["Borewell pump motor burn ayindi taps lo water stop ayindi", "Community water motor damaged voltage issue repair fast or tanker send", "Public drinking water motor failure replace motor immediately"]
        },
        {
            'cluster_id': 'CL_WS_NOW_03',
            'en': ["Main water distribution line valve closed by maintenance crew and not restored", "Water valve operator forgot to open sluice valve to our residential pocket", "Valve breakdown halting clean water flow to more than four hundred families"],
            'te': ["వాటర్ వర్క్స్ సిబ్బంది వాల్వ్ కట్టేసి తిరిగి తెరవడం మరిచిపోవడంతో సరఫరా ఆగింది", "మా వీధికి వచ్చే మెయిన్ వాటర్ వాల్వ్ పాడైపోయింది నీరు రావడం లేదు", "వాటర్ వాల్వ్ సరిచేసి కాలనీకి తాగునీటి సరఫరాను పునరుద్ధరించండి"],
            'te_latn': ["Water distribution valve closed and not opened supply halted to colony", "Main water sluice valve repair cheyandi water reach avvatledu", "Water valve operator issue taps empty since two days check line"]
        }
    ],

    'water_contamination': [
        {
            'cluster_id': 'CL_WS_CNT_01',
            'en': ["Tap water coming out dark black and foul-smelling like gutter sludge", "Municipal tap water mixed with sewage, highly toxic contaminated liquid", "Drinking water supplied is cloudy brown with sewage odor, children falling sick"],
            'te': ["కుళాయిల్లో నల్లటి మురికి నీరు వస్తోంది డ్రైనేజీ కంపు తాగడానికి వీల్లేదు", "మునిసిపల్ కుళాయి నీరు డ్రైనేజీ కలిసి కలుషితమైంది పిల్లలు వాంతులు చేసుకుంటున్నారు", "కలుషిత నీరు తాగడం వల్ల కాలనీలో కలరా ప్రబలే ప్రమాదం ఉంది వెంటనే సరఫరా ఆపండి"],
            'te_latn': ["Taps lo black dirty water vastundi sewage foul smell panikiradu", "Municipal tap water mixed with drainage highly contaminated disease risk", "Drinking water dirty brown smell valla vomiting and illness stop supply"]
        },
        {
            'cluster_id': 'CL_WS_CNT_02',
            'en': ["Municipal overhead reservoir tank filled with green algae and dead worms", "Overhead water storage tank not cleaned for six months, worms coming from taps", "Visible debris and insect larvae observed in municipal tap drinking water"],
            'te': ["ఓవర్‌హెడ్ వాటర్ ట్యాంక్ క్లీన్ చేయకపోవడం వల్ల కుళాయి నీటిలో పురుగులు వస్తున్నాయి", "నీటి ట్యాంకులో నాచు పేరుకుపోయింది నీటిలో పచ్చటి రంగు దుర్వాసన వస్తోంది", "మున్సిపల్ రిజర్వాయర్ ట్యాంక్ ను బ్లీచింగ్ తో శుభ్రం చేసి క్లోరినేషన్ జరపండి"],
            'te_latn': ["Overhead water tank not cleaned worms and insects coming from taps", "Water tank full of green algae contaminated water tap supply", "Clean overhead water reservoir with bleaching and chlorination fast"]
        },
        {
            'cluster_id': 'CL_WS_CNT_03',
            'en': ["Excess chlorine chemical overdose in tap water causing burning eyes and throat", "Severe chemical chemical smell in tap water unfit for drinking or cooking", "Water bleaching powder overdose causing skin rashes and burning sensation"],
            'te': ["మునిసిపల్ నీటిలో బ్లీచింగ్ మరియు క్లోరిన్ మోతాదు ఎక్కువై ఘాటైన వాసన వస్తోంది", "నీరు తాగితే గొంతు మంట చర్మ వ్యాధులు వస్తున్నాయి క్లోరిన్ లెవల్స్ సరిచూడండి", "కుళాయి నీటిలో రసాయన వాసన వస్తోంది వాటర్ క్వాలిటీ టెస్ట్ చేయించాలి"],
            'te_latn': ["Excess chlorine overdose in municipal taps burning throat and smell", "Tap water chemical smell too strong unable to drink or cook", "Bleaching chemical heavy overdose in drinking water inspect quality"]
        }
    ],

    'pipeline_leakage': [
        {
            'cluster_id': 'CL_WS_LKG_01',
            'en': ["Major underground water main burst flooding street with thousands of liters", "High pressure drinking water pipe burst, clean water gushing 10 feet into air", "Main feeder pipeline split open road inundated with precious drinking water"],
            'te': ["ప్రధాన మంచినీటి పైపులైన్ పగిలి వేలాది లీటర్ల తాగునీరు రోడ్డుపై వృధాగా పోతోంది", "హై ప్రెజర్ వాటర్ పైపు పగిలి మంచి నీరు వరదలా వీధుల్లో పారుతోంది", "రోడ్డు కింద ఉన్న తాగునీటి మెయిన్ పైపు లీకేజీని అత్యవసరంగా అరికట్టండి"],
            'te_latn': ["Main drinking water pipe burst clean water gushing out onto road waste", "Underground water main ruptured thousands of liters drinking water wasted", "Water pipeline burst flood on street turn off supply valve and repair"]
        },
        {
            'cluster_id': 'CL_WS_LKG_02',
            'en': ["Public street standpost faucet broken, clean water leaking non-stop into gutter", "Public street tap valve sheared off, water flowing 24/7 causing muddy sludge", "Damaged municipal public tap leaking continuous fresh water onto road"],
            'te': ["వీధి కుళాయి విరిగిపోయి మంచి నీరు నిరంతరం రోడ్డుపై కాలువలా ప్రవహిస్తోంది", "పబ్లిక్ ట్యాప్ వాల్వ్ పాడైపోయింది నీరు రోజంతా కారి బురదమయంగా మారింది", "కుళాయికి కొత్త ట్యాప్ బిగించి తాగునీటి వృధాను అరికట్టండి"],
            'te_latn': ["Public street tap broken water leaking continuously into roadside mud", "Public standpost faucet broken non stop fresh water wastage", "Street public tap valve replace cheyandi water wasting"]
        }
    ],

    'low_water_pressure': [
        {
            'cluster_id': 'CL_WS_PRS_01',
            'en': ["Extremely feeble water pressure in colony, takes one hour to fill single bucket", "Tap water trickles in drops, motor unable to draw water to storage tank", "Low pipeline pressure in tail-end residential layout, upper floors totally dry"],
            'te': ["కుళాయిల్లో నీటి ప్రెజర్ చాలా తక్కువగా ఉంది బిందెడు నీళ్లు పట్టడానికి గంట పడుతోంది", "మోటార్ వేసినా నీరు రావడం లేదు కేవలం బొట్లు బొట్లుగా మాత్రమే పడుతోంది", "కాలనీ చివరి ఇళ్లకు నీటి ప్రెజర్ సరిపోవడం లేదు ప్రెజర్ పెంచాలి"],
            'te_latn': ["Taps lo water pressure very low drops matrame padutunnayi one bucket takes 1 hour", "Water pressure zero motor vesina water lift kavadam ledu", "Tail end houses water pressure low booster pump check cheyandi"]
        },
        {
            'cluster_id': 'CL_WS_PRS_02',
            'en': ["Air lock in underground distribution pipeline causing zero water pressure", "Pipeline clogged with calcium scaling restricting water flow to residential lane", "Air release valve damaged resulting in air pocket blocking water pressure"],
            'te': ["పైప్‌లైన్ లో ఎయిర్ లాక్ పడటంతో నీటి ప్రవాహం ఆగిపోయింది ప్రెజర్ రావడం లేదు", "పైపుల్లో గాలి చేరింది వాటర్ వర్క్స్ ప్లంబర్ వచ్చి ఎయిర్ రిలీజ్ చేయాలి", "పైప్‌లైన్ జామ్ అయి నీరు చాలినంతగా రావడం లేదు పరిశీలించండి"],
            'te_latn': ["Pipeline air lock valla zero water pressure plumbers air release cheyandi", "Underground pipe air lock water not coming with force check lines", "Air valve issue in drinking water pipe lines inspect pressure"]
        }
    ],

    # ==================== ELECTRICAL & STREET LIGHTING (street_lights) ====================
    'street_light_failure': [
        {
            'cluster_id': 'CL_EL_FLR_01',
            'en': ["All street lights on entire bypass road dark for past two weeks", "Ten consecutive LED street lights not turning on, complete pitch darkness", "Street lighting blackout along colony road leading to chain snatching fear"],
            'te': ["మా కాలనీలో అన్ని వీధి దీపాలు వెలగడం లేదు రాత్రిపూట అంతా చిమ్మచీకటిగా ఉంది", "రెండు వారాలుగా వీధి లైట్లు పాడైపోయాయి మహిళలు రాత్రి నడవడానికి భయపడుతున్నారు", "ఎల్ఈడీ వీధి లైట్లు ఆరిపోయాయి వెంటనే కొత్త బల్బులు వేయించండి"],
            'te_latn': ["Colony lo all street lights 2 weeks nundi velagadam ledu pitch dark", "LED street lights not working theft and snatching fear in dark", "Street light switch repair cheyandi night time total darkness"]
        },
        {
            'cluster_id': 'CL_EL_FLR_02',
            'en': ["Street light fixture flickering rapidly and making buzzing electrical noise", "Faulty choke in street light pole causing strobe flickering all night", "Defective LED luminaire sparking intermittently in front of residential house"],
            'te': ["వీధి లైట్ బల్బు మినుకు మినుకుమంటూ సౌండ్ వస్తోంది ఎప్పుడైనా పేలిపోవచ్చు", "స్తంభంపై ఉన్న లైట్ నిరంతరం బజ్జింగ్ శబ్దంతో మినుకుమినుకుమంటోంది", "లైట్ ఫిక్చర్ పాడైపోయింది ఎలక్ట్రికల్ టీమ్ వచ్చి బల్బు మార్చాలి"],
            'te_latn': ["Street light flickering continuously buzzing sound danger", "Faulty choke lamp blinking all night disturbing residents replace bulb", "Street light sparking and blinking fix electrical fixture"]
        },
        {
            'cluster_id': 'CL_EL_FLR_03',
            'en': ["Street lights continuously burning in bright broad daylight for ten days", "Daytime street lighting waste of municipal public electricity", "Automatic daylight sensor timer defective, lamps stay on 24 hours a day"],
            'te': ["పగటిపూట కూడా వీధి లైట్లు ఆపకుండా వెలుగుతున్నాయి విద్యుత్ వృధా అవుతోంది", "టైమర్ స్విచ్ పాడైపోయి 24 గంటలూ లైట్లు వెలుగుతూనే ఉన్నాయి సరిచేయండి", "పగటివేళ లైట్లు ఆఫ్ చేయించేలా మునిసిపల్ విద్యుత్ విభాగం చర్యలు తీసుకోవాలి"],
            'te_latn': ["Daytime kuda street lights 24 hours on electricity wastage", "Timer switch defective daylight sensor not working lamps on in sun", "Day time lights turn off cheyandi automatic timer repair"]
        }
    ],

    'damaged_electric_pole': [
        {
            'cluster_id': 'CL_EL_POL_01',
            'en': ["Concrete street light pole broken at base and leaning 45 degrees over traffic", "Cracked electric pole ready to collapse onto road, extreme emergency", "Vehicle rammed into electrical mast, concrete shattered with reinforcement bent"],
            'te': ["విద్యుత్ స్తంభం అడుగుభాగంలో విరిగిపోయి రోడ్డుపైకి ప్రమాదకరంగా వంగిపోయింది", "కరెంట్ స్తంభం ఎప్పుడైనా రోడ్డుపై పడిపోయేలా ఉంది తక్షణమే మార్చాలి", "లారీ ఢీకొట్టడంతో విద్యుత్ స్తంభం విరిగింది అత్యవసరంగా విద్యుత్ సరఫరా ఆపి కొత్తది వేయండి"],
            'te_latn': ["Electric pole base broken leaning dangerously over road can fall anytime", "Concrete current pole cracked 45 degrees emergency replace new pole", "Vehicle hit electric post ready to collapse power cut and replace pole"]
        },
        {
            'cluster_id': 'CL_EL_POL_02',
            'en': ["Rusted hollow steel light pole corroded completely through at ground level", "Iron light pole severely rusted by dog urine about to topple in gusty wind", "Metal electrical pole wobbling dangerously near bus stop shelter"],
            'te': ["ఇనుప వీధి లైట్ స్తంభం తుప్పు పట్టి కింద పగిలిపోయింది గాలి వేస్తే పడిపోతుంది", "బస్టాండ్ వద్ద ఉన్న కరెంట్ స్తంభం తుప్పుపట్టి ఊగుతోంది ప్రజల ప్రాణాలకు ముప్పు", "తుప్పు పట్టిన స్తంభాన్ని తొలగించి కొత్త కాంక్రీట్ స్తంభం వేయించండి"],
            'te_latn': ["Rusted iron light pole completely corroded at base wobbling", "Metal electric pole broken near bus stand topple danger replace fast", "Iron street light pole base rusted wind valla collapse risk"]
        }
    ],

    'exposed_electrical_wires': [
        {
            'cluster_id': 'CL_EL_WIR_01',
            'en': ["Live high voltage overhead electric wire snapped and hanging at head height", "Snapped live current wire dangling over water puddle on street, sparking", "Exposed electrical conductor fell onto metal gate, fatal electrocution danger"],
            'te': ["లైవ్ కరెంట్ తీగ తెగి రోడ్డుపై తల ఎత్తులో వేలాడుతోంది స్పార్క్ వస్తోంది", "కరెంట్ వైర్ తెగి వర్షపు నీటి గుంతలో పడింది ముట్టుకుంటే ప్రాణాపాయం", "విద్యుత్ సరఫరా వెంటనే నిలిపివేసి తెగిన తీగను పునరుద్ధరించండి అత్యవసరం"],
            'te_latn': ["Live current wire snapped and dangling at head height sparking emergency", "Current wire tegipoyi road water puddle lo padindi fatal shock hazard", "Live high voltage electric wire down cut power and fix urgently"]
        },
        {
            'cluster_id': 'CL_EL_WIR_02',
            'en': ["Electrical junction junction box at bottom of pole open with bare terminals", "Open pole junction box with live bare copper wires reachable by small children", "Street light pillar box door broken off, exposed wiring during monsoon rains"],
            'te': ["విద్యుత్ స్తంభం కింద ఉన్న జంక్షన్ బాక్స్ మూత లేకుండా తెరిచి ఉంది పిల్లలు తిరుగుతున్నారు", "లైవ్ కరెంట్ వైర్లు బాక్స్ బయటకు వచ్చి ఉన్నాయి వర్షం పడితే షాక్ కొడుతుంది", "జంక్షన్ బాక్స్ కు వెంటనే డోర్ వేసి లాక్ చేయండి ప్రమాదం జరగకముందే"],
            'te_latn': ["Electric pole junction box open bare live terminals reachable by kids", "Junction box cover broken live copper wires exposed in rain danger", "Pole control box lock chesi live wires insulate cheyandi"]
        }
    ],

    # ==================== SANITATION & SOLID WASTE (others) ====================
    'garbage_accumulation': [
        {
            'cluster_id': 'CL_SN_ACC_01',
            'en': ["Massive pile of rotting municipal garbage dumped on residential road corner", "Rotting trash heap scattered by stray pigs and dogs emitting unbearable stench", "Garbage accumulated for over ten days turning colony corner into illegal dumping yard"],
            'te': ["రోడ్డు మూలలో కొండలా చెత్త కుప్పలు పేరుకుపోయాయి వీధి కుక్కలు చెల్లాచెదురు చేస్తున్నాయి", "కుళ్ళిన ఆహార వ్యర్థాలతో దుర్వాసన భరించలేకపోతున్నాం ఈగలు ముసురుతున్నాయి", "పారిశుద్ధ్య సిబ్బందిని పంపించి జేసీబీతో చెత్త కుప్పను ఎత్తించి బ్లీచింగ్ చల్లించండి"],
            'te_latn': ["Road corner lo huge garbage pile accumulated dogs scattering foul smell", "Rotting waste heap bad smell mosquito menace send sanitation squad", "Chetha kuppalu road meeda dump chesaru clear chesi bleaching powder challandi"]
        },
        {
            'cluster_id': 'CL_SN_ACC_02',
            'en': ["Municipal community trash bin overflowed, waste spilling across road", "Broken green municipal dumpster overflowing, traffic forced onto sidewalk", "Public dumper bin overflowing with domestic refuse blocking street drain"],
            'te': ["మునిసిపల్ చెత్త డబ్బా నిండిపోయి చెత్త అంతా రోడ్డుపై పడిపోయింది వాహనాలు వెళ్లలేకపోతున్నాయి", "చెత్త కుండీ పగిలి వ్యర్థాలు బయటకు పారుతున్నాయి కొత్త చెత్త డబ్బా ఏర్పాటు చేయండి", "చెత్త డబ్బాను రోజువారీగా ఖాళీ చేయించాల్సిందిగా శానిటేషన్ విభాగాన్ని కోరుతున్నాం"],
            'te_latn': ["Municipal dustbin overflowing waste spilled on road vehicles unable to pass", "Broken dumper bin garbage scattering on street replace new bin", "Municipal garbage bin empty cheyandi daily basis"]
        }
    ],

    'garbage_collection_failure': [
        {
            'cluster_id': 'CL_SN_COL_01',
            'en': ["Door-to-door municipal garbage collection vehicle not visited for eight days", "Sanitation auto has skipped our street completely for over one week", "Household waste rotting in residential compounds because collection cart absent"],
            'te': ["ఇంటింటికీ చెత్త సేకరించే ఆటో గత ఎనిమిది రోజులుగా మా వీధికి రావడం లేదు", "శానిటేషన్ సిబ్బంది చెత్త సేకరణ మానేశారు ఇళ్లలో చెత్త నిల్వ ఉండి కంపుకొడుతోంది", "క్రమం తప్పకుండా ప్రతిరోజూ చెత్త సేకరించేలా శానిటరీ ఇన్‌స్పెక్టర్ చర్యలు తీసుకోవాలి"],
            'te_latn': ["Door to door garbage vehicle past 8 days nundi ravadam ledu waste pending", "Sanitation auto vehicle skipped our colony collection completely stopped", "Daily waste collection regularize cheyandi send municipal van"]
        },
        {
            'cluster_id': 'CL_SN_COL_02',
            'en': ["Sanitation worker refuses to collect dry segregated plastic waste", "Garbage collection staff demanding illegal private tips to collect domestic trash", "Sanitation rickshaw driver skips alternate lanes causing domestic waste build-up"],
            'te': ["పారిశుద్ధ్య కార్మికులు చెత్త సేకరణకు లంచాలు అడుగుతున్నారు విధుల్లో నిర్లక్ష్యం", "చెత్త తీసుకునే వాహనం కొన్ని సందుల్లోకి రాకుండా వెళ్లిపోతోంది ప్రజలు ఇబ్బంది పడుతున్నారు", "నిర్లక్ష్యంగా వ్యవహరిస్తున్న శానిటేషన్ సిబ్బందిపై విచారణ జరిపి చర్యలు తీసుకోండి"],
            'te_latn': ["Sanitation workers demanding private tips to collect household waste", "Garbage collection vehicle skipping inner lanes regularly resolve issue", "Sanitation staff discipline check and regularize collection"]
        }
    ],

    'dead_animal_removal': [
        {
            'cluster_id': 'CL_SN_ANM_01',
            'en': ["Dead stray dog carcass rotting on roadside near market, unbearable flies and stench", "Decomposing animal body lying on sidewalk emitting nauseating disease hazard", "Dead street animal rotting in heat near residential gates remove immediately"],
            'te': ["రోడ్డు పక్కన చనిపోయిన వీధి కుక్క కళేబరం కుళ్లిపోయి విపరీతమైన దుర్వాసన వస్తోంది", "జంతు కళేబరం కుళ్ళిపోయి ఈగలు ముసురుతున్నాయి అంటువ్యాధులు ప్రబలే ప్రమాదం ఉంది", "శానిటేషన్ ఎమర్జెన్సీ టీమ్ వెంటనే వచ్చి కుక్క కళేబరాన్ని తరలించి సున్నం వేయాలి"],
            'te_latn': ["Road side dead stray dog rotting unbearable smell and flies health risk", "Decomposing animal body on street remove immediately emergency sanitation", "Dead animal carcass lying near gate sanitation team clear fast"]
        },
        {
            'cluster_id': 'CL_SN_ANM_02',
            'en': ["Dead calf carcass dumped inside open drainage canal choking water", "Decaying animal floating in stormwater canal creating horrific neighborhood odor", "Animal remains stuck inside culvert grate remove before contamination spreads"],
            'te': ["డ్రైనేజీ కాలువలో చనిపోయిన జంతువు పడి కుళ్లిపోతోంది నీరు నిలిచిపోయింది", "కాలువలో తేలుతున్న జంతు కళేబరం వల్ల పరిసర ప్రాంతాలన్నీ దుర్గంధంతో నిండిపోయాయి", "డ్రైనేజీ నుంచి జంతు కళేబరాన్ని బయటకు తీసి లోతైన ప్రదేశంలో పూడ్చిపెట్టాలి"],
            'te_latn': ["Drainage canal lo dead calf carcass floating foul stench remove immediately", "Decaying animal stuck in drainage grate clean canal before disease spreads", "Drainage nundi dead animal carcass remove cheyandi"]
        }
    ],

    'public_sanitation_issue': [
        {
            'cluster_id': 'CL_SN_SAN_01',
            'en': ["Municipal public toilet near bus station completely filthy and unmaintained", "Public urinal overflowing with stagnant urine, water supply broken and foul stench", "Women passengers unable to use dilapidated and uncleaned municipal restroom"],
            'te': ["బస్టాండ్ వద్ద ఉన్న మునిసిపల్ పబ్లిక్ టాయిలెట్ అత్యంత అపరిశుభ్రంగా ఉంది నీటి సరఫరా లేదు", "పబ్లిక్ మూత్రశాలలు నిర్వహణ లేక కంపుకొడుతున్నాయి ప్రయాణికులు తీవ్ర ఇబ్బందులు పడుతున్నారు", "టాయిలెట్లను బ్లీచింగ్ వేసి శుభ్రం చేయించి వాటర్ ట్యాప్ రిపేర్ చేయించండి"],
            'te_latn': ["Bus stand public toilet completely filthy and foul smell no water supply", "Public urinals broken maintenance zero passengers suffering clean immediately", "Municipal public toilet clean chesi running water provide cheyandi"]
        },
        {
            'cluster_id': 'CL_SN_SAN_02',
            'en': ["Massive mosquito infestation in ward, municipal fogging and spraying required", "Dengue cases reported in colony, no bleaching powder sprinkled for months", "Stagnant pools of water breeding lakhs of mosquitoes, urgent vector control needed"],
            'te': ["కాలనీలో దోమలు విపరీతంగా పెరిగిపోయాయి డెంగ్యూ మలేరియా జ్వరాలు వస్తున్నాయి", "మునిసిపాలిటీ వారు బ్లీచింగ్ పౌడర్ చల్లి ఫాగింగ్ స్ప్రే చేయించాలని కోరుతున్నాం", "సీజనల్ వ్యాధులు ప్రబలకుండా దోమల నివారణ మందులు వెంటనే పిచికారీ చేయించండి"],
            'te_latn': ["Colony lo mosquito menace very high dengue cases reported municipal fogging needed", "Bleaching powder spraying not done since months vector control required", "Mosquito fogging vehicle send cheyandi colony motham"]
        }
    ],

    'other_civic_issue': [
        {
            'cluster_id': 'CL_SN_OTH_01',
            'en': ["Pack of aggressive stray dogs chasing two-wheelers and biting pedestrians", "Stray dog menace near primary school gate, children getting attacked", "Rabid dog roaming residential colony, dog catching vehicle squad needed"],
            'te': ["వీధి కుక్కలు గుంపులుగా చేరి బైకర్లను వెంబడిస్తున్నాయి పాదచారులను కరుస్తున్నాయి", "పాఠశాల సమీపంలో కుక్కల బెడద ఎక్కువైంది పిల్లలు బయటకు రావడానికి భయపడుతున్నారు", "మున్సిపల్ డాగ్ క్యాచింగ్ వ్యాన్ పంపించి కుక్కలను పట్టుకోవాల్సిందిగా విజ్ఞప్తి"],
            'te_latn': ["Stray dogs pack chasing bikes and biting pedestrians dog catching van needed", "Street dog menace near school kids getting attacked catch dogs urgently", "Colony lo dogs terror ekkuva ayindi municipal dog squad pampandi"]
        },
        {
            'cluster_id': 'CL_SN_OTH_02',
            'en': ["Commercial open burning of plastic waste producing suffocating toxic black smoke", "Vacant plot being used to burn chemical trash, residents having breathing issues", "Illegal bonfire of plastic bags and dry leaves in residential neighborhood"],
            'te': ["ఖాళీ స్థలంలో ప్లాస్టిక్ వ్యర్థాలను తగులబెడుతున్నారు వెలువడే విషపూరిత పొగతో ఊపిరాడటం లేదు", "రాత్రిళ్లు చెత్తను కాల్చడం వల్ల కాలనీ అంతా దట్టమైన పొగ కమ్ముకుంటోంది ఆపండి", "చెత్త కాల్చే వారిపై జరిమానా విధించి కాలుష్యాన్ని అరికట్టండి"],
            'te_latn': ["Open plot lo plastic waste burning toxic black smoke suffocating residents", "Illegal trash burning causing breathing problems stop it and fine them", "Plastic waste burning night time air pollution stop immediately"]
        }
    ]
}

def generate_records():
    records = []
    rec_id = 1
    
    # We will build rich, varied citizen instances for every cluster
    for c_type, clusters in RAW_INCIDENTS.items():
        tax = TAXONOMY[c_type]
        dept = tax['dept']
        is_emg = tax['is_emg']
        sev = tax['sev']
        
        for cluster in clusters:
            cid = cluster['cluster_id']
            ulb = random.choice(AP_MUNICIPALITIES)
            ward_num = random.randint(1, 40)
            ward_str = f"Ward {ward_num}"
            
            # English variants (3-5 per cluster)
            for en_text in cluster['en']:
                records.append({
                    'complaint_id': f"NXC_{rec_id:05d}",
                    'cluster_id': cid,
                    'complaint_text': en_text.strip(),
                    'language_style': 'en',
                    'department': dept,
                    'complaint_type': c_type,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_id += 1
                
                # Add one realistic contextualized variant with location
                loc_context = f"{en_text.strip()} (near {ulb['code']} {ward_str})"
                records.append({
                    'complaint_id': f"NXC_{rec_id:05d}",
                    'cluster_id': cid,
                    'complaint_text': loc_context,
                    'language_style': 'en',
                    'department': dept,
                    'complaint_type': c_type,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_id += 1

            # Native Telugu variants (3-5 per cluster)
            for te_text in cluster['te']:
                norm_te = unicodedata.normalize('NFC', te_text.strip())
                records.append({
                    'complaint_id': f"NXC_{rec_id:05d}",
                    'cluster_id': cid,
                    'complaint_text': norm_te,
                    'language_style': 'te',
                    'department': dept,
                    'complaint_type': c_type,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_id += 1
                
                loc_te = f"{norm_te} ({ulb['name']} పరిధిలోని వార్డు నెం.{ward_num})"
                records.append({
                    'complaint_id': f"NXC_{rec_id:05d}",
                    'cluster_id': cid,
                    'complaint_text': loc_te,
                    'language_style': 'te',
                    'department': dept,
                    'complaint_type': c_type,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_id += 1

            # Romanized Telugu variants (3-5 per cluster)
            for latn_text in cluster['te_latn']:
                records.append({
                    'complaint_id': f"NXC_{rec_id:05d}",
                    'cluster_id': cid,
                    'complaint_text': latn_text.strip(),
                    'language_style': 'te_latn',
                    'department': dept,
                    'complaint_type': c_type,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_id += 1
                
                loc_latn = f"{latn_text.strip()} ({ulb['code']} area ward {ward_num})"
                records.append({
                    'complaint_id': f"NXC_{rec_id:05d}",
                    'cluster_id': cid,
                    'complaint_text': loc_latn,
                    'language_style': 'te_latn',
                    'department': dept,
                    'complaint_type': c_type,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_id += 1

    df = pd.DataFrame(records)
    print(f"Generated raw dataset: {len(df)} records across {df['cluster_id'].nunique()} clusters.")
    
    # -------------------------------------------------------------------------
    # STRICT GROUP-BASED SPLIT (70% Train, 15% Validation, 15% Test)
    # Guaranteed 0% overlap of cluster_id or underlying template across splits!
    # -------------------------------------------------------------------------
    cluster_df = df[['cluster_id', 'department']].drop_duplicates().sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    
    train_clusters = []
    val_clusters = []
    test_clusters = []
    
    # Stratify cluster allocation by department
    for dept in df['department'].unique():
        dept_cl = cluster_df[cluster_df['department'] == dept]['cluster_id'].tolist()
        n = len(dept_cl)
        n_train = int(round(n * 0.70))
        n_val = int(round(n * 0.15))
        if n_val == 0 and n >= 3:
            n_val = 1
        n_test = n - n_train - n_val
        if n_test == 0 and n >= 3:
            n_test = 1
            n_train -= 1
            
        train_clusters.extend(dept_cl[:n_train])
        val_clusters.extend(dept_cl[n_train:n_train + n_val])
        test_clusters.extend(dept_cl[n_train + n_val:])
        
    print(f"Clusters split: {len(train_clusters)} Train, {len(val_clusters)} Val, {len(test_clusters)} Test")
    
    # Assign split tags
    def assign_split(cid):
        if cid in train_clusters:
            return 'train'
        elif cid in val_clusters:
            return 'validation'
        else:
            return 'test'
            
    df['split'] = df['cluster_id'].apply(assign_split)
    
    # Verify zero overlap
    train_texts = set(df[df['split'] == 'train']['complaint_text'].str.strip())
    val_texts = set(df[df['split'] == 'validation']['complaint_text'].str.strip())
    test_texts = set(df[df['split'] == 'test']['complaint_text'].str.strip())
    
    train_val_ov = len(train_texts.intersection(val_texts))
    train_test_ov = len(train_texts.intersection(test_texts))
    val_test_ov = len(val_texts.intersection(test_texts))
    
    print("\n--- ZERO-LEAKAGE VERIFICATION ---")
    print(f"Train & Val text overlap: {train_val_ov}")
    print(f"Train & Test text overlap: {train_test_ov}")
    print(f"Val & Test text overlap: {val_test_ov}")
    assert train_val_ov == 0 and train_test_ov == 0 and val_test_ov == 0, "DATA LEAKAGE DETECTED!"
    print("Zero leakage verified: 100% disjoint text sets across all splits.")
    
    # Save datasets
    out_dir = os.path.join("ai", "datasets", "cleaned")
    os.makedirs(out_dir, exist_ok=True)
    
    full_csv = os.path.join(out_dir, "nexciv_multilingual_cleaned.csv")
    df.to_csv(full_csv, index=False, encoding='utf-8')
    
    train_df = df[df['split'] == 'train'].reset_index(drop=True)
    val_df = df[df['split'] == 'validation'].reset_index(drop=True)
    test_df = df[df['split'] == 'test'].reset_index(drop=True)
    
    train_df.to_csv(os.path.join(out_dir, "train.csv"), index=False, encoding='utf-8')
    val_df.to_csv(os.path.join(out_dir, "validation.csv"), index=False, encoding='utf-8')
    test_df.to_csv(os.path.join(out_dir, "test.csv"), index=False, encoding='utf-8')
    
    # Also update ai/datasets/ with the cleaned versions
    train_df.to_csv(os.path.join("ai", "datasets", "train.csv"), index=False, encoding='utf-8')
    val_df.to_csv(os.path.join("ai", "datasets", "validation.csv"), index=False, encoding='utf-8')
    test_df.to_csv(os.path.join("ai", "datasets", "test.csv"), index=False, encoding='utf-8')
    
    print(f"\nSaved clean datasets:")
    print(f"- Total records: {len(df)}")
    print(f"- Train records: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"- Validation records: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"- Test records: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
    
    print("\nDepartment distribution across splits:")
    for split_name, s_df in [('Train', train_df), ('Validation', val_df), ('Test', test_df)]:
        print(f"\n{split_name} split departments:")
        print(s_df['department'].value_counts())
        print(f"{split_name} split language styles:")
        print(s_df['language_style'].value_counts())
        
    return df

if __name__ == '__main__':
    generate_records()
