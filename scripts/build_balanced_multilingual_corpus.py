"""
NEX-CIV: Balanced Multilingual Real Civic Grievance Corpus Builder
Builds ~2,500 highly authentic municipal complaints across:
- 5 Municipal Departments (Roads, Drainage, Water Supply, Electrical, Sanitation)
- 20 Granular Civic Types
- 3 Language Styles: English (en), Native Telugu (te), Romanized Telugu (te_latn)
- Linguistic Robustness: Dialect variations, informal phrasing, code-mixing, negation, boundary cases
- Strict Cluster Partitioning: 70% Train, 15% Validation, 15% Test
- 100% Guaranteed ZERO LEAKAGE between splits
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

AP_ULBS = [
    {'name': 'Vijayawada Municipal Corporation (VMC)', 'code': 'VMC', 'district': 'NTR'},
    {'name': 'Greater Visakhapatnam Municipal Corporation (GVMC)', 'code': 'GVMC', 'district': 'Visakhapatnam'},
    {'name': 'Guntur Municipal Corporation (GMC)', 'code': 'GMC', 'district': 'Guntur'},
    {'name': 'Tirupati Municipal Corporation (TMC)', 'code': 'TMC', 'district': 'Tirupati'},
    {'name': 'Eluru Municipal Corporation', 'code': 'ELR', 'district': 'Eluru'},
    {'name': 'Kakinada Municipal Corporation', 'code': 'KKD', 'district': 'Kakinada'},
    {'name': 'Kurnool Municipal Corporation', 'code': 'KMC', 'district': 'Kurnool'},
    {'name': 'Nellore Municipal Corporation', 'code': 'NMC', 'district': 'SPSR Nellore'}
]

# 25 clusters per department = 125 clusters total
# Each cluster contains distinct natural complaints across en, te, te_latn, code-mix, and boundary cases.
CLUSTERS_DATA = {
    # =========================================================================
    # DEPARTMENT 1: ROADS & BUILDINGS (road) - 25 Clusters
    # =========================================================================
    'road': [
        # Potholes (Clusters 1-8)
        {
            'id': 'RD_01', 'type': 'potholes', 'is_emg': False, 'sev': 3,
            'en': ["Massive deep pothole on main transit road causing serious motorcycle accidents", "Deep road crater near traffic junction, two-wheelers are skidding and falling", "Emergency patch work needed for deep pothole on arterial road"],
            'te': ["ప్రధాన రహదారిపై భారీ గుంతలు పడ్డాయి బైకులు పడి తీవ్రంగా గాయపడుతున్నారు", "రోడ్డు మధ్యలో ఏర్పడిన పెద్ద గోతి వల్ల వాహనాలు అదుపుతప్పుతున్నాయి", "వెంటనే ప్యాచ్ వర్క్ చేపట్టి ప్రమాదకర రోడ్డు గుంతలను పూడ్చండి"],
            'te_latn': ["Main road meeda pedda guntalu paddayi bikes skid ayi padipotunnaru", "Road madhyalo huge pothole valla vehicles control tapputunnayi repair cheyandi", "Road paina deep gundalu unnay patch work urgent ga cheyandi"]
        },
        {
            'id': 'RD_02', 'type': 'potholes', 'is_emg': False, 'sev': 3,
            'en': ["Flyover down-ramp has developed series of sharp potholes causing hard braking", "Potholes right at the descent of the bridge creating severe accident hazard", "Vehicles colliding on flyover slope due to sudden swerving to avoid road holes"],
            'te': ["ఫ్లైఓవర్ దిగే ర్యాంప్ వద్ద గుంతలు పడటంతో వాహనాలు సడన్ బ్రేకులు వేసి ఢీకొంటున్నాయి", "వంతెన దిగువన ప్రమాదకర గుంతలు ఏర్పడి నిత్యం ప్రమాదాలు జరుగుతున్నాయి", "ఫ్లైఓవర్ రోడ్డుపై గుంతలను పూడ్చకపోతే ప్రాణనష్టం జరిగే అవకాశం ఉంది"],
            'te_latn': ["Flyover slope paina potholes valla vehicles sudden braking tho collide avtunnayi", "Bridge down ramp daggara road holes repair fast accidents happening", "Flyover descent road guntalu patch work urgent"]
        },
        {
            'id': 'RD_03', 'type': 'potholes', 'is_emg': False, 'sev': 3,
            'en': ["Colony bus route road is full of waterlogged hidden potholes", "Rainwater filled road craters making depth invisible, auto-rickshaws overturning", "Dangerous submerged potholes on transit route after monsoon shower"],
            'te': ["కాలనీ బస్సు రూట్ రోడ్డుపై నీటితో నిండిన గుంతలు ఉన్నాయి ఆటోలు బోల్తా పడుతున్నాయి", "వర్షపు నీరు నిలిచి గుంతల లోతు కనిపించకపోవడంతో వాహనదారులు పడిపోతున్నారు", "బస్సు తిరిగే ప్రధాన రోడ్డుపై తారు గుంతలను పూడ్చండి"],
            'te_latn': ["Colony bus route road lo water filled potholes valla auto rickshaws overturn", "Rain water valla gundala lothu teliyaka two wheelers crash avtunnaru", "Bus transit road meeda deep potholes urgent repairs"]
        },
        {
            'id': 'RD_04', 'type': 'potholes', 'is_emg': False, 'sev': 3,
            'en': ["Vegetable rythu bazaar entrance road is riddled with deep mud craters", "Market access road has crater cluster breaking vehicle suspensions", "Heavy shoppers traffic getting stalled by deep holes on market lane"],
            'te': ["రైతు బజార్ ప్రవేశ రహదారి వద్ద గుంతలు పడి రాకపోకలు స్తంభించిపోయాయి", "మార్కెట్ రోడ్డుపై వాహనాల సస్పెన్షన్లు విరిగిపోతున్నాయి గుంతలు పూడ్చండి", "మార్కెట్ కు వచ్చే ప్రజలు గోతులలో పడి ఇబ్బందులు పడుతున్నారు"],
            'te_latn': ["Rythu bazaar entry road lo deep craters valla traffic block avtundi", "Market lane potholes valla vehicle suspensions damage avtunnayi", "Market road holes repair urgently public suffering"]
        },
        {
            'id': 'RD_05', 'type': 'potholes', 'is_emg': False, 'sev': 2,
            'en': ["Newly laid asphalt road already developed sharp holes within three weeks", "Substandard road patch work washed away after single rain leaving jagged edges", "Poor quality bitumen road eroded creating pit holes everywhere"],
            'te': ["వేసి నెల కూడా కాకముందే కొత్త రోడ్డుపై తారు లేచిపోయి గుంతలు పడ్డాయి", "నాసిరకం ప్యాచ్ వర్క్ వర్షానికి కొట్టుకుపోయి రోడ్డు అంతా రాళ్లమయంగా మారింది", "రోడ్డు నాణ్యత పరిశీలించి గుంతలు పడ్డ చోట మళ్లీ బీటీ ప్యాచ్ వేయించండి"],
            'te_latn': ["Kotha tar road vesina 1 month ke guntalu paddayi low quality work", "Asphalt peeled off single rain ke pit holes vachayi investigate quality", "New road surface damaged patch work re-do immediately"]
        },
        {
            'id': 'RD_06', 'type': 'potholes', 'is_emg': False, 'sev': 3,
            'en': ["School bus corridor road has huge cavities where vans get stuck daily", "Deep road potholes outside school gate creating safety hazard for small children", "School van tires falling into deep craters, parents demanding urgent patch work"],
            'te': ["పాఠశాల గేటు ఎదురుగా ఉన్న రోడ్డుపై ప్రమాదకర గుంతలు పడ్డాయి స్కూల్ బస్సులు ఇరుక్కుపోతున్నాయి", "విద్యార్థులు తిరిగే దారిలో పెద్ద గోతులు ఉండటంతో ప్రమాదాలు జరిగే అవకాశం ఉంది", "స్కూల్ జోన్ రోడ్డుపై గుంతలను యుద్ధప్రాతిపదికన పూడ్చాలి"],
            'te_latn': ["School gate eduruga huge road holes school vans stuck avtunnayi daily", "Pillala school road meeda dangerous craters patch work cheyandi", "School zone road pothole repair urgently for students safety"]
        },
        {
            'id': 'RD_07', 'type': 'potholes', 'is_emg': False, 'sev': 3,
            'en': ["Hospital emergency ambulance entry lane blocked with rough potholes", "Ambulance carrying critical patients getting delayed by severe road craters", "Hospital approach road potholes causing severe jolts to trauma victims"],
            'te': ["ఆసుపత్రి ఎమర్జెన్సీ అప్రోచ్ రోడ్డుపై గుంతలు ఉండటంతో అంబులెన్సులు వేగంగా వెళ్లలేకపోతున్నాయి", "రోగులను తీసుకెళ్లే అంబులెన్సులు కుదుపులకు గురవుతున్నాయి రోడ్డును వెంటనే బాగుచేయండి", "హాస్పిటల్ దారిలోని గుంతలను తక్షణమే పూడ్చి రోడ్డును సుగమం చేయాలి"],
            'te_latn': ["Hospital emergency ambulance route lo rough potholes valla patients suffering", "Ambulance speed slow avtundi road craters valla repair immediately", "Hospital road guntalu patch work urgent for emergency transit"]
        },
        {
            'id': 'RD_08', 'type': 'potholes', 'is_emg': False, 'sev': 2,
            'en': ["Unmarked damaged speed breaker has created deep crater on landing side", "Broken speed bump concrete chipped away leaving deep tyre-damaging trench", "Speed breaker paint faded and edges hollowed out into sharp road dip"],
            'te': ["స్పీడ్ బ్రేకర్ పక్కన రోడ్డు కుంగిపోయి లోతైన గుంత ఏర్పడింది వాహనాలు ఎగిరిపడుతున్నాయి", "విరిగిపోయిన స్పీడ్ బ్రేకర్ వల్ల రాత్రి పూట వాహనాలు అదుపు తప్పి పడిపోతున్నారు", "స్పీడ్ బ్రేకర్ మరమ్మతులు చేపట్టి పక్కన పడ్డ గుంతలను పూడ్చండి"],
            'te_latn': ["Speed breaker landing side lo deep crater formed tire damage avtundi", "Broken speed bump concrete edges sharp hole ga marindi fix cheyandi", "Speed breaker pakka road pit repair immediately"]
        },
        # Damaged Roads (Clusters 9-14)
        {
            'id': 'RD_09', 'type': 'damaged_roads', 'is_emg': False, 'sev': 3,
            'en': ["Entire asphalt road eroded down to muddy foundation, transit is impossible", "Bitumen stripped away completely on residential street leaving rocky rubble path", "Colony internal road washed away during cyclone, only loose boulders remain"],
            'te': ["మా కాలనీలో తారు రోడ్డు వర్షానికి పూర్తిగా కొట్టుకుపోయి కంకర తేలి నడవలేకపోతున్నాం", "రోడ్డు ఉపరితలం పూర్తిగా ఛిద్రమైంది రాళ్ల తేలిన దారిగా మారింది", "ధ్వంసమైన తారు రోడ్డును తొలగించి కొత్తగా బీటీ లేదా సీసీ రోడ్డు నిర్మించండి"],
            'te_latn': ["Colony lo tar road rain ki kottukupoyi kankara thelindi transit kashtam", "Entire asphalt layer washed out bare gravel path la marindi reconstruct", "Internal colony road completely broken new BT road grant cheyandi"]
        },
        {
            'id': 'RD_10', 'type': 'damaged_roads', 'is_emg': False, 'sev': 3,
            'en': ["Cement concrete road has cracked into multiple tilted slabs with iron rebar exposed", "Reinforced CC road fractured in middle, sharp steel mesh protruding dangerously", "Heavy trucks cracked concrete road slabs creating severe hazard for car tires"],
            'te': ["సిమెంట్ కాంక్రీట్ సీసీ రోడ్డు మధ్యలో పగుళ్లు వచ్చి ఇనుప కడ్డీలు పైకి తేలాయి", "సీసీ రోడ్డు ముక్కలైపోయి స్లాబ్‌లు పైకి లేచాయి వాహనాల టైర్లు కోసుకుపోతున్నాయి", "విరిగిన కాంక్రీట్ రోడ్డును పునర్నిర్మించి ప్రమాదకర ఇనుప కడ్డీలను తొలగించండి"],
            'te_latn': ["CC road center lo crack ayi iron rods bayataku vachayi dangerous", "Cement road fractured into jagged slabs tires bursting reconstruct", "Concrete road broken rebar exposed urgent repair required"]
        },
        {
            'id': 'RD_11', 'type': 'damaged_roads', 'is_emg': True, 'sev': 4,
            'en': ["Massive sinkhole crater opened up on main road, asphalt hollowed underneath", "Road collapsed inwards after underground pipeline failure, vehicle drop peril", "Huge underground cave-in on busy transit street, place safety barricades immediately"],
            'te': ["ప్రధాన రహదారిపై నేల కుంగి భారీ సింక్‌హోల్ ఏర్పడింది రోడ్డు ఎప్పుడైనా కూలిపోవచ్చు", "రోడ్డు కింద మట్టి కొట్టుకుపోయి పెద్ద అగాధం ఏర్పడింది అత్యవసర సహాయం అవసరం", "వాహనాలు లోపలికి పడిపోయే ప్రాణాపాయం ఉంది రోడ్డును వెంటనే బారికేడ్ చేయండి"],
            'te_latn': ["Main road center lo pedda sinkhole cave-in padindi road about to collapse", "Underground soil erosion valla asphalt hollowed deep crater emergency", "Road caved in 4 feet depth barricades pettandi vehicle drop danger"]
        },
        {
            'id': 'RD_12', 'type': 'damaged_roads', 'is_emg': False, 'sev': 2,
            'en': ["Utility pipeline cutting left unpaved on street for three months, road ruined", "Water board dug trench across road and abandoned it without restoring bitumen", "Excavated road crossing filled only with loose soil sinking during rain"],
            'te': ["పైపుల కోసం రోడ్డు తవ్వి మూడు నెలలైనా తిరిగి పూడ్చకుండా వదిలేశారు", "రోడ్డు కటింగ్ చేసిన చోట మట్టి కుంగిపోయి రాకపోకలకు తీవ్ర అంతరాయం కలుగుతోంది", "తవ్విన రోడ్డును కాంట్రాక్టర్ వెంటనే తారు వేసి పునరుద్ధరించాలి"],
            'te_latn': ["Utility pipeline trench dug and left unpaved road completely ruined", "Water board cut road and abandoned loose mud sinking in rain", "Road cutting place patch work chesi bitumen restore cheyandi"]
        },
        {
            'id': 'RD_13', 'type': 'damaged_roads', 'is_emg': False, 'sev': 3,
            'en': ["Canal embankment road eroded and collapsing into the flowing waterway", "Irrigation canal bund road washed out by half, heavy vehicles cannot pass", "Canal bank road has lost its retaining wall and soil is sliding into water"],
            'te': ["కాలువ గట్టు కోతకు గురై సగం రోడ్డు నీటిలో కొట్టుకుపోయింది వాహనాలు వెళ్లలేవు", "కాలువ పక్కనున్న రోడ్డు కుంగిపోయింది రివెట్‌మెంట్ గోడ నిర్మించి రోడ్డు వేయాలి", "గట్టు రోడ్డు కూలిపోకుండా అత్యవసర రక్షణ పనులు చేపట్టాలి"],
            'te_latn': ["Canal bund road half washed out into water transit dangerous", "Canal side road retaining wall broken soil sliding into canal", "Embankment road broken reconstruct with protection wall"]
        },
        {
            'id': 'RD_14', 'type': 'damaged_roads', 'is_emg': False, 'sev': 2,
            'en': ["Uneven wavy road surface with severe rutting causing violent vehicle bounce", "Asphalt road has developed ripples and waves under heavy heat, loss of control", "Corrugated bitumen road surface creating dangerous motorcycle wobble"],
            'te': ["రోడ్డు సమతలంగా లేక అలల మాదిరిగా ఎగుడుదిగుడుగా తయారైంది వాహనాలు ఎగిరిపడుతున్నాయి", "నాసిరకం తారు కరిగిపోయి రోడ్డు అంతా గతుకులమయంగా మారింది స్టీరింగ్ తిరగడం లేదు", "రోడ్డును లెవల్ చేసి కొత్త తారు పొర వేయాల్సిందిగా కోరుతున్నాం"],
            'te_latn': ["Uneven wavy asphalt road ripples valla vehicles violently bouncing", "Road surface rutting issue steering control missing re-tar surface", "Corrugated road surface leveling work required"]
        },
        # Footpath Damage (Clusters 15-19)
        {
            'id': 'RD_15', 'type': 'footpath_damage', 'is_emg': False, 'sev': 2,
            'en': ["Pedestrian footpath paver blocks shattered and missing on commercial street", "Broken paver tiles on municipal sidewalk causing senior citizens to trip and fall", "Footpath pavement broken into loose bricks forcing pedestrians onto fast lane"],
            'te': ["పాదచారుల ఫుట్‌పాత్ పేవర్‌బ్లాక్స్ పగిలిపోయాయి వృద్ధులు కిందపడి గాయపడుతున్నారు", "షాపింగ్ వీధిలో ఫుట్‌పాత్ టైల్స్ ఊడిపోయి నడవడానికి వీల్లేకుండా ఉంది సరిచేయండి", "కాలిబాట రాళ్లు లేచిపోవడంతో ప్రజలు ప్రమాదకరంగా రోడ్డుపై నడవాల్సి వస్తోంది"],
            'te_latn': ["Pedestrian footpath paver blocks virigipoyi loose stones vachayi", "Footpath tiles broken senior citizens trip ayi fall avtunnaru repair", "Footpath damaged pedestrians road paina nadavalsi vastondi"]
        },
        {
            'id': 'RD_16', 'type': 'footpath_damage', 'is_emg': False, 'sev': 3,
            'en': ["Concrete slabs covering roadside drain footpath cracked creating deep pit", "Footpath slab over stormwater canal collapsed, open gutter pit on walkway", "Broken walkway slab directly opposite market, pedestrians can plunge into drain"],
            'te': ["ఫుట్‌పాత్ పై వేసిన సిమెంట్ స్లాబ్‌లు విరిగిపోయి మురుగు కాలువ తెరిచి ఉంది", "నడిచే దారిలోని స్లాబ్ కూలిపోయింది నడుస్తున్నప్పుడు పిల్లలు పడిపోయే ప్రమాదం ఉంది", "పాదచారుల బాటపై ఉన్న డ్రైనేజీ కప్పు స్లాబ్‌లను తక్షణమే మార్చి మూయండి"],
            'te_latn': ["Footpath cement slab broken open drain exposed walkers risk", "Walkway concrete slab collapsed deep pit danger for children", "Footpath drain covering slab replace cheyandi urgent"]
        },
        {
            'id': 'RD_17', 'type': 'footpath_damage', 'is_emg': False, 'sev': 2,
            'en': ["Commercial shops have illegally encroached and demolished municipal footpath", "Private shopkeepers constructed concrete ramps destroying continuous sidewalk", "Unauthorized steps and ramps built over public walking track blocking pedestrians"],
            'te': ["దుకాణదారులు ఫుట్‌పాత్‌ను ఆక్రమించి విరగ్గొట్టారు అక్రమ ర్యాంప్‌లు కట్టేశారు", "కమర్షియల్ షాపుల వారు ఫుట్‌పాత్ ధ్వంసం చేసి ప్రైవేట్ మెట్లు కట్టారు తొలగించండి", "పాదచారుల కాలిబాట ఆక్రమణలు క్లియర్ చేసి ఫుట్‌పాత్‌ను పునరుద్ధరించండి"],
            'te_latn': ["Commercial shops encroached footpath and constructed illegal ramps", "Footpath broken by shop owners walking track completely blocked", "Sidewalk encroachment clear chesi footpath restore cheyandi"]
        },
        {
            'id': 'RD_18', 'type': 'footpath_damage', 'is_emg': False, 'sev': 2,
            'en': ["Public park walking track tiles broken with exposed tree roots causing stumbles", "Municipal walking track tiles dislodged, morning joggers twisting ankles", "Jogging track concrete surface fractured and uneven along municipal lake park"],
            'te': ["మునిసిపల్ పార్కులో వాకింగ్ ట్రాక్ టైల్స్ ఊడిపోయాయి వాకర్స్ పడి గాయపడుతున్నారు", "పార్కు నడక దారిలో చెట్ల వేర్లు పైకి వచ్చి టైల్స్ పగిలాయి సరిచేయించండి", "ఉదయం వాకింగ్ చేసే వృద్ధులకు ఇబ్బంది లేకుండా వాకింగ్ ట్రాక్ రిపేర్ చేయండి"],
            'te_latn': ["Municipal park walking track tiles broken morning walkers falling", "Jogging track tiles displaced ankle twisting danger repair path", "Park walkway concrete fractured fix tiles immediately"]
        },
        {
            'id': 'RD_19', 'type': 'footpath_damage', 'is_emg': False, 'sev': 2,
            'en': ["Handrails on elevated pedestrian footpath broken and rusted away", "Footpath safety railing collapsed along deep roadside ditch, walkers exposed", "Missing pedestrian guardrails on bridge footpath creating plunge risk"],
            'te': ["ఎత్తైన ఫుట్‌పాత్ రక్షణ రెయిలింగ్ విరిగిపోయింది కింద పడిపోయే ప్రమాదం ఉంది", "కాలిబాట పక్కన ఉన్న ఇనుప రెయిలింగ్ తుప్పుపట్టి కూలిపోయింది సరిచేయండి", "వంతెన ఫుట్‌పాత్ కు కొత్త సేఫ్టీ హ్యాండ్‌రెయిల్స్ అమర్చాలి"],
            'te_latn': ["Elevated footpath handrails broken rusted fall hazard into ditch", "Footpath safety railing collapsed walkers exposed install new rails", "Pedestrian guardrail missing on bridge walkway fix fast"]
        },
        # Road Obstruction (Clusters 20-25)
        {
            'id': 'RD_20', 'type': 'road_obstruction', 'is_emg': False, 'sev': 3,
            'en': ["Large fallen tree branch blocking both lanes of municipal transit road", "Gale winds knocked down heavy bough across road halting all vehicular traffic", "Fallen tree blocking street preventing ambulances and buses from moving"],
            'te': ["పెద్ద చెట్టు కొమ్మ విరిగి ప్రధాన రహదారిపై పడింది రెండు దారులు మూసుకుపోయాయి", "గాలివానకు చెట్టు నేలకూలి రోడ్డుపై పడటంతో ట్రాఫిక్ పూర్తిగా స్తంభించింది", "రోడ్డుకు అడ్డంగా పడిన చెట్టును క్రేన్ తెప్పించి వెంటనే తొలగించండి"],
            'te_latn': ["Pedda chettu komma virigi road paina padindi traffic completely blocked", "Fallen tree branch blocking transit ambulances unable to pass clear it", "Tree bough across street clear cheyandi municipal disaster team"]
        },
        {
            'id': 'RD_21', 'type': 'road_obstruction', 'is_emg': False, 'sev': 2,
            'en': ["Building construction material dumped on asphalt blocking half the road", "Piles of construction sand and gravel unloaded on public street causing bike skids", "Illegal dumping of building aggregate narrowing residential transit corridor"],
            'te': ["భవన నిర్మాణ ఇసుక మరియు కంకర రోడ్డుపై పోశారు ఒక వైపు దారి మూసుకుపోయింది", "రోడ్డుపై అక్రమంగా ఇసుక కుప్పలు పోయడంతో బైకులు జారి పడుతున్నాయి తొలగించండి", "రోడ్డుపై పోసిన నిర్మాణ సామగ్రిని వెంటనే జప్తు చేసి రోడ్డు క్లియర్ చేయండి"],
            'te_latn': ["Construction sand and kankara road meeda dump chesaru lane blocked", "Sand pile on public road causing two wheeler skids remove aggregate", "Building materials road encroachment clear fast"]
        },
        {
            'id': 'RD_22', 'type': 'road_obstruction', 'is_emg': False, 'sev': 2,
            'en': ["Abandoned junk scrap vehicles parked permanently on roadside narrowing street", "Old rusted scrap lorry dumped on corner blocking turn visibility and traffic", "Unclaimed accident car left abandoned on municipal corridor for two months"],
            'te': ["పాత తుక్కు వాహనాన్ని రోడ్డు మూలలో నెలల తరబడి వదిలేశారు ట్రాఫిక్ జామ్ అవుతోంది", "నిరుపయోగంగా పడి ఉన్న స్క్రాప్ వాహనం వల్ల మలుపు వద్ద ప్రమాదాలు జరుగుతున్నాయి", "రోడ్డుపై వదిలేసిన తుక్కు వాహనాన్ని మున్సిపల్ క్రేన్ తో తరలించండి"],
            'te_latn': ["Abandoned scrap vehicle road corner lo vadilesaru traffic jammed", "Old junk lorry parked permanently blocking turn visibility tow away", "Unclaimed scrap car roadside obstruction remove urgently"]
        },
        {
            'id': 'RD_23', 'type': 'road_obstruction', 'is_emg': False, 'sev': 2,
            'en': ["Unauthorized massive festival flex banners and iron poles erected across road", "Heavy welcome arch erected without permission restricting fire engine transit", "Illegal flex hoardings tied to street light poles flapping dangerously into traffic"],
            'te': ["రోడ్డుపై అనుమతి లేకుండా భారీ ఫ్లెక్సీ బ్యానర్లు ఇనుప తోరణాలు కట్టి రాకపోకలు ఆపారు", "అక్రమ స్వాగత తోరణాల వల్ల వాహన రాకపోకలకు తీవ్ర అంతరాయం కలుగుతోంది తొలగించండి", "రోడ్డుకు అడ్డంగా కట్టిన భారీ హోర్డింగ్‌లను మునిసిపల్ సిబ్బంది తొలగించాలి"],
            'te_latn': ["Illegal flex banners and iron poles erected across road traffic blocked", "Unauthorized welcome arch restricting transit clear encroachments", "Flex boards flapping into vehicle lane remove hoardings"]
        },
        {
            'id': 'RD_24', 'type': 'road_obstruction', 'is_emg': False, 'sev': 2,
            'en': ["Street vendors and push carts permanently encroached traffic carriageway", "Roadside fruit and vegetable carts blocking arterial road during peak hours", "Unauthorized commercial push cart parking turning busy corridor into bottle neck"],
            'te': ["తోపుడు బండ్ల వ్యాపారులు రోడ్డును ఆక్రమించడంతో ట్రాఫిక్ తీవ్రంగా స్తంభించింది", "కూరగాయల బండ్లు రోడ్డు మధ్య వరకు రావడంతో బస్సులు తిరగలేకపోతున్నాయి", "ట్రాఫిక్ పోలీసులతో కలిసి రోడ్డు ఆక్రమణలను తొలగించి మార్కెట్ కు తరలించండి"],
            'te_latn': ["Street vendors push carts encroached carriageway peak hours traffic jam", "Push cart vendors blocking transit road clear road encroachment", "Footpath and road encroachment by vendors clear immediately"]
        },
        {
            'id': 'RD_25', 'type': 'road_obstruction', 'is_emg': False, 'sev': 2,
            'en': ["Compound wall debris and demolition rubble dumped illegally on colony street", "Demolished building concrete chunks scattered on road blocking two-way cars", "Demolition contractor abandoned rubble on municipal street clear with loader"],
            'te': ["కూల్చివేసిన భవన శిథిలాలు మరియు బండరాళ్లను రోడ్డుపై పోసి వదిలేశారు", "రోడ్డుపై కాంక్రీట్ వ్యర్థాలు పారబోయడంతో కార్లు వెళ్లడానికి వీల్లేకుండా ఉంది", "రోడ్డుపై పోసిన డెమోలిషన్ వేస్ట్ ను ట్రాక్టర్ తెప్పించి వెంటనే తరలించండి"],
            'te_latn': ["Demolition building rubble and concrete dumped on colony street", "Building debris blocking two way cars clear with municipal loader", "Rubble dumped on street transit blocked remove contractor debris"]
        }
    ],

    # =========================================================================
    # DEPARTMENT 2: PUBLIC HEALTH & DRAINAGE (drainage) - 25 Clusters
    # =========================================================================
    'drainage': [
        # Drainage Overflow (Clusters 1-8)
        {
            'id': 'DR_01', 'type': 'drainage_overflow', 'is_emg': False, 'sev': 3,
            'en': ["Black foul sewage water overflowing from open canal onto residential road", "Drainage canal overflowing with dark sludge, terrible stench across entire ward", "Raw sewage spilling out of open roadside gutter inundating residential gates"],
            'te': ["మురుగు కాలువ పొంగి నల్లటి మురుగు నీరు రోడ్డుపై ప్రవహిస్తోంది తీవ్ర దుర్వాసన", "కాలనీలోని డ్రైనేజీ నిండిపోయి ఇళ్ల ముందర నల్లటి బురద నీరు నిలిచిపోయింది", "డ్రైనేజీ పొంగి దుర్గంధం వస్తోంది ప్రజలు రోగాల బారిన పడుతున్నారు క్లీన్ చేయండి"],
            'te_latn': ["Drainage canal overflow ayi black sewage water road paina flow avtundi", "Foul smell and dirty sewage entering house gates drainage overflowing", "Colony drainage pongipoyi road motham gutter la marindi clearing required"]
        },
        {
            'id': 'DR_02', 'type': 'drainage_overflow', 'is_emg': False, 'sev': 3,
            'en': ["Light drizzle causes storm sewer to back up and flood commercial shops", "Slightest rainfall leads to drainage chamber backflow entering ground-floor stores", "Stormwater drain overwhelmed, foul water standing two feet deep in market lane"],
            'te': ["చిన్న వర్షానికే డ్రైనేజీ పొంగి మార్కెట్ లోని దుకాణాల్లోకి మురుగు నీరు చేరుతోంది", "వర్షపు నీటి కాలువ వెనక్కి తన్ని వ్యాపార సముదాయాల్లోకి మురుగు పారుతోంది", "మార్కెట్ లో మురుగు నీరు నిలిచి వ్యాపారులు తీవ్ర నష్టాలు ఎదుర్కొంటున్నారు"],
            'te_latn': ["Chinna rain ke drainage chamber overflow ayi shops loki vastundi", "Market area lo foul water standing 2 feet deep customer transit blocked", "Storm sewer backflow clean chesi super sucker machine pampandi"]
        },
        {
            'id': 'DR_03', 'type': 'drainage_overflow', 'is_emg': False, 'sev': 3,
            'en': ["Underground sewer manhole spewing toilet wastewater onto colony lane", "Sewerage pipeline geyser erupted pushing fecal effluent across the road", "Underground chamber overflow bubbling up through road joint fissures with stench"],
            'te': ["అండర్‌గ్రౌండ్ డ్రైనేజ్ మ్యాన్‌హోల్ నుంచి టాయిలెట్ వ్యర్థాలు రోడ్డుపైకి ఉబికి వస్తున్నాయి", "సీవరేజ్ లైన్ పొంగి మురుగు నీరు రోడ్డుపై చిమ్ముతోంది తీవ్ర కంపు భరించలేకున్నాం", "మునిసిపల్ సక్కర్ మెషిన్ తెప్పించి అండర్‌గ్రౌండ్ జామ్ క్లియర్ చేయండి"],
            'te_latn': ["Underground drainage manhole nundi toilet waste water reverse road paina", "Sewerage chamber bubbling up foul effluent everywhere emergency clearing", "Underground sewer line overflow super sucker machine pampandi"]
        },
        {
            'id': 'DR_04', 'type': 'drainage_overflow', 'is_emg': False, 'sev': 3,
            'en': ["Hospital approach lane inundated by overflowing drainage canal", "Foul drain water overflowing outside hospital casualty gate, hygiene disaster", "Patients and doctors wading through contaminated drain water outside clinic"],
            'te': ["ఆసుపత్రి గేటు వద్దే మురుగు కాలువ పొంగి రోడ్డు అంతా కంపుకొడుతోంది", "ఆసుపత్రి దారిలో మురుగు నీరు నిలవడంతో రోగులు నడవడానికి తీవ్ర ఇబ్బందులు పడుతున్నారు", "హాస్పిటల్ ముందు పొంగిన మురుగు నీటిని వెంటనే తొలగించి బ్లీచింగ్ చల్లించండి"],
            'te_latn': ["Hospital gate bayate drainage canal overflow ayindi foul hygiene risk", "Patients wading through contaminated drain water outside hospital clinic", "Hospital road drainage overflow clear chesi bleaching powder challandi"]
        },
        {
            'id': 'DR_05', 'type': 'drainage_overflow', 'is_emg': False, 'sev': 3,
            'en': ["Drainage slope defect causing water to stagnate and overflow reverse", "Inverted drain gradient makes sewage flow backwards into household basements", "Defective culvert slope causing domestic greywater to pool and overflow"],
            'te': ["డ్రైనేజీ కాలువ వాలు తప్పుగా ఉండటం వల్ల మురుగు నీరు ముందుకు పోక ఇళ్లల్లోకి వస్తోంది", "కాలువ లెవల్ తప్పడంతో నీరు వెనక్కి తన్ని బేస్‌మెంట్‌లలో చేరుతోంది", "ఇంజనీరింగ్ విభాగం కాలువ వాలును సరిచేసి మురుగు బయటకు వెళ్లేలా చూడాలి"],
            'te_latn': ["Drainage slope defective water flowing backwards into house basements", "Drain gradient inverted sewage pooling and overflowing reverse", "Canal level defect rectify cheyandi water flow stagnant"]
        },
        {
            'id': 'DR_06', 'type': 'drainage_overflow', 'is_emg': False, 'sev': 3,
            'en': ["Primary school playground flooded with overflowing septic drain water", "School children surrounded by dirty canal overflow during recess hours", "Noxious sewage canal breached entering school courtyard, urgent health risk"],
            'te': ["పాఠశాల ఆట స్థలంలోకి మురుగు కాలువ పొంగి నీరు నిలిచిపోయింది పిల్లలకు ప్రమాదం", "స్కూలు ఆవరణలోకి డ్రైనేజీ నీరు చేరడంతో దుర్వాసనతో విద్యార్థులు అస్వస్థతకు గురవుతున్నారు", "శానిటరీ టీమ్ వెంటనే వచ్చి పాఠశాల ఆవరణలోని మురుగును శుభ్రం చేయాలి"],
            'te_latn': ["Primary school ground flooded with overflowing septic drain water", "School courtyard lo foul sewage overflow kids falling sick clean immediately", "School premises drainage water suckering chesi bleaching challandi"]
        },
        {
            'id': 'DR_07', 'type': 'drainage_overflow', 'is_emg': False, 'sev': 3,
            'en': ["Commercial restaurants dumping grease into drain causing massive overflow", "Hotel kitchen fat solidified in pipe causing sewage fountain onto public road", "Grease choke forced entire colony main sewer to overflow onto pedestrian path"],
            'te': ["హోటళ్ల వారు నూనె వ్యర్థాలు కాలువలో పోయడంతో కాలువ గడ్డకట్టి పొంగిపొర్లుతోంది", "రెస్టారెంట్ వ్యర్థాల వల్ల మెయిన్ డ్రైనేజ్ జామ్ అయ్యి రోడ్డుపై మురుగు పారుతోంది", "నిబంధనలు ఉల్లంఘించిన హోటళ్లకు జరిమానా వేసి డ్రైనేజీ బ్లాక్ తొలగించండి"],
            'te_latn': ["Restaurant grease dumped in drain canal solidified massive overflow", "Hotels oil waste choked colony sewer line dirty fountain on road", "Commercial oil choke clear chesi sewer clearing cheyandi"]
        },
        {
            'id': 'DR_08', 'type': 'drainage_overflow', 'is_emg': False, 'sev': 2,
            'en': ["Apartment cellar parking flooded with municipal roadside drain backflow", "Backflow flap valve missing, municipal road gutter draining into apartment cellar", "Underground parking submerged in two feet of sewage water during high tide rain"],
            'te': ["మునిసిపల్ కాలువ వెనక్కి తన్ని అపార్ట్‌మెంట్ సెల్లార్ పార్కింగ్‌లోకి మురుగు చేరింది", "రోడ్డు కాలువ నీరు అపార్ట్‌మెంట్ లోకి వస్తోంది కార్లు మోటార్లు మునిగిపోయాయి", "డ్రైనేజీ బ్యాక్‌ఫ్లో వాల్వ్ ఏర్పాటు చేసి సెల్లార్ మురుగును పంపింగ్ చేయించండి"],
            'te_latn': ["Apartment cellar parking flooded with municipal roadside drain backflow", "Gutter water reverse flowing into parking basement pumps motor submerged", "Drain backflow issue solve cheyandi apartment cellar clear"]
        },
        # Blocked Drainage (Clusters 9-14)
        {
            'id': 'DR_09', 'type': 'blocked_drainage', 'is_emg': False, 'sev': 2,
            'en': ["Stormwater drain completely choked with plastic covers and bottles", "Polythene garbage blocking the canal culvert preventing any water outflow", "Drains heavily clogged with single-use plastic, stagnant water breeding mosquitoes"],
            'te': ["డ్రైనేజీ కాలువలో ప్లాస్టిక్ సీసాలు కవర్లు పేరుకుపోయి నీరు ముందుకు సాగడం లేదు", "కాలువ పూడికతో మూసుకుపోయింది నిల్వ నీటిలో లక్షలాది దోమలు పుడుతున్నాయి", "కల్వర్టు కింద ప్లాస్టిక్ వ్యర్థాలు అడ్డుపడ్డాయి సిబ్బందితో పూడిక తీయించండి"],
            'te_latn': ["Drainage canal lo plastic bottles and covers block ayi water stopped", "Choked drain stagnant black water mosquitoes chala ekkuva ayyayi", "Canal culvert lo plastic waste block clear cheyandi immediately"]
        },
        {
            'id': 'DR_10', 'type': 'blocked_drainage', 'is_emg': False, 'sev': 2,
            'en': ["Decades of silt accumulation hardened into stone-like layer inside canal", "Drain bed elevated with solid silt deposit reducing water carrying capacity to zero", "Desiltation not carried out before monsoon, drain totally choked with mud"],
            'te': ["కాలువలో సంవత్సరాలుగా పూడికతీయకపోవడంతో మట్టి గడ్డకట్టి నీటి మార్గం మూసుకుపోయింది", "డ్రైనేజీ కాలువ పూడికతో నిండిపోయింది మురుగు బయటకు వెళ్లడం లేదు", "శానిటరీ ఇన్‌స్పెక్టర్ పరిశీలించి జేసీబీతో పూడికతీత పనులు వెంటనే చేపట్టాలి"],
            'te_latn': ["Drainage lo years nundi silt and mud deposit ayi water stagnation", "Desiltation cheyaledu monsoon vachindi canal capacity zero", "Colony drainage canal desilting JCB machine pampandi"]
        },
        {
            'id': 'DR_11', 'type': 'blocked_drainage', 'is_emg': False, 'sev': 2,
            'en': ["Building construction cement slurry dumped into drain setting into hard rock", "Hardened concrete debris inside municipal drain choked all colony drainage", "Building contractors washed mortar into drain creating rock-solid blockage"],
            'te': ["భవన నిర్మాణ సిమెంట్ వ్యర్థాలు కాలువలో పోయడంతో సిమెంట్ గడ్డకట్టి కాలువ మూసుకుపోయింది", "డ్రైనేజీలో కాంక్రీట్ చెత్త వేయడం వల్ల మురుగు నీటి ప్రవాహం పూర్తిగా ఆగిపోయింది", "కాలువను ధ్వంసం చేసిన కాంట్రాక్టర్ పై చర్యలు తీసుకుని బ్లాక్ తొలగించండి"],
            'te_latn': ["Construction cement slurry drain lo dump chesaru concrete block ayindi", "Hardened mortar inside municipal gutter completely choked flow", "Contractor cement waste block in drainage clear immediately"]
        },
        {
            'id': 'DR_12', 'type': 'blocked_drainage', 'is_emg': False, 'sev': 2,
            'en': ["Tree roots penetrated underground drainage pipe creating impenetrable web", "Massive root intrusion cracked and blocked underground sewer line", "Toilet waste backing up into homes due to tree root blockage inside pipe"],
            'te': ["చెట్ల వేర్లు భూగర్భ డ్రైనేజీ పైపుల్లోకి చొచ్చుకుపోయి పైపులు పూర్తిగా మూసుకుపోయాయి", "వేర్లు అడ్డుపడటంతో ఇళ్లల్లోని టాయిలెట్ నీరు వెనక్కి వస్తోంది తక్షణ చర్యలు తీసుకోండి", "డ్రైనేజీ పైపు కట్ చేసి చెట్ల వేర్లను తొలగించి కొత్త పైపు వేయాలి"],
            'te_latn': ["Tree roots penetrated underground drainage pipe toilet water reverse", "Massive root intrusion cracked sewer line water stagnant", "Underground drainage pipe roots block cut and clear pipe"]
        },
        {
            'id': 'DR_13', 'type': 'blocked_drainage', 'is_emg': False, 'sev': 2,
            'en': ["Culvert bridge mouth choked by dead branches and floating domestic rubbish", "Canal culvert grate jammed with floating trash after thunderstorm", "Stormwater intake grill blinded by foliage causing street inundation"],
            'te': ["కల్వర్టు వంతెన కింద చెట్ల కొమ్మలు మరియు చెత్తాచెదారం ఇరుక్కుని నీరు ఆగిపోయింది", "వర్షపు నీటి కాలువ గ్రిల్ వద్ద చెత్త పేరుకుపోవడంతో నీరు రోడ్డుపైకి తన్నుతోంది", "కల్వర్టు గేట్ ను తక్షణమే శుభ్రం చేసి నీటి ప్రవాహాన్ని సుగమం చేయండి"],
            'te_latn': ["Culvert bridge mouth choked with dead branches and floating rubbish", "Canal culvert grate jammed with trash water flooding street", "Culvert grill clear chesi water flow release cheyandi"]
        },
        {
            'id': 'DR_14', 'type': 'blocked_drainage', 'is_emg': False, 'sev': 2,
            'en': ["Meat and poultry market animal entrails thrown into open drain clogging pipe", "Slaughterhouse blood and waste clogging neighborhood municipal drain with stench", "Butcher shops dumping bone and skin waste directly into roadside gutter"],
            'te': ["చికెన్ మరియు మటన్ షాపుల వ్యర్థాలు కాలువలో పారవేయడంతో కాలువ పూడిపోయింది", "మాంసం మార్కెట్ వ్యర్థాలతో కాలువ జామ్ అయ్యి తీవ్ర దుర్వాసన వస్తోంది", "మాంసం వ్యర్థాలు వేసే షాపులను సీజ్ చేసి కాలువను జెట్టింగ్ మెషిన్ తో క్లీన్ చేయండి"],
            'te_latn': ["Meat market entrails and poultry waste clogged open drain foul stench", "Butcher shops waste in roadside gutter canal jammed clear immediately", "Chicken shop waste blocked drain super sucker cleaning needed"]
        },
        # Open Manhole (Clusters 15-19)
        {
            'id': 'DR_15', 'type': 'open_manhole', 'is_emg': True, 'sev': 4,
            'en': ["Open uncovered manhole on pedestrian path, extreme life-safety death trap", "Manhole lid missing on street right outside primary school gate, children at risk", "Deep open sewer pit with zero warning barricades on dark residential lane"],
            'te': ["పాదచారుల దారిలో మ్యాన్‌హోల్ మూత లేకుండా తెరిచి ఉంది ప్రాణాపాయం పొంచి ఉంది", "స్కూలు బయటే డ్రైనేజీ గుంత తెరిచి ఉంది చిన్న పిల్లలు పడిపోయే ప్రమాదం ఉంది", "రాత్రి సమయంలో ఎవరైనా పడితే ప్రాణాలు పోతాయి వెంటనే కొత్త సిమెంట్ మూత వేయండి"],
            'te_latn': ["Open manhole on pedestrian path no cover extreme life safety hazard", "School bayate manhole lid ledu kids play area danger cement lid veyandi", "Deep open sewer pit in colony night time death trap fit cover urgently"]
        },
        {
            'id': 'DR_16', 'type': 'open_manhole', 'is_emg': True, 'sev': 4,
            'en': ["Heavy lorry crushed concrete manhole lid leaving gaping hole in traffic lane", "Manhole cover shattered by truck, vehicle wheels falling directly into deep cavity", "Cracked manhole frame unstable, slab slips whenever two-wheelers ride over"],
            'te': ["భారీ లారీ తగిలి మ్యాన్‌హోల్ మూత పగిలిపోయింది లోపలికి పెద్ద రంధ్రం పడింది", "డ్రైనేజీ చాంబర్ మూత పగుళ్లు ఇచ్చి వాహనాల టైర్లు గుంతలో ఇరుక్కుపోతున్నాయి", "విరిగిన మ్యాన్‌హోల్ స్లాబ్ ను తొలగించి దృఢమైన ఐరన్ లేదా సీసీ కవర్ అమర్చండి"],
            'te_latn': ["Heavy vehicle hit chesi manhole cement lid break ayindi vehicle wheels stuck", "Manhole cover cracked open hole vehicle accidents happening", "Replace broken manhole frame with heavy duty cast iron lid urgently"]
        },
        {
            'id': 'DR_17', 'type': 'open_manhole', 'is_emg': True, 'sev': 4,
            'en': ["Drain cleaning crew removed manhole slab yesterday and left site unattended", "Sanitation workers opened sewer chamber and abandoned it without warning signs", "Open manhole left uncovered after desilting work in middle of arterial road"],
            'te': ["నిన్న కాలువ క్లీన్ చేయడానికి మ్యాన్‌హోల్ మూత తీసి అలాగే వదిలేసి వెళ్ళిపోయారు", "మునిసిపల్ సిబ్బంది మ్యాన్‌హోల్ తెరిచి బారికేడ్ పెట్టకుండా నిర్లక్ష్యంగా వదిలారు", "రోడ్డు మధ్యలో తెరిచి ఉన్న మ్యాన్‌హోల్ ను తక్షణమే మూసివేయించాలి అత్యవసరం"],
            'te_latn': ["Cleaning crew manhole lid remove chesi unattended vadilesaru danger", "Sanitation workers left open sewer chamber without barricades on road", "Open manhole road middle lo undi immediately cover pettandi emergency"]
        },
        {
            'id': 'DR_18', 'type': 'open_manhole', 'is_emg': True, 'sev': 4,
            'en': ["Manhole iron lid stolen by scrap thieves overnight leaving cavernous drop", "Cast iron manhole cover stolen on main road, fatal plunge peril in darkness", "Theft of sewer chamber grate has left a dangerous 10-foot vertical drop"],
            'te': ["రాత్రికి రాత్రే ఇనుప మ్యాన్‌హోల్ మూతను దొంగలు ఎత్తుకెళ్లారు లోతైన గుంత ఏర్పడింది", "మెయిన్ రోడ్డుపై మ్యాన్‌హోల్ కవర్ దొంగిలించబడింది చీకట్లో ప్రాణాపాయం ఉంది", "వెంటనే కాంక్రీట్ మూత బిగించి ప్రమాద నివారణ చర్యలు చేపట్టండి"],
            'te_latn': ["Manhole iron lid stolen overnight deep vertical pit left open danger", "Cast iron manhole cover stolen fatal drop hazard on road replace fast", "Stolen manhole cover place lo new cement slab veyandi immediately"]
        },
        {
            'id': 'DR_19', 'type': 'open_manhole', 'is_emg': True, 'sev': 4,
            'en': ["Flooded street concealing open manhole, water swirling into suction vortex", "Rain water submerged open manhole chamber creating deadly drowning trap", "Hidden open manhole underwater on flooded colony lane, cordoning urgently needed"],
            'te': ["వరద నీటి కింద తెరిచి ఉన్న మ్యాన్‌హోల్ గుంత సుడిగుండంలా మారింది ప్రాణాపాయం", "రోడ్డుపై నీరు నిలవడంతో తెరిచిన మ్యాన్‌హోల్ కనిపించడం లేదు ఎవరైనా పడితే మునిగిపోతారు", "వెంటనే ఆ ప్రాంతాన్ని బారికేడ్ చేసి ఎర్రటి జెండాలు లేదా ప్రమాద హెచ్చరికలు పెట్టండి"],
            'te_latn': ["Flooded street concealing open manhole drowning death trap", "Rain water kindha open manhole teliyaka pedestrians fall danger cordoning fast", "Submerged open sewer pit warning barricade pettandi urgently"]
        },
        # Sewage Leakage (Clusters 20-25)
        {
            'id': 'DR_20', 'type': 'sewage_leakage', 'is_emg': False, 'sev': 3,
            'en': ["Underground sewer main pipe fractured leaking sewage onto drinking pipeline", "Sewage leaking underground and contaminating nearby clean water distribution lines", "Cross contamination hazard: burst sewer pipe seeping into municipal pipeline"],
            'te': ["భూగర్భ సీవరేజ్ పైపు పగిలి పక్కనే ఉన్న తాగునీటి పైపుల్లోకి మురుగు నీరు కలుస్తోంది", "సీవరేజ్ లైన్ పగిలి రోడ్డు కింద నుండి మురికి నీరు పైకి ఉబికి వస్తోంది కంపుతో", "తాగునీరు కలుషితం కాకముందే సీవరేజ్ పైపు లీకేజీని అరికట్టండి"],
            'te_latn': ["Underground sewer line leak ayi adjacent drinking water pipe contamination danger", "Burst sewer pipe seeping filthy water onto colony road and foundation", "Sewage pipeline fracture urgent repair required disease outbreak risk"]
        },
        {
            'id': 'DR_21', 'type': 'sewage_leakage', 'is_emg': False, 'sev': 3,
            'en': ["Sewage chamber joint eroded, continuous toxic liquid pooling by houses", "Joint between drainage pipes separated, continuous foul effluent leaking", "Sewage seepage penetrating residential compound walls causing structural damage"],
            'te': ["డ్రైనేజీ పైపుల జాయింట్ ఊడిపోయి మురుగు నీరు నిరంతరం ఇళ్ల గోడల పక్కగా కారుతోంది", "మురుగునీటి సీపేజ్ వల్ల కాంపౌండ్ వాల్స్ దెబ్బతిని భవనాలు బీటలు వారుతున్నాయి", "డ్రైనేజీ చాంబర్ జాయింట్ ను రిపేర్ చేసి లీకేజీని శాశ్వతంగా ఆపండి"],
            'te_latn': ["Drainage pipe joint disconnected continuous sewage pooling near houses", "Sewage seepage entering house compound walls damage happening", "Sewer chamber joint cement sealing repair cheyandi"]
        },
        {
            'id': 'DR_22', 'type': 'sewage_leakage', 'is_emg': False, 'sev': 3,
            'en': ["Raw sewage oozing from pavement paver blocks onto public walkway", "Underground drainage leakage bubbling through tiles on pedestrian corridor", "Walkway pavement soaked in foul smelling sewer effluent repairing line required"],
            'te': ["ఫుట్‌పాత్ రాళ్ల సందుల నుండి మురుగు నీరు పైకి ఉబికి వస్తోంది విపరీతమైన దుర్వాసన", "కాలిబాట కింద ఉన్న డ్రైనేజీ పైపు లీక్ అయ్యి రోడ్డు అంతా బురదమయంగా మారింది", "పాదచారులు నడవలేకపోతున్నారు పైపులైన్ తవ్వి లీకేజీని రిపేర్ చేయండి"],
            'te_latn': ["Raw sewage oozing from pavement tiles onto walkway foul stench", "Underground drainage leakage bubbling up through footpath stones", "Footpath pavement soaked in sewer water fix pipeline leak"]
        },
        {
            'id': 'DR_23', 'type': 'sewage_leakage', 'is_emg': False, 'sev': 3,
            'en': ["Septic tank overflow seepage draining into open municipal rainwater canal", "Apartment complex illegally releasing raw sewage septic overflow into roadside gutter", "Untreated sewage discharged openly into stormwater drain generating toxic vapors"],
            'te': ["సెప్టిక్ ట్యాంక్ వ్యర్థాలను మునిసిపల్ వర్షపు నీటి కాలువలోకి అక్రమంగా వదులుతున్నారు", "అపార్ట్‌మెంట్ వారు మురుగు నీటిని శుద్ధి చేయకుండా నేరుగా రోడ్డుపైకి వదులుతున్నారు", "చట్టవిరుద్ధంగా మురుగు నీటిని వదిలే వారిపై కాలుష్య నియంత్రణ చర్యలు తీసుకోండి"],
            'te_latn': ["Septic tank overflow seeping into open stormwater canal foul gases", "Apartment releasing raw sewage into municipal gutter take action", "Untreated sewage discharge into street drain stop illegal pipe"]
        },
        {
            'id': 'DR_24', 'type': 'sewage_leakage', 'is_emg': False, 'sev': 3,
            'en': ["Sewerage pumping station pipeline fissure discharging sludge into street", "Municipal sewage booster main burst, sludge flooding adjacent residential pocket", "Pumping station outflow line damaged, black effluent inundating lane"],
            'te': ["సీవరేజ్ పంపింగ్ స్టేషన్ మెయిన్ పైపు పగిలి మురుగు కాలనీ వీధుల్లోకి ప్రవహిస్తోంది", "పంపింగ్ మెషిన్ పైపు లీకేజీ వల్ల వందలాది ఇళ్ల ముందు నల్లటి మురుగు నిలిచింది", "పంపింగ్ స్టేషన్ ఇంజనీర్లు స్పందించి పైపులైన్ అత్యవసర రిపేర్ చేపట్టాలి"],
            'te_latn': ["Sewerage pumping station pipe burst discharging black sludge into street", "Municipal sewage booster line fissure flooding houses repair fast", "Pumping station outflow pipeline burst emergency repairs needed"]
        },
        {
            'id': 'DR_25', 'type': 'sewage_leakage', 'is_emg': False, 'sev': 2,
            'en': ["Commercial dairy cattle shed washing cow dung into drain causing sewage jam", "Cattle dung effluent clogging colony drainage pipes with putrid smell", "Dairy farm owner dumping dung slurry directly into municipal underground sewer"],
            'te': ["పాడి గేదెల వ్యర్థాలు పేడను కాలువలోకి కడగడంతో డ్రైనేజీ పూర్తిగా జామ్ అయ్యింది", "గేదెల పేడ కాలువలో నిండిపోయి మురుగు నీరు ముందుకు పోకుండా ఆగిపోయింది", "డైరీ ఫామ్ పై చర్యలు తీసుకుని కాలువలో పేడ వ్యర్థాలు వేయకుండా ఆపండి"],
            'te_latn': ["Dairy cattle shed washing dung into drain causing complete sewage block", "Cow dung slurry clogging colony sewer pipes terrible smell clear it", "Dairy owner dumping cattle waste in municipal drain inspect and fine"]
        }
    ],

    # =========================================================================
    # DEPARTMENT 3: WATER SUPPLY & QUALITY (water_supply) - 25 Clusters
    # =========================================================================
    'water_supply': [
        # No Water Supply (Clusters 1-7)
        {
            'id': 'WS_01', 'type': 'no_water_supply', 'is_emg': False, 'sev': 3,
            'en': ["Zero municipal drinking water supply in our ward for past five days", "No tap water since Monday, residents forced to buy private water tankers", "Complete drinking water outage in colony for over 96 hours, severe crisis"],
            'te': ["గత ఐదు రోజులుగా మా వార్డులో మునిసిపల్ తాగునీటి సరఫరా పూర్తిగా నిలిచిపోయింది", "కుళాయిల్లో బొట్టు నీరు రావడం లేదు ప్రైవేట్ వాటర్ కొనుక్కోలేక ప్రజలు అల్లాడుతున్నారు", "నాలుగు రోజులుగా నీళ్లు లేక కాలనీ ప్రజలు తీవ్ర ఇబ్బందులు పడుతున్నారు ట్యాంకర్లు పంపండి"],
            'te_latn': ["Past 5 days nundi municipal drinking water supply zero taps completely dry", "One drop water kuda ravadam ledu colony people suffering buy private tankers", "No water supply since 4 days emergency water tanker supply cheyandi"]
        },
        {
            'id': 'WS_02', 'type': 'no_water_supply', 'is_emg': False, 'sev': 3,
            'en': ["Public borewell motor burnt out, low-income slum layout left without water", "Community water pump burned due to voltage spike, taps totally dead", "Submersible water motor failed in municipal pump house repair immediately"],
            'te': ["మునిసిపల్ బోరు మోటారు కాలిపోయింది పేదల కాలనీలో నీరందక అవస్థలు పడుతున్నారు", "వోల్టేజ్ సమస్యతో వాటర్ పంప్ మోటార్ పాడైంది కుళాయిలకు నీరు చేరడం లేదు", "వాటర్ వర్క్స్ అధికారులు స్పందించి కొత్త మోటారు అమర్చాలి లేదా రిపేర్ చేయాలి"],
            'te_latn': ["Borewell pump motor burn ayindi taps lo water stop ayindi", "Community water motor damaged voltage issue repair fast or tanker send", "Public drinking water motor failure replace motor immediately"]
        },
        {
            'id': 'WS_03', 'type': 'no_water_supply', 'is_emg': False, 'sev': 3,
            'en': ["Main water distribution line valve closed by maintenance crew and not restored", "Water valve operator forgot to open sluice valve to our residential pocket", "Valve breakdown halting clean water flow to more than four hundred families"],
            'te': ["వాటర్ వర్క్స్ సిబ్బంది వాల్వ్ కట్టేసి తిరిగి తెరవడం మరిచిపోవడంతో సరఫరా ఆగింది", "మా వీధికి వచ్చే మెయిన్ వాటర్ వాల్వ్ పాడైపోయింది నీరు రావడం లేదు", "వాటర్ వాల్వ్ సరిచేసి కాలనీకి తాగునీటి సరఫరాను పునరుద్ధరించండి"],
            'te_latn': ["Water distribution valve closed and not opened supply halted to colony", "Main water sluice valve repair cheyandi water reach avvatledu", "Water valve operator issue taps empty since two days check line"]
        },
        {
            'id': 'WS_04', 'type': 'no_water_supply', 'is_emg': False, 'sev': 3,
            'en': ["Scheduled water supply timing altered without public notice, residents missed water", "Municipal drinking water supplied only for 10 minutes at midnight, taps dry", "Erratic water supply timings causing working people and elders extreme hardship"],
            'te': ["ముందస్తు సమాచారం లేకుండా నీటి సరఫరా సమయాన్ని మార్చేశారు ప్రజలకు నీరు అందలేదు", "రాత్రి అర్ధరాత్రి పూట పది నిమిషాలు మాత్రమే నీరు ఇచ్చి ఆపేశారు నిద్రలు మాని నిరీక్షించాలా", "క్రమం తప్పకుండా నిర్దిష్ట వేళల్లో రోజుకు రెండు గంటలు నీరు సరఫరా చేయండి"],
            'te_latn': ["Water supply timing changed without notice taps dry for 3 days", "Midnight 10 minutes matrame water release chesaru public suffering", "Drinking water schedule regularize cheyandi fixed morning hours"]
        },
        {
            'id': 'WS_05', 'type': 'no_water_supply', 'is_emg': False, 'sev': 3,
            'en': ["Tail-end layout completely cut off from municipal drinking water grid", "Last two streets of ward never receive water due to faulty branch connection", "Drinking water pipeline dead end has zero pressure, no water for weeks"],
            'te': ["కాలనీ చివర ఉన్న వీధులకు మునిసిపల్ తాగునీరు అసలు చేరడం లేదు", "పైప్‌లైన్ చివర ఉండటంతో నీరంతా ముందే అయిపోయి మా ఇళ్లకు రావడం లేదు", "టెయిల్ ఎండ్ ఇళ్లకు ప్రత్యేక బూస్టర్ లైన్ వేసి తాగునీటి సమస్యను పరిష్కరించండి"],
            'te_latn': ["Tail end colony streets zero water supply pipeline pressure insufficient", "Last lane houses never receive water booster line connection required", "Colony dead end taps completely dry solve drinking water crisis"]
        },
        {
            'id': 'WS_06', 'type': 'no_water_supply', 'is_emg': False, 'sev': 3,
            'en': ["Municipal water tanker contracted to supply water skipped colony for 3 days", "Contract tanker driver selling municipal water to commercial builders instead of ward", "Drinking water tanker diverted illegally, residents parched demand investigation"],
            'te': ["మునిసిపాలిటీ కేటాయించిన వాటర్ ట్యాంకర్ మా కాలనీకి రాకుండా వేరే చోటకు వెళ్లిపోతోంది", "ప్రభుత్వ వాటర్ ట్యాంకర్ డ్రైవర్ నీటిని ప్రైవేట్ నిర్మాణాలకు అమ్ముకుంటున్నాడు విచారణ చేయండి", "మా వార్డుకు రావాల్సిన ట్యాంకర్ ను సక్రమంగా పంపించి నీటిని పంపిణీ చేయించండి"],
            'te_latn': ["Municipal water tanker skipped our colony for past 3 days crisis", "Tanker driver selling public water to private construction investigate", "Send municipal drinking water tanker to our street immediately"]
        },
        {
            'id': 'WS_07', 'type': 'no_water_supply', 'is_emg': False, 'sev': 3,
            'en': ["Water supply disrupted due to electrical feeder trip at central water works", "Raw water treatment plant transformer failure halted city drinking supply", "Water works sub-station breakdown keeping storage reservoirs empty"],
            'te': ["హెడ్ వాటర్ వర్క్స్ వద్ద కరెంట్ సరఫరా నిలిచిపోవడంతో నగరమంతటా తాగునీరు ఆగింది", "వాటర్ పంపింగ్ స్టేషన్ వద్ద విద్యుత్ సమస్య వల్ల రిజర్వాయర్లు నిండలేదు", "విద్యుత్ సమస్యను త్వరగా పరిష్కరించి తాగునీటి సరఫరాను పునరుద్ధరించండి"],
            'te_latn': ["Central water works power trip valla city water supply halted", "Water treatment plant motor sub station breakdown reservoirs empty", "Restore electricity at water works and resume tap water supply"]
        },
        # Water Contamination (Clusters 8-13)
        {
            'id': 'WS_08', 'type': 'water_contamination', 'is_emg': True, 'sev': 4,
            'en': ["Tap water coming out dark black and foul-smelling like gutter sludge", "Municipal tap water mixed with sewage, highly toxic contaminated liquid", "Drinking water supplied is cloudy brown with sewage odor, residents falling sick"],
            'te': ["కుళాయిల్లో నల్లటి మురికి నీరు వస్తోంది డ్రైనేజీ కంపు తాగడానికి వీల్లేదు", "మునిసిపల్ కుళాయి నీరు డ్రైనేజీ కలిసి కలుషితమైంది పిల్లలు వాంతులు చేసుకుంటున్నారు", "కలుషిత నీరు తాగడం వల్ల కాలనీలో కలరా ప్రబలే ప్రమాదం ఉంది వెంటనే సరఫరా ఆపండి"],
            'te_latn': ["Taps lo black dirty water vastundi sewage foul smell panikiradu", "Municipal tap water mixed with drainage highly contaminated disease risk", "Drinking water dirty brown smell valla vomiting and illness stop supply"]
        },
        {
            'id': 'WS_09', 'type': 'water_contamination', 'is_emg': True, 'sev': 4,
            'en': ["Overhead municipal water storage tank filled with dead worms and algae", "Overhead reservoir tank not cleaned for eight months, live worms in tap water", "Visible sediment and insect larvae coming out of household drinking water taps"],
            'te': ["ఓవర్‌హెడ్ వాటర్ ట్యాంక్ క్లీన్ చేయకపోవడం వల్ల కుళాయి నీటిలో పురుగులు వస్తున్నాయి", "నీటి ట్యాంకులో నాచు పేరుకుపోయింది నీటిలో పచ్చటి రంగు దుర్వాసన వస్తోంది", "మున్సిపల్ రిజర్వాయర్ ట్యాంక్ ను బ్లీచింగ్ తో శుభ్రం చేసి క్లోరినేషన్ జరపండి"],
            'te_latn': ["Overhead water tank not cleaned worms and insects coming from taps", "Water tank full of green algae contaminated water tap supply", "Clean overhead water reservoir with bleaching and chlorination fast"]
        },
        {
            'id': 'WS_10', 'type': 'water_contamination', 'is_emg': True, 'sev': 4,
            'en': ["Severe chemical chlorine overdose in tap water causing burning eyes and throat", "Strong chemical bleaching smell in drinking water unfit for cooking or drinking", "Water bleaching powder overdose causing severe skin burning and vomiting"],
            'te': ["మునిసిపల్ నీటిలో బ్లీచింగ్ మరియు క్లోరిన్ మోతాదు ఎక్కువై ఘాటైన వాసన వస్తోంది", "నీరు తాగితే గొంతు మంట చర్మ వ్యాధులు వస్తున్నాయి క్లోరిన్ లెవల్స్ సరిచూడండి", "కుళాయి నీటిలో రసాయన వాసన వస్తోంది వాటర్ క్వాలిటీ టెస్ట్ చేయించాలి"],
            'te_latn': ["Excess chlorine overdose in municipal taps burning throat and smell", "Tap water chemical smell too strong unable to drink or cook", "Bleaching chemical heavy overdose in drinking water inspect quality"]
        },
        {
            'id': 'WS_11', 'type': 'water_contamination', 'is_emg': True, 'sev': 4,
            'en': ["Colony drinking water line fractured inside sewage drain canal", "Drinking water pipeline submerged in open drain, fecal water suction into taps", "Grave public health emergency: water pipeline leaking inside raw sewage ditch"],
            'te': ["మురుగు కాలువ లోపల ఉన్న మంచి నీటి పైపు పగిలి డ్రైనేజీ నీరు కుళాయిల్లోకి లాగుతోంది", "డ్రైనేజీ కాలువలో మునిగి ఉన్న తాగునీటి పైపు పగిలి తీవ్ర కాలుష్యం ఏర్పడింది", "పైపును డ్రైనేజీ బయటకు మార్చి కొత్త హెచ్‌డీపీఈ పైప్‌లైన్ వేయండి అత్యవసరం"],
            'te_latn': ["Colony drinking water pipe broken inside sewage canal fecal suction", "Drinking water pipeline submerged in open drain extreme health danger", "Shift water line outside drain and replace with new pipe immediately"]
        },
        {
            'id': 'WS_12', 'type': 'water_contamination', 'is_emg': False, 'sev': 3,
            'en': ["Yellow muddy turbid water flowing from municipal taps after pipeline repair", "Tap water full of red clay mud and sand sediment clogging water purifiers", "Municipal tap water extremely muddy brown color filter cartridges getting choked"],
            'te': ["కుళాయిల్లో ఎర్రటి మట్టి నీరు వస్తోంది ఫిల్టర్లు మోటార్లు జామ్ అయిపోతున్నాయి", "మట్టి బురద నీరు సరఫరా అవుతోంది బట్టలు ఉతకడానికి కూడా పనికి రావడం లేదు", "పైప్‌లైన్ ఫ్లషింగ్ చేసి తేటటి తాగునీటిని సరఫరా చేయాల్సిందిగా కోరుతున్నాం"],
            'te_latn': ["Yellow muddy turbid water coming from taps after repair work", "Tap water full of mud and sand sediment filter candles ruined", "Muddy brown tap water flushing lines needed clear drinking water"]
        },
        {
            'id': 'WS_13', 'type': 'water_contamination', 'is_emg': True, 'sev': 4,
            'en': ["Outbreak of acute gastroenteritis in colony due to contaminated tap water", "Multiple hospitalized with severe diarrhea after drinking municipal tap water", "Contaminated municipal water epidemic risk: health wing must sample and test water"],
            'te': ["కలుషిత కుళాయి నీరు తాగి కాలనీలో పలువురు డయేరియాతో ఆసుపత్రి పాలయ్యారు", "గ్యాస్ట్రో ఎంటరైటిస్ కేసులు పెరుగుతున్నాయి మునిసిపల్ నీరే దీనికి కారణం తనిఖీ చేయండి", "నీటి నమూనాలను ల్యాబ్ లో పరీక్షించి సురక్షితమైన నీరు అందించండి అత్యవసరం"],
            'te_latn': ["Acute diarrhea outbreak in colony due to contaminated municipal tap water", "Multiple hospital admissions after drinking tap water collect lab samples", "Contaminated drinking water medical emergency inspect pipeline"]
        },
        # Pipeline Leakage (Clusters 14-19)
        {
            'id': 'WS_14', 'type': 'pipeline_leakage', 'is_emg': False, 'sev': 3,
            'en': ["Major underground water main burst flooding street with thousands of liters", "High pressure drinking water pipe burst, clean water gushing 10 feet into air", "Main feeder pipeline split open road inundated with precious drinking water"],
            'te': ["ప్రధాన మంచినీటి పైపులైన్ పగిలి వేలాది లీటర్ల తాగునీరు రోడ్డుపై వృధాగా పోతోంది", "హై ప్రెజర్ వాటర్ పైపు పగిలి మంచి నీరు వరదలా వీధుల్లో పారుతోంది", "రోడ్డు కింద ఉన్న తాగునీటి మెయిన్ పైపు లీకేజీని అత్యవసరంగా అరికట్టండి"],
            'te_latn': ["Main drinking water pipe burst clean water gushing out onto road waste", "Underground water main ruptured thousands of liters drinking water wasted", "Water pipeline burst flood on street turn off supply valve and repair"]
        },
        {
            'id': 'WS_15', 'type': 'pipeline_leakage', 'is_emg': False, 'sev': 2,
            'en': ["Public street standpost faucet broken, clean water leaking non-stop into gutter", "Public street tap valve sheared off, water flowing 24/7 creating muddy sludge", "Damaged municipal public tap leaking continuous fresh water onto road"],
            'te': ["వీధి కుళాయి విరిగిపోయి మంచి నీరు నిరంతరం రోడ్డుపై కాలువలా ప్రవహిస్తోంది", "పబ్లిక్ ట్యాప్ వాల్వ్ పాడైపోయింది నీరు రోజంతా కారి బురదమయంగా మారింది", "కుళాయికి కొత్త ట్యాప్ బిగించి తాగునీటి వృధాను అరికట్టండి"],
            'te_latn': ["Public street tap broken water leaking continuously into roadside mud", "Public standpost faucet broken non stop fresh water wastage", "Street public tap valve replace cheyandi water wasting"]
        },
        {
            'id': 'WS_16', 'type': 'pipeline_leakage', 'is_emg': False, 'sev': 3,
            'en': ["Drinking water distribution pipe joint split open beneath colony asphalt", "Water gushing from road joints eroding asphalt foundation and creating cavities", "Continuous underground water leak washed away road sub-base forming hollow"],
            'te': ["రోడ్డు కింద తాగునీటి పైపు జాయింట్ పగిలి నీరు పైకి ఉబికి రోడ్డును దెబ్బతీస్తోంది", "తాగునీటి లీకేజీ వల్ల తారు రోడ్డు కింద మట్టి కొట్టుకుపోయి రోడ్డు కుంగిపోతోంది", "పైప్‌లైన్ జాయింట్ ను తవ్వి సీల్ చేసి రోడ్డును కాపాడండి"],
            'te_latn': ["Drinking water pipe joint split underground water gushing onto asphalt", "Water leak eroding road foundation beneath bitumen repair line", "Underground pipe joint crack fix leak before road caves in"]
        },
        {
            'id': 'WS_17', 'type': 'pipeline_leakage', 'is_emg': False, 'sev': 3,
            'en': ["Sluice valve chamber flooded with massive water pipe leak near bypass", "Water control valve flange gasket blown, water shooting out of valve box", "Municipal water junction chamber submerged in gushing fresh water"],
            'te': ["వాల్వ్ చాంబర్ లో పైపు కప్లింగ్ ఊడిపోయి వేల లీటర్ల నీరు రోడ్డుపై పారుతోంది", "మెయిన్ వాల్వ్ వద్ద రబ్బరు వాషర్ పోయి నీరు ఫౌంటెన్ లా ఎగసిపడుతోంది", "వాటర్ వాల్వ్ బాక్స్ తనిఖీ చేసి లీకేజీని అరికట్టాల్సిందిగా విజ్ఞప్తి"],
            'te_latn': ["Sluice valve chamber flooded with major water pipe leak near bypass", "Water valve flange gasket blown water fountain from valve box", "Valve chamber pipe coupling replace gasket and stop water waste"]
        },
        {
            'id': 'WS_18', 'type': 'pipeline_leakage', 'is_emg': False, 'sev': 2,
            'en': ["Air release valve on drinking water main continuously spurting water jet", "Defective kinetic air valve on municipal pipeline spraying water onto power lines", "Air valve stuck open wasting drinking water non-stop on highway verge"],
            'te': ["పైప్‌లైన్ పై ఉన్న ఎయిర్ వాల్వ్ పాడైపోయి నిరంతరం నీటి తుంపర్లు రోడ్డుపై కొడుతున్నాయి", "ఎయిర్ రిలీజ్ వాల్వ్ జామ్ అయి నీరు ఆగకుండా కారుతోంది విద్యుత్ తీగలపై పడుతోంది", "ఎయిర్ వాల్వ్ ను రిపేర్ చేసి నీటి వృధాను మరియు విద్యుత్ ప్రమాదాన్ని నివారించండి"],
            'te_latn': ["Air release valve on water main spurting water jet onto highway verge", "Air valve stuck open wasting clean water spray onto electric lines", "Repair kinetic air valve on water pipeline immediately"]
        },
        {
            'id': 'WS_19', 'type': 'pipeline_leakage', 'is_emg': False, 'sev': 2,
            'en': ["Illegal water connection tapping punctured municipal pipe causing leak", "Unauthorized private pipe tapping causing loss of drinking water and mud pool", "Illegal drill hole on water main left improperly sealed leaking fresh water"],
            'te': ["అక్రమ కుళాయి కనెక్షన్ కోసం పైపును పగలగొట్టి వదిలేయడంతో నీరు వృధాగా పోతోంది", "పైప్‌లైన్ కు అనుమతి లేని రంధ్రాలు వేసి నీటిని చౌర్యం చేస్తున్నారు లీకేజీ అవుతోంది", "అక్రమ కనెక్షన్లను తొలగించి పైప్‌లైన్ లీక్ ను క్లాంప్ వేసి సరిచేయండి"],
            'te_latn': ["Illegal water connection tapping punctured municipal pipeline causing leak", "Unauthorized drilling on water main leaking drinking water clamp pipe", "Remove illegal tap connection and fix pipeline puncture"]
        },
        # Low Water Pressure (Clusters 20-25)
        {
            'id': 'WS_20', 'type': 'low_water_pressure', 'is_emg': False, 'sev': 2,
            'en': ["Extremely feeble water pressure in colony, takes one hour to fill single bucket", "Tap water trickles in drops, motor unable to draw water to storage tank", "Low pipeline pressure in residential layout, upper floors completely dry"],
            'te': ["కుళాయిల్లో నీటి ప్రెజర్ చాలా తక్కువగా ఉంది బిందెడు నీళ్లు పట్టడానికి గంట పడుతోంది", "మోటార్ వేసినా నీరు రావడం లేదు కేవలం బొట్లు బొట్లుగా మాత్రమే పడుతోంది", "కాలనీ చివరి ఇళ్లకు నీటి ప్రెజర్ సరిపోవడం లేదు ప్రెజర్ పెంచాలి"],
            'te_latn': ["Taps lo water pressure very low drops matrame padutunnayi takes 1 hour", "Water pressure zero motor vesina water lift kavadam ledu", "Tail end houses water pressure low booster pump check cheyandi"]
        },
        {
            'id': 'WS_21', 'type': 'low_water_pressure', 'is_emg': False, 'sev': 2,
            'en': ["Air lock in underground distribution pipeline causing zero tap pressure", "Water pipeline clogged with calcium scaling restricting water flow to lane", "Air release valve damaged resulting in air pocket blocking water velocity"],
            'te': ["పైప్‌లైన్ లో ఎయిర్ లాక్ పడటంతో నీటి ప్రవాహం ఆగిపోయింది ప్రెజర్ రావడం లేదు", "పైపుల్లో గాలి చేరింది వాటర్ వర్క్స్ ప్లంబర్ వచ్చి ఎయిర్ రిలీజ్ చేయాలి", "పైప్‌లైన్ జామ్ అయి నీరు చాలినంతగా రావడం లేదు పరిశీలించండి"],
            'te_latn': ["Pipeline air lock valla zero water pressure plumbers air release cheyandi", "Underground pipe air lock water not coming with force check lines", "Air valve issue in drinking water pipe lines inspect pressure"]
        },
        {
            'id': 'WS_22', 'type': 'low_water_pressure', 'is_emg': False, 'sev': 2,
            'en': ["Direct on-line suction pumps installed by upstream houses stealing all pressure", "Heavy 2HP motors connected directly to municipal main starving neighboring homes", "Illegal inline booster pumps causing negative pressure and dry taps for colony"],
            'te': ["కొందరు ఇళ్లల్లో నేరుగా మెయిన్ లైన్ కు 2హెచ్‌పీ మోటార్లు వేసి నీటిని లాగేస్తున్నారు", "ఆన్‌లైన్ మోటార్ల వల్ల పక్క ఇళ్లకు బొట్టు నీరు కూడా రావడం లేదు తనిఖీ చేయండి", "మునిసిపల్ లైన్ కు డైరెక్ట్ మోటార్లు పెట్టిన వారిపై దాడులు చేసి మోటార్లు జప్తు చేయండి"],
            'te_latn': ["Direct online suction pumps by upstream houses stealing water pressure", "2HP motors directly connected to municipal main taps dry for others", "Inspect and seize illegal booster motors on municipal line"]
        },
        {
            'id': 'WS_23', 'type': 'low_water_pressure', 'is_emg': False, 'sev': 2,
            'en': ["Distribution control valve partially throttled by line inspector, low flow", "Sluice valve opened only quarter turn reducing tap discharge to trickle", "Water department operator throttling supply valve to colony inspect valve setting"],
            'te': ["లైన్ ఇన్‌స్పెక్టర్ వాల్వ్ ను సగం మాత్రమే తెరవడంతో నీటి ప్రెజర్ పడిపోయింది", "వాల్వ్ సరిగ్గా తిప్పకపోవడం వల్ల నీరు సన్నటి ధారగా మాత్రమే వస్తోంది", "వాల్వ్ గేట్ ను పూర్తి స్థాయిలో తెరిచి సరిపడా ప్రెజర్ తో నీరు అందించండి"],
            'te_latn': ["Distribution valve opened only quarter turn tap flow very feeble", "Line operator throttled supply valve low water discharge check valve", "Open sluice valve fully to restore adequate water pressure"]
        },
        {
            'id': 'WS_24', 'type': 'low_water_pressure', 'is_emg': False, 'sev': 2,
            'en': ["Water supply pipe diameter too narrow for newly expanded residential colony", "Decades old 2-inch GI pipeline unable to cater to five hundred new tenements", "Pipeline capacity choked, demand upgrading to 6-inch HDPE distribution line"],
            'te': ["కాలనీ విస్తరించినా పాత చిన్న పైపులైన్ మార్చకపోవడంతో నీటి ప్రెజర్ రావడం లేదు", "రెండు అంగుళాల పాత పైపు వందలాది ఇళ్లకు సరిపోవడం లేదు కొత్త పెద్ద పైపు వేయాలి", "పెరిగిన జనాభాకు అనుగుణంగా కొత్త 6 అంగుళాల పైప్‌లైన్ మంజూరు చేయండి"],
            'te_latn': ["Water pipe diameter too narrow for expanded colony feeble pressure", "Old 2 inch GI pipe unable to cater to 500 houses upgrade to 6 inch", "Pipeline capacity upgrade required for colony water pressure"]
        },
        {
            'id': 'WS_25', 'type': 'low_water_pressure', 'is_emg': False, 'sev': 2,
            'en': ["Overhead water reservoir operated at low head height causing poor gravity feed", "Water tank kept half empty, lack of gravitational pressure for third floor taps", "Reservoir water level depleted before supply hours resulting in zero pressure"],
            'te': ["ఓవర్‌హెడ్ ట్యాంకును పూర్తిగా నింపకపోవడం వల్ల గ్రావిటీ ప్రెజర్ తగ్గిపోయింది", "ట్యాంకులో నీటి మట్టం తక్కువగా ఉండటంతో కుళాయిల్లో నీరు ఫోర్స్ గా రావడం లేదు", "వాటర్ ట్యాంకును పూర్తి సామర్థ్యం మేరకు నింపి ప్రెజర్ తో సరఫరా చేయండి"],
            'te_latn': ["Overhead tank half empty lack of gravity pressure for taps", "Reservoir water level low feeble tap flow fill tank completely", "Water storage tank head pressure insufficient fill reservoir to full"]
        }
    ],

    # =========================================================================
    # DEPARTMENT 4: ELECTRICAL & STREET LIGHTING (street_lights) - 25 Clusters
    # =========================================================================
    'street_lights': [
        # Street Light Failure (Clusters 1-9)
        {
            'id': 'EL_01', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["All street lights on entire bypass road dark for past two weeks", "Ten consecutive LED street lights not turning on, complete pitch darkness", "Street lighting blackout along colony road leading to chain snatching fear"],
            'te': ["మా కాలనీలో అన్ని వీధి దీపాలు వెలగడం లేదు రాత్రిపూట అంతా చిమ్మచీకటిగా ఉంది", "రెండు వారాలుగా వీధి లైట్లు పాడైపోయాయి మహిళలు రాత్రి నడవడానికి భయపడుతున్నారు", "ఎల్ఈడీ వీధి లైట్లు ఆరిపోయాయి వెంటనే కొత్త బల్బులు వేయించండి"],
            'te_latn': ["Colony lo all street lights 2 weeks nundi velagadam ledu pitch dark", "LED street lights not working theft and snatching fear in dark", "Street light switch repair cheyandi night time total darkness"]
        },
        {
            'id': 'EL_02', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["Street light fixture flickering rapidly and making buzzing electrical noise", "Faulty choke in street light pole causing strobe flickering all night", "Defective LED luminaire sparking intermittently in front of residential house"],
            'te': ["వీధి లైట్ బల్బు మినుకు మినుకుమంటూ సౌండ్ వస్తోంది ఎప్పుడైనా పేలిపోవచ్చు", "స్తంభంపై ఉన్న లైట్ నిరంతరం బజ్జింగ్ శబ్దంతో మినుకుమినుకుమంటోంది", "లైట్ ఫిక్చర్ పాడైపోయింది ఎలక్ట్రికల్ టీమ్ వచ్చి బల్బు మార్చాలి"],
            'te_latn': ["Street light flickering continuously buzzing sound danger", "Faulty choke lamp blinking all night disturbing residents replace bulb", "Street light sparking and blinking fix electrical fixture"]
        },
        {
            'id': 'EL_03', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["Street lights continuously burning in bright broad daylight for ten days", "Daytime street lighting waste of municipal public electricity", "Automatic daylight sensor timer defective, lamps stay on 24 hours a day"],
            'te': ["పగటిపూట కూడా వీధి లైట్లు ఆపకుండా వెలుగుతున్నాయి విద్యుత్ వృధా అవుతోంది", "టైమర్ స్విచ్ పాడైపోయి 24 గంటలూ లైట్లు వెలుగుతూనే ఉన్నాయి సరిచేయండి", "పగటివేళ లైట్లు ఆఫ్ చేయించేలా మునిసిపల్ విద్యుత్ విభాగం చర్యలు తీసుకోవాలి"],
            'te_latn': ["Daytime kuda street lights 24 hours on electricity wastage", "Timer switch defective daylight sensor not working lamps on in sun", "Day time lights turn off cheyandi automatic timer repair"]
        },
        {
            'id': 'EL_04', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["Main MCB circuit breaker tripped in street lighting control junction", "Phase fuse blown for colony lighting feeder, entire ward lane in darkness", "Short circuit in control box knocked out all LED fixtures on market road"],
            'te': ["వీధి దీపాల జంక్షన్ బాక్స్ లో ఎంసీబీ ట్రిప్ అయ్యి కాలనీ అంతా చీకటిమయమైంది", "ఫ్యూజ్ పోవడంతో వీధి లైట్లు వెలగడం లేదు ఎలక్ట్రీషియన్ వచ్చి ఫ్యూజ్ వేయాలి", "లైటింగ్ ఫీడర్ బాక్స్ లో షార్ట్ సర్క్యూట్ అయ్యింది వెంటనే బాగుచేయండి"],
            'te_latn': ["Main MCB tripped in street light control box colony in darkness", "Phase fuse blown street lights off send municipal lineman to fix", "Short circuit in street lighting junction box repair breaker"]
        },
        {
            'id': 'EL_05', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["Newly erected electric pole has no street light bulb fixture mounted", "Pole installed six months ago left without lamp bracket or wiring", "Dark pocket on colony road because two poles have empty brackets"],
            'te': ["కొత్తగా వేసిన కరెంట్ స్తంభానికి వీధి లైట్ ఫిక్చర్ అమర్చలేదు చీకటిగా ఉంది", "స్తంభం వేసి ఆరు నెలలైనా బల్బు పెట్టలేదు మహిళలు రాత్రి తిరగలేకపోతున్నారు", "ఖాళీ స్తంభానికి కొత్త ఎల్ఈడీ లైట్ అమర్చాల్సిందిగా కోరుతున్నాం"],
            'te_latn': ["New electric pole has no light fixture dark pocket on street", "Pole installed 6 months ago but no bulb fitted install LED light", "Empty lamp bracket on electric pole fit new street luminaire"]
        },
        {
            'id': 'EL_06', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["Dense tree foliage completely covering street light bulb blocking illumination", "Tree branches overgrown around street light keeping the pavement pitch dark", "Municipal pruner needed to cut branches blinding the road street light"],
            'te': ["చెట్ల కొమ్మలు పెరిగిపోయి వీధి లైట్ బల్బును కప్పేశాయి రోడ్డుపై వెలుతురు పడటం లేదు", "కొమ్మల వల్ల లైట్ వెలుగు కిందకు రావడం లేదు చెట్ల కొమ్మలను నరికించండి", "స్ట్రీట్ లైట్ చుట్టూ ఉన్న కొమ్మలను కత్తిరించి రోడ్డుపై వెలుతురు వచ్చేలా చేయండి"],
            'te_latn': ["Tree branches overgrown covering street light pitch dark on road", "Foliage blocking street light beam municipal branch cutting needed", "Prune tree branches blinding the municipal street lamp"]
        },
        {
            'id': 'EL_07', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["Underground lighting power cable snapped during road widening works", "Excavator cut underground street light power cable, ten poles dead", "Severed street light cable beneath asphalt needs trenching and jointing"],
            'te': ["రోడ్డు పనుల తవ్వకాల్లో వీధి లైట్ల అండర్‌గ్రౌండ్ కేబుల్ తెగిపోయింది లైట్లు ఆగిపోయాయి", "జేసీబీ తగిలి కేబుల్ కట్ అయ్యింది వరుసగా 10 స్తంభాలకు కరెంట్ రావడం లేదు", "తెగిపోయిన భూగర్భ విద్యుత్ కేబుల్ ను జాయింట్ చేసి లైట్లు వెలిగించండి"],
            'te_latn': ["Underground street light cable cut during road excavation work", "Excavator cut power cable 10 poles dead underground jointing needed", "Severed street lighting cable repair urgently to restore light"]
        },
        {
            'id': 'EL_08', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["High mast tower flood lights at major traffic circle non functional", "Ring road high mast light completely switched off, critical intersection dark", "Four out of six floodlight bulbs fused on municipal junction high mast tower"],
            'te': ["ప్రధాన కూడలి వద్ద ఉన్న హైమాస్ట్ లైట్ వెలగడం లేదు రాత్రి ట్రాఫిక్ కు తీవ్ర అంతరాయం", "సర్కిల్ వద్ద హైమాస్ట్ టవర్ లైట్లు ఆరిపోయాయి నిత్యం ప్రమాదాలు జరుగుతున్నాయి", "హైమాస్ట్ బల్బులను మార్చి కూడలిలో నిరంతరం వెలుతురు ఉండేలా చేయండి"],
            'te_latn': ["High mast tower flood lights at major circle non functional dark intersection", "Ring road high mast lighting off accidents happening replace bulbs", "Traffic junction high mast lights repair fast"]
        },
        {
            'id': 'EL_09', 'type': 'street_light_failure', 'is_emg': False, 'sev': 2,
            'en': ["Solar street light panel covered with bird droppings and battery dead", "Solar powered LED street light battery not holding charge, turns off by 8 PM", "Defective solar luminaire battery needs replacement on bypass colony lane"],
            'te': ["సోలార్ వీధి లైట్ బ్యాటరీ పాడైపోయింది రాత్రి 8 గంటలకే లైట్ ఆరిపోతోంది", "సోలార్ ప్యానెల్ దెబ్బతినడంతో లైట్ వెలగడం లేదు కొత్త బ్యాటరీ అమర్చాలి", "సోలార్ వీధి దీపాన్ని పరిశీలించి రిపేర్ చేయాల్సిందిగా విజ్ఞప్తి"],
            'te_latn': ["Solar street light battery dead turns off by 8pm replace battery", "Solar panel defective street light not working repair luminaire", "Solar street light maintenance required battery replacement needed"]
        },
        # Damaged Electric Pole (Clusters 10-17)
        {
            'id': 'EL_10', 'type': 'damaged_electric_pole', 'is_emg': True, 'sev': 4,
            'en': ["Concrete street light pole broken at base and leaning 45 degrees over road", "Cracked electric pole ready to collapse onto traffic, extreme emergency", "Heavy vehicle rammed into electrical pole, concrete shattered with reinforcement bent"],
            'te': ["విద్యుత్ స్తంభం అడుగుభాగంలో విరిగిపోయి రోడ్డుపైకి ప్రమాదకరంగా వంగిపోయింది", "కరెంట్ స్తంభం ఎప్పుడైనా రోడ్డుపై పడిపోయేలా ఉంది ప్రాణాపాయం పొంచి ఉంది", "లారీ ఢీకొట్టడంతో విద్యుత్ స్తంభం విరిగింది విద్యుత్ సరఫరా ఆపి కొత్తది వేయండి"],
            'te_latn': ["Electric pole base broken leaning dangerously over road can fall anytime", "Concrete current pole cracked 45 degrees emergency replace new pole", "Vehicle hit electric post ready to collapse power cut and replace pole"]
        },
        {
            'id': 'EL_11', 'type': 'damaged_electric_pole', 'is_emg': True, 'sev': 4,
            'en': ["Rusted hollow steel light pole corroded completely through at ground level", "Iron light pole severely rusted by dog urine about to topple in gusty wind", "Metal electrical pole wobbling dangerously near crowded bus stop shelter"],
            'te': ["ఇనుప వీధి లైట్ స్తంభం తుప్పు పట్టి కింద పగిలిపోయింది గాలి వేస్తే పడిపోతుంది", "బస్టాండ్ వద్ద ఉన్న కరెంట్ స్తంభం తుప్పుపట్టి ఊగుతోంది ప్రజల ప్రాణాలకు ముప్పు", "తుప్పు పట్టిన స్తంభాన్ని తొలగించి కొత్త కాంక్రీట్ స్తంభం వేయించండి"],
            'te_latn': ["Rusted iron light pole completely corroded at base wobbling", "Metal electric pole broken near bus stand topple danger replace fast", "Iron street light pole base rusted wind valla collapse risk"]
        },
        {
            'id': 'EL_12', 'type': 'damaged_electric_pole', 'is_emg': True, 'sev': 4,
            'en': ["Wooden support holding electric cross-arm decayed and snapping wires", "Cross arm of high tension pole fractured, insulators hanging loose over street", "Transformer support pole foundation sinking after heavy rain risk of falling"],
            'te': ["ట్రాన్స్‌ఫార్మర్ స్తంభం పునాది కుంగిపోయింది ట్రాన్స్‌ఫార్మర్ రోడ్డుపై పడే ప్రమాదం ఉంది", "కరెంట్ స్తంభం పైభాగం విరిగిపోయి ఇన్సులేటర్లు వైర్లతో సహా వేలాడుతున్నాయి", "ట్రాన్స్‌ఫార్మర్ స్తంభాన్ని తక్షణమే సరిచేసి పెను ప్రమాదాన్ని నివారించండి"],
            'te_latn': ["Transformer support pole foundation sinking heavy risk of toppling", "Cross arm fractured insulators and wires hanging loose over street", "Transformer pole emergency repair required replace foundation"]
        },
        {
            'id': 'EL_13', 'type': 'damaged_electric_pole', 'is_emg': True, 'sev': 4,
            'en': ["Electric pole foundation eroded by open drainage ditch adjacent to it", "Open gutter running alongside electric pole has washed away supporting soil", "Pole tilted precariously towards drainage canal, foundation collapse imminent"],
            'te': ["డ్రైనేజీ కాలువ పక్కనే ఉన్న కరెంట్ స్తంభం కింద మట్టి కొట్టుకుపోయి స్తంభం వంగింది", "కాలువ నీటి కోత వల్ల విద్యుత్ స్తంభం పునాది బలహీనపడింది కూలిపోయే ప్రమాదం ఉంది", "స్తంభం చుట్టూ కాంక్రీట్ బేస్ వేసి స్తంభాన్ని నిటారుగా నిలబెట్టండి"],
            'te_latn': ["Electric pole foundation eroded by adjacent drain soil washed away", "Pole tilted towards drainage ditch imminent collapse danger", "Current stambham base mud washed out reinforce concrete base"]
        },
        {
            'id': 'EL_14', 'type': 'damaged_electric_pole', 'is_emg': True, 'sev': 4,
            'en': ["Lightning strike cracked concrete pole splitting it into two halves", "Thunderbolt shattered middle of electric pole held together only by tension of wires", "Severely fractured concrete pole after storm can snap at any moment"],
            'te': ["పిడుగుపాటుకు విద్యుత్ స్తంభం నిలువునా చీలిపోయింది వైర్ల బరువుపై మాత్రమే నిలబడింది", "తుఫాన్ కు విరిగిన కరెంట్ స్తంభం ఎప్పుడైనా కూలిపోవచ్చు స్థానికులు భయాందోళన", "విద్యుత్ లైన్ ఆఫ్ చేసి పగిలిన స్తంభం స్థానంలో కొత్తది అమర్చండి అత్యవసరం"],
            'te_latn': ["Lightning strike cracked concrete pole into halves held only by wires", "Thunderstorm shattered electric pole snap risk cut power replace fast", "Broken current pole after storm emergency replacement needed"]
        },
        {
            'id': 'EL_15', 'type': 'damaged_electric_pole', 'is_emg': False, 'sev': 3,
            'en': ["Guy-wire support stay wire of electric pole snapped by road construction crew", "Pole stay wire disconnected leaving high tension pole without lateral balance", "Snapped tension stay cable lying across footpath trip hazard replace stay set"],
            'te': ["విద్యుత్ స్తంభం సపోర్ట్ స్టే వైర్ తెగిపోయింది స్తంభం బ్యాలెన్స్ తప్పింది", "స్టే వైర్ ఊడిపోవడంతో స్తంభం రోడ్డు వైపు వంగుతోంది కొత్త స్టే వైర్ బిగించండి", "ఫుట్‌పాత్ పై పడి ఉన్న స్టే వైర్ వల్ల పాదచారులు కింద పడుతున్నారు సరిచేయండి"],
            'te_latn': ["Electric pole guy wire stay wire snapped lateral balance lost", "Pole stay cable disconnected tilting towards road install new stay", "Stay wire snapped on footpath repair stay set immediately"]
        },
        {
            'id': 'EL_16', 'type': 'damaged_electric_pole', 'is_emg': True, 'sev': 4,
            'en': ["Electric pole catching fire at insulator junction with loud crackling sounds", "Fire sparked on top of electric pole near transformers residential area panicking", "Flaming insulator on power mast dropping molten plastic onto parked cars"],
            'te': ["కరెంట్ స్తంభంపై ఇన్సులేటర్ల వద్ద మంటలు చెలరేగి భారీ శబ్దంతో స్పార్క్స్ వస్తున్నాయి", "ట్రాన్స్‌ఫార్మర్ స్తంభంపై నిప్పురవ్వలు రాలుతున్నాయి ప్రజలు భయంతో పరుగులు తీస్తున్నారు", "ఫైర్ ఇంజిన్ మరియు విద్యుత్ శాఖ సిబ్బంది వెంటనే వచ్చి మంటలు ఆపాలి అత్యవసరం"],
            'te_latn': ["Electric pole catching fire at insulator junction loud crackling sounds", "Fire sparked on transformer pole power cut immediately emergency", "Flaming insulator dropping sparks on street rush emergency team"]
        },
        {
            'id': 'EL_17', 'type': 'damaged_electric_pole', 'is_emg': False, 'sev': 2,
            'en': ["Overhead internet and TV cable clusters pulling electric pole down with weight", "Hundreds of illegal black optical cables tangled around municipal light pole", "Excessive telecom cable bunching bending light pole clear unauthorized wires"],
            'te': ["ఇంటర్నెట్ మరియు కేబుల్ వైర్లు విపరీతంగా చుట్టేయడంతో కరెంట్ స్తంభం బరువుకు వంగుతోంది", "అనుమతి లేని కేబుల్ వైర్ల గుత్తులు వీధి లైట్ స్తంభాలపై ప్రమాదకరంగా వేలాడుతున్నాయి", "కరెంట్ స్తంభాలపై ఉన్న ప్రైవేట్ కేబుల్ వైర్లను తొలగించి బరువు తగ్గించండి"],
            'te_latn': ["Internet telecom cables bunching pulling light pole down with heavy weight", "Hundreds of illegal black optical cables tangled around pole clear them", "Private TV cable clusters bending electric pole remove encroachments"]
        },
        # Exposed Electrical Wires (Clusters 18-25)
        {
            'id': 'EL_18', 'type': 'exposed_electrical_wires', 'is_emg': True, 'sev': 4,
            'en': ["Live high voltage overhead electric wire snapped and hanging at head height", "Snapped live current wire dangling over water puddle on street, sparking violently", "Exposed electrical conductor fell onto residential metal gate, electrocution danger"],
            'te': ["లైవ్ కరెంట్ తీగ తెగి రోడ్డుపై తల ఎత్తులో వేలాడుతోంది నిరంతరం స్పార్క్ వస్తోంది", "కరెంట్ వైర్ తెగి వర్షపు నీటి గుంతలో పడింది ముట్టుకుంటే ప్రాణాపాయం పొంచి ఉంది", "విద్యుత్ సరఫరా వెంటనే నిలిపివేసి తెగిన తీగను పునరుద్ధరించండి అత్యవసరం"],
            'te_latn': ["Live current wire snapped and dangling at head height sparking emergency", "Current wire tegipoyi road water puddle lo padindi fatal shock hazard", "Live high voltage electric wire down cut power and fix urgently"]
        },
        {
            'id': 'EL_19', 'type': 'exposed_electrical_wires', 'is_emg': True, 'sev': 4,
            'en': ["Electrical junction box at bottom of pole open with bare terminals exposed", "Open pole junction box with live bare copper wires reachable by small children", "Street light pillar box door broken off, exposed wiring reachable during rain"],
            'te': ["విద్యుత్ స్తంభం కింద ఉన్న జంక్షన్ బాక్స్ మూత లేకుండా తెరిచి ఉంది పిల్లలు తిరుగుతున్నారు", "లైవ్ కరెంట్ వైర్లు బాక్స్ బయటకు వచ్చి ఉన్నాయి వర్షం పడితే షాక్ కొడుతుంది", "జంక్షన్ బాక్స్ కు వెంటనే డోర్ వేసి తాళం వేయండి ప్రమాదం జరగకముందే"],
            'te_latn': ["Electric pole junction box open bare live terminals reachable by kids", "Junction box cover broken live copper wires exposed in rain danger", "Pole control box lock chesi live wires insulate cheyandi emergency"]
        },
        {
            'id': 'EL_20', 'type': 'exposed_electrical_wires', 'is_emg': True, 'sev': 4,
            'en': ["High tension overhead wire sagging dangerously low across colony road", "Overhead electricity wires sagging below 9 feet, trucks constantly brushing wires", "Loose live cables hanging low near double decker bus corridor fatal danger"],
            'te': ["హై టెన్షన్ కరెంట్ వైర్లు రోడ్డుకు చాలా దిగువగా వేలాడుతున్నాయి లారీలకు తగులుతున్నాయి", "కరెంట్ తీగలు కిందకు వాలిపోయాయి ఎవరైనా తాకితే ప్రాణాలు పోతాయి", "వాలిపోయిన తీగలను లాగి సరిచేయాల్సిందిగా విద్యుత్ అధికారులను కోరుతున్నాం"],
            'te_latn': ["High tension overhead wire sagging dangerously low across road trucks hitting", "Overhead electric wire sagging below 9 feet fatal electrocution risk", "Tighten loose overhead power cables urgently before truck accident"]
        },
        {
            'id': 'EL_21', 'type': 'exposed_electrical_wires', 'is_emg': True, 'sev': 4,
            'en': ["Underground electrical power cable dug up and bare joints exposed in mud", "Excavation exposed uninsulated live power cable in waterlogged ditch on street", "Bare live cable joint lying in open puddle near vegetable vendor stalls"],
            'te': ["రోడ్డు తవ్వకాల్లో భూగర్భ విద్యుత్ కేబుల్ పైకి తేలి నగ్నంగా రోడ్డుపై కనిపిస్తోంది", "నీటి గుంతలో లైవ్ విద్యుత్ కేబుల్ పడి ఉంది ముట్టుకుంటే షాక్ కొట్టే ప్రమాదం ఉంది", "కేబుల్ కు ఇన్సులేషన్ వేసి మట్టి కప్పి ప్రమాదం జరగకుండా చూడండి"],
            'te_latn': ["Underground power cable dug up bare joints exposed in water puddle", "Uninsulated live power cable open in mud ditch near vendors shock danger", "Insulate bare live joints and bury power cable properly emergency"]
        },
        {
            'id': 'EL_22', 'type': 'exposed_electrical_wires', 'is_emg': True, 'sev': 4,
            'en': ["Electric transformer fencing missing, exposed 11KV live bushings near school", "Transformer installed on ground without protective cage, live terminals open", "No barrier around high voltage street transformer, grazing cattle getting shocked"],
            'te': ["ట్రాన్స్‌ఫార్మర్ చుట్టూ రక్షణ కంచె ఫెన్సింగ్ లేదు లైవ్ వైర్లు బహిరంగంగా ఉన్నాయి", "పాఠశాల పక్కనే ఉన్న ట్రాన్స్‌ఫార్మర్ కు ఫెన్సింగ్ లేకపోవడంతో విద్యార్థులకు పెనుముప్పు", "ట్రాన్స్‌ఫార్మర్ చుట్టూ వెంటనే ఇనుప రక్షణ కంచె ఏర్పాటు చేయాలి అత్యవసరం"],
            'te_latn': ["Transformer fencing missing exposed 11KV live bushings near school danger", "Ground transformer without protective cage live wires open to public", "Erect security fence around street transformer immediately"]
        },
        {
            'id': 'EL_23', 'type': 'exposed_electrical_wires', 'is_emg': True, 'sev': 4,
            'en': ["Street light pole giving electric shocks when touched during rainy drizzle", "Current leakage into iron pole body, pedestrian received shock while leaning", "Faulty earthing causing entire metal lamp post to become electrified"],
            'te': ["వర్షం పడినప్పుడు కరెంట్ స్తంభం ముట్టుకుంటే విద్యుత్ షాక్ కొడుతోంది లీకేజీ ఉంది", "ఇనుప స్తంభంలోకి కరెంట్ పాస్ అవుతోంది ఒక కుక్క ముట్టుకుని చనిపోయింది", "స్తంభానికి ఎర్తింగ్ సరిచేసి విద్యుత్ లీకేజీని అరికట్టండి అత్యవసరంగా"],
            'te_latn': ["Street light pole giving electric shocks when touched rainy current leak", "Metal lamp post electrified dog died of shock fix earthing immediately", "Current leakage in street light pole ground fault repair fast"]
        },
        {
            'id': 'EL_24', 'type': 'exposed_electrical_wires', 'is_emg': True, 'sev': 4,
            'en': ["Tree branch touching overhead high tension line causing continuous fireworks sparks", "Foliage rubbing against live phase wire emitting continuous flame flashes at night", "Dry tree branches tangled in live conductors creating severe fire hazard"],
            'te': ["చెట్ల కొమ్మలు హైటెన్షన్ కరెంట్ తీగలను తాకుతూ నిరంతరం నిప్పురవ్వలు కురుస్తున్నాయి", "గాలి వీచినప్పుడల్లా తీగలు రాపిడికి గురై మంటలు వస్తున్నాయి కొమ్మలు నరకండి", "విద్యుత్ తీగలపై పడిన చెట్టు కొమ్మలను తక్షణమే తొలగించి ప్రమాదాన్ని ఆపండి"],
            'te_latn': ["Tree branches touching high tension line continuous fireworks sparks", "Foliage rubbing against live phase wire fire flashes at night cut branches", "Trim tree boughs touching overhead power cables fire hazard"]
        },
        {
            'id': 'EL_25', 'type': 'exposed_electrical_wires', 'is_emg': True, 'sev': 4,
            'en': ["Snapped consumer service wire lying submerged in colony drainage gutter", "Phase wire from pole fell into roadside water channel, water electrifying", "Broken wire conducting current into flowing gutter water, disconnect service line"],
            'te': ["ఇంటికి వెళ్లే సర్వీస్ కరెంట్ వైర్ తెగి మురుగు కాలువ నీటిలో పడిపోయింది", "కాలువ నీటిలోకి కరెంట్ పాస్ అయ్యే ప్రమాదం ఉంది వెంటనే విద్యుత్ సరఫరా ఆపండి", "తెగిపడిన సర్వీస్ వైర్ ను సరిచేసి ప్రమాదం జరగకుండా చూడండి"],
            'te_latn': ["Snapped consumer service wire lying in colony drainage water electrifying", "Broken live wire conducting current into roadside gutter disconnect power", "Service wire fell into open drain electric shock danger fix fast"]
        }
    ],

    # =========================================================================
    # DEPARTMENT 5: SANITATION & SOLID WASTE (others) - 25 Clusters
    # =========================================================================
    'others': [
        # Garbage Accumulation (Clusters 1-6)
        {
            'id': 'SN_01', 'type': 'garbage_accumulation', 'is_emg': False, 'sev': 2,
            'en': ["Massive pile of rotting municipal garbage dumped on residential road corner", "Rotting trash heap scattered by stray pigs and dogs emitting unbearable stench", "Garbage accumulated for over ten days turning colony corner into illegal dumping yard"],
            'te': ["రోడ్డు మూలలో కొండలా చెత్త కుప్పలు పేరుకుపోయాయి వీధి కుక్కలు చెల్లాచెదురు చేస్తున్నాయి", "కుళ్ళిన ఆహార వ్యర్థాలతో దుర్వాసన భరించలేకపోతున్నాం ఈగలు ముసురుతున్నాయి", "పారిశుద్ధ్య సిబ్బందిని పంపించి జేసీబీతో చెత్త కుప్పను ఎత్తించి బ్లీచింగ్ చల్లించండి"],
            'te_latn': ["Road corner lo huge garbage pile accumulated dogs scattering foul smell", "Rotting waste heap bad smell mosquito menace send sanitation squad", "Chetha kuppalu road meeda dump chesaru clear chesi bleaching powder challandi"]
        },
        {
            'id': 'SN_02', 'type': 'garbage_accumulation', 'is_emg': False, 'sev': 2,
            'en': ["Municipal community trash bin overflowed, waste spilling across road", "Broken green municipal dumpster overflowing, traffic forced onto sidewalk", "Public dumper bin overflowing with domestic refuse blocking street drain"],
            'te': ["మునిసిపల్ చెత్త డబ్బా నిండిపోయి చెత్త అంతా రోడ్డుపై పడిపోయింది వాహనాలు వెళ్లలేకపోతున్నాయి", "చెత్త కుండీ పగిలి వ్యర్థాలు బయటకు పారుతున్నాయి కొత్త చెత్త డబ్బా ఏర్పాటు చేయండి", "చెత్త డబ్బాను రోజువారీగా ఖాళీ చేయించాల్సిందిగా శానిటేషన్ విభాగాన్ని కోరుతున్నాం"],
            'te_latn': ["Municipal dustbin overflowing waste spilled on road vehicles unable to pass", "Broken dumper bin garbage scattering on street replace new bin", "Municipal garbage bin empty cheyandi daily basis"]
        },
        {
            'id': 'SN_03', 'type': 'garbage_accumulation', 'is_emg': False, 'sev': 2,
            'en': ["Vacant private residential plot converted into illegal garbage dumping ground", "Neighbors throwing rotten kitchen waste into empty plot full of wild bushes", "Unfenced vacant plot piled five feet high with domestic refuse and plastic bags"],
            'te': ["ఖాళీ స్థలంలో చుట్టుపక్కల వారు చెత్త వేసి డంపింగ్ యార్డ్ లా మార్చేశారు దుర్గంధం", "ఖాళీ ప్లాట్ లో చెత్త కుప్పలు పెరిగి పాములు తేళ్లు వస్తున్నాయి శుభ్రం చేయించండి", "స్థలం యజమానికి నోటీసులు ఇచ్చి చెత్తను జేసీబీతో క్లియర్ చేయించాలి"],
            'te_latn': ["Vacant plot converted into illegal garbage dumping ground foul smell", "Empty plot lo trash dump chesaru snakes and mosquitoes coming clean it", "Vacant plot garbage clearance JCB machine needed issue notices"]
        },
        {
            'id': 'SN_04', 'type': 'garbage_accumulation', 'is_emg': False, 'sev': 2,
            'en': ["Fish and poultry market chicken feathers and rotten meat dumped openly on roadside", "Raw fish market waste decomposing under sun causing horrific nauseating odor", "Poultry shop owners dumping animal entrails directly on pavement attract vultures"],
            'te': ["చేపల మరియు చికెన్ మార్కెట్ వ్యర్థాలను రోడ్డు పక్కనే పారబోయడంతో భరించలేని కంపు వస్తోంది", "కుళ్ళిన మాంసం వ్యర్థాల వల్ల ఈగలు వీధి కుక్కలు ముసురుతున్నాయి అంటువ్యాధుల భయం", "మార్కెట్ వ్యర్థాలను వెంటనే తొలగించి క్రిమిసంహారక మందులు పిచికారీ చేయించండి"],
            'te_latn': ["Fish and chicken market rotten waste dumped openly on road terrible smell", "Meat market entrails decomposing under sun clean immediately", "Poultry market waste clearance and disinfection urgently required"]
        },
        {
            'id': 'SN_05', 'type': 'garbage_accumulation', 'is_emg': False, 'sev': 2,
            'en': ["Commercial wedding hall dumped hundreds of single-use plates and food on road", "Function hall discarded catering food waste on street corner causing stray dog frenzy", "Leftover feast food and plastic bottles dumped along colony street clear debris"],
            'te': ["ఫంక్షన్ హాల్ వారు మిగిలిపోయిన భోజనం మరియు ప్లాస్టిక్ ప్లేట్లను రోడ్డుపై పారబోశారు", "కల్యాణ మండపం వ్యర్థాల వల్ల కుక్కలు గుంపులుగా చేరి వీధిలో ప్రజలపై దాడి చేస్తున్నాయి", "ఫంక్షన్ హాల్ యాజమాన్యానికి జరిమానా విధించి వ్యర్థాలను వెంటనే ఎత్తించండి"],
            'te_latn': ["Function hall catering food waste and plates dumped on road corner", "Wedding hall waste attracts stray dogs pack clear street immediately", "Catering leftover food waste dumped on colony lane fine management"]
        },
        {
            'id': 'SN_06', 'type': 'garbage_accumulation', 'is_emg': False, 'sev': 2,
            'en': ["Single-use plastic carry bags scattered across municipal park and lake bed", "Littering of plastic covers and liquor bottles in children play area", "Plastic waste clogging park walking track municipal cleanup drive required"],
            'te': ["మునిసిపల్ పార్కులో ప్లాస్టిక్ కవర్లు మరియు మద్యం సీసాలు చెల్లాచెదురుగా పడి ఉన్నాయి", "పిల్లలు ఆడుకునే ప్రదేశంలో ప్లాస్టిక్ వ్యర్థాలు పేరుకుపోయాయి శుభ్రం చేయించండి", "పార్క్ పరిసరాలను రోజూ ఊడ్చి పరిశుభ్రంగా ఉంచాలని కోరుతున్నాం"],
            'te_latn': ["Single use plastic bags scattered in municipal park and lake walking track", "Children play park full of plastic litter and bottles clean grounds", "Municipal park cleanup required remove plastic garbage"]
        },
        # Garbage Collection Failure (Clusters 7-11)
        {
            'id': 'SN_07', 'type': 'garbage_collection_failure', 'is_emg': False, 'sev': 2,
            'en': ["Door-to-door municipal garbage collection vehicle not visited for eight days", "Sanitation auto has skipped our street completely for over one week", "Household waste rotting in residential compounds because collection cart absent"],
            'te': ["ఇంటింటికీ చెత్త సేకరించే ఆటో గత ఎనిమిది రోజులుగా మా వీధికి రావడం లేదు", "శానిటేషన్ సిబ్బంది చెత్త సేకరణ మానేశారు ఇళ్లలో చెత్త నిల్వ ఉండి కంపుకొడుతోంది", "క్రమం తప్పకుండా ప్రతిరోజూ చెత్త సేకరించేలా శానిటరీ ఇన్‌స్పెక్టర్ చర్యలు తీసుకోవాలి"],
            'te_latn': ["Door to door garbage vehicle past 8 days nundi ravadam ledu waste pending", "Sanitation auto vehicle skipped our colony collection completely stopped", "Daily waste collection regularize cheyandi send municipal van"]
        },
        {
            'id': 'SN_08', 'type': 'garbage_collection_failure', 'is_emg': False, 'sev': 2,
            'en': ["Sanitation auto workers demanding illegal monthly bribes to collect household trash", "Collection staff refusing to take garbage unless private money paid to them", "Corrupt sanitation workers skipping households that refuse unofficial tips"],
            'te': ["చెత్త సేకరణ సిబ్బంది ఇళ్ల వద్ద డబ్బులు లంచం అడుగుతున్నారు ఇవ్వకపోతే చెత్త తీసుకోం అంటున్నారు", "శానిటేషన్ కార్మికులు నిర్లక్ష్యంగా వ్యవహరిస్తూ డబ్బుల కోసం వేధిస్తున్నారు", "లంచాలు డిమాండ్ చేస్తున్న సిబ్బందిపై చర్యలు తీసుకుని చెత్త సక్రమంగా ఎత్తించండి"],
            'te_latn': ["Sanitation workers demanding illegal monthly tips to collect garbage", "Workers refusing waste collection without private money take action", "Corrupt sanitation staff skipping houses inspect and regularize"]
        },
        {
            'id': 'SN_09', 'type': 'garbage_collection_failure', 'is_emg': False, 'sev': 2,
            'en': ["Door to door electric garbage tipper auto broken down and not replaced", "Municipal sanitation vehicle out of service for weeks, no alternative van deployed", "Breakdown of battery waste auto halting garbage pickup in three colony wards"],
            'te': ["చెత్త సేకరించే ఎలక్ట్రిక్ ఆటో పాడైపోయింది ప్రత్యామ్నాయ వాహనం పంపలేదు", "ఆటో రిపేర్ లో ఉండటంతో వారం రోజులుగా చెత్త ఎత్తడం లేదు కొత్త వాహనం పంపండి", "శానిటేషన్ వాహనాన్ని వెంటనే బాగుచేయించి చెత్త సేకరణ పునరుద్ధరించండి"],
            'te_latn': ["Garbage collection auto broken down no alternate vehicle deployed", "Sanitation tipper vehicle out of order for 1 week waste accumulated", "Send replacement waste auto vehicle to our ward immediately"]
        },
        {
            'id': 'SN_10', 'type': 'garbage_collection_failure', 'is_emg': False, 'sev': 2,
            'en': ["Sanitation workers refusing to collect segregated wet waste properly", "Collection staff mixing separated dry and wet waste back together in truck", "Green waste bins ignored by sanitation workers leaving garden clippings on curb"],
            'te': ["మేము తడి పొడి చెత్త వేరు చేసినా సిబ్బంది తీసుకోకుండా అన్నీ కలిపేస్తున్నారు", "చెట్ల ఆకులు కొమ్మల వ్యర్థాలను ఎత్తడానికి శానిటేషన్ సిబ్బంది నిరాకరిస్తున్నారు", "నియమాల ప్రకారం తడి పొడి చెత్తను వేర్వేరుగా సేకరించేలా సిబ్బందికి ఆదేశాలు ఇవ్వండి"],
            'te_latn': ["Sanitation staff refusing to collect segregated waste properly mixing all", "Workers refusing green garden clippings on curb regularize collection", "Segregated waste collection guidelines follow cheyandi"]
        },
        {
            'id': 'SN_11', 'type': 'garbage_collection_failure', 'is_emg': False, 'sev': 2,
            'en': ["Sanitation rickshaw drives by at irregular random hours without blowing whistle", "Garbage collection van doesn't ring bell or blow horn, passes away silently", "Residents unable to hand over garbage because collector timings are unpredictable"],
            'te': ["చెత్త సేకరణ ఆటో విజిల్ లేదా హారన్ వేయకుండా వేగంగా వెళ్లిపోతోంది ప్రజలు చెత్త వేయలేకపోతున్నారు", "నిర్దిష్ట వేళల్లో కాకుండా ఎప్పుడు పడితే అప్పుడు రావడం వల్ల చెత్త మిగిలిపోతోంది", "ఉదయం 7 నుండి 9 గంటల మధ్యలో హారన్ వేస్తూ చెత్త సేకరించేలా చూడండి"],
            'te_latn': ["Sanitation rickshaw passes silently without blowing horn missed waste", "Garbage van timings irregular comes at random hours please regularize", "Sound whistle properly while collecting door to door waste"]
        },
        # Dead Animal Removal (Clusters 12-16)
        {
            'id': 'SN_12', 'type': 'dead_animal_removal', 'is_emg': True, 'sev': 3,
            'en': ["Dead stray dog carcass rotting on roadside near market, unbearable flies and stench", "Decomposing animal body lying on sidewalk emitting nauseating disease hazard", "Dead street animal rotting in heat near residential gates remove immediately"],
            'te': ["రోడ్డు పక్కన చనిపోయిన వీధి కుక్క కళేబరం కుళ్లిపోయి విపరీతమైన దుర్వాసన వస్తోంది", "జంతు కళేబరం కుళ్ళిపోయి ఈగలు ముసురుతున్నాయి అంటువ్యాధులు ప్రబలే ప్రమాదం ఉంది", "శానిటేషన్ ఎమర్జెన్సీ టీమ్ వెంటనే వచ్చి కుక్క కళేబరాన్ని తరలించి సున్నం వేయాలి"],
            'te_latn': ["Road side dead stray dog rotting unbearable smell and flies health risk", "Decomposing animal body on street remove immediately emergency sanitation", "Dead animal carcass lying near gate sanitation team clear fast"]
        },
        {
            'id': 'SN_13', 'type': 'dead_animal_removal', 'is_emg': True, 'sev': 3,
            'en': ["Dead calf carcass dumped inside open drainage canal choking water", "Decaying animal floating in stormwater canal creating horrific neighborhood odor", "Animal remains stuck inside culvert grate remove before contamination spreads"],
            'te': ["డ్రైనేజీ కాలువలో చనిపోయిన జంతువు పడి కుళ్లిపోతోంది నీరు నిలిచిపోయింది", "కాలువలో తేలుతున్న జంతు కళేబరం వల్ల పరిసర ప్రాంతాలన్నీ దుర్గంధంతో నిండిపోయాయి", "డ్రైనేజీ నుంచి జంతు కళేబరాన్ని బయటకు తీసి లోతైన ప్రదేశంలో పూడ్చిపెట్టాలి"],
            'te_latn': ["Drainage canal lo dead calf carcass floating foul stench remove immediately", "Decaying animal stuck in drainage grate clean canal before disease spreads", "Drainage nundi dead animal carcass remove cheyandi"]
        },
        {
            'id': 'SN_14', 'type': 'dead_animal_removal', 'is_emg': True, 'sev': 3,
            'en': ["Runover cat carcass flattened on fast lane of flyover causing bike skids", "Dead stray cat crushed on highway service road emitting terrible smell", "Hit and run dead animal carcass on municipal bypass clear immediately"],
            'te': ["ఫ్లైఓవర్ పై వాహనం ఢీకొని పిల్లి చనిపోయింది రక్తపు మరకలతో రోడ్డుపై ఉంది", "బైపాస్ రోడ్డుపై వాహనాలు తొక్కిన జంతు కళేబరం కుళ్లిపోయి దుర్వాసన వస్తోంది", "శానిటరీ వర్కర్లు వచ్చి రోడ్డుపై ఉన్న కళేబరాన్ని ఎత్తించి బ్లీచింగ్ చల్లాలి"],
            'te_latn': ["Runover cat carcass on flyover road emitting bad smell remove fast", "Crushed dead animal on highway service road clear and bleach", "Hit and run dead animal on street municipal squad clear fast"]
        },
        {
            'id': 'SN_15', 'type': 'dead_animal_removal', 'is_emg': True, 'sev': 3,
            'en': ["Dead cow carcass lying near railway level crossing attracting dogs and vultures", "Stray cow died on roadside railway verge, decomposition hazard for commuters", "Cattle carcass rotting near rail track remove with municipal loader"],
            'te': ["రైల్వే గేటు సమీపంలో ఆవు చనిపోయి రెండు రోజులైంది కళేబరం కుళ్లిపోతోంది", "చనిపోయిన పశువు కళేబరం వల్ల పరిసరాలు అపరిశుభ్రంగా మారాయి ఈగలు ముసురుతున్నాయి", "మున్సిపల్ జేసీబీ తెప్పించి పశువు కళేబరాన్ని త్వరగా ఖననం చేయించండి"],
            'te_latn': ["Dead cow carcass near railway level crossing rotting stench remove loader", "Stray cattle dead on road vultures gathering dispose of carcass immediately", "Dead animal cow carcass removal needed urgently"]
        },
        {
            'id': 'SN_16', 'type': 'dead_animal_removal', 'is_emg': True, 'sev': 3,
            'en': ["Dead pig carcass rotting near primary school boundary wall", "Decaying swine carcass emitting pestilential odor outside school classroom", "Decomposing pig on colony street health danger for children remove fast"],
            'te': ["పాఠశాల ప్రహరీ గోడ పక్కన చనిపోయిన పంది కళేబరం కుళ్లి విపరీతమైన కంపు వస్తోంది", "దుర్వాసన వల్ల విద్యార్థులు తరగతి గదుల్లో కూర్చోలేకపోతున్నారు అస్వస్థతకు గురవుతున్నారు", "శానిటేషన్ సిబ్బంది వెంటనే వచ్చి పంది కళేబరాన్ని తొలగించి క్రిమిసంహారక మందు చల్లాలి"],
            'te_latn': ["Dead pig carcass rotting near school wall foul odor remove immediately", "Decaying swine carcass health hazard for school kids clear fast", "Dead pig on street municipal squad remove and spray bleaching"]
        },
        # Public Sanitation (Clusters 17-21)
        {
            'id': 'SN_17', 'type': 'public_sanitation_issue', 'is_emg': False, 'sev': 2,
            'en': ["Municipal public toilet near bus station completely filthy and unmaintained", "Public urinal overflowing with stagnant urine, water supply broken and foul stench", "Women passengers unable to use dilapidated and uncleaned municipal restroom"],
            'te': ["బస్టాండ్ వద్ద ఉన్న మునిసిపల్ పబ్లిక్ టాయిలెట్ అత్యంత అపరిశుభ్రంగా ఉంది నీటి సరఫరా లేదు", "పబ్లిక్ మూత్రశాలలు నిర్వహణ లేక కంపుకొడుతున్నాయి ప్రయాణికులు తీవ్ర ఇబ్బందులు పడుతున్నారు", "టాయిలెట్లను బ్లీచింగ్ వేసి శుభ్రం చేయించి వాటర్ ట్యాప్ రిపేర్ చేయించండి"],
            'te_latn': ["Bus stand public toilet completely filthy and foul smell no water supply", "Public urinals broken maintenance zero passengers suffering clean immediately", "Municipal public toilet clean chesi running water provide cheyandi"]
        },
        {
            'id': 'SN_18', 'type': 'public_sanitation_issue', 'is_emg': False, 'sev': 2,
            'en': ["Massive mosquito infestation in ward, municipal fogging and spraying required", "Dengue cases reported in colony, no bleaching powder sprinkled for months", "Stagnant pools of water breeding lakhs of mosquitoes, urgent vector control needed"],
            'te': ["కాలనీలో దోమలు విపరీతంగా పెరిగిపోయాయి డెంగ్యూ మలేరియా జ్వరాలు వస్తున్నాయి", "మునిసిపాలిటీ వారు బ్లీచింగ్ పౌడర్ చల్లి ఫాగింగ్ స్ప్రే చేయించాలని కోరుతున్నాం", "సీజనల్ వ్యాధులు ప్రబలకుండా దోమల నివారణ మందులు వెంటనే పిచికారీ చేయించండి"],
            'te_latn': ["Colony lo mosquito menace very high dengue cases reported municipal fogging needed", "Bleaching powder spraying not done since months vector control required", "Mosquito fogging vehicle send cheyandi colony motham"]
        },
        {
            'id': 'SN_19', 'type': 'public_sanitation_issue', 'is_emg': False, 'sev': 2,
            'en': ["Roadside sweeping sweepers piling dust and leaves without lifting for days", "Sanitation sweepers sweeping road dirt into open drains instead of lifting", "Piles of swept street silt left on kerb blowing back onto traffic"],
            'te': ["వీధులు ఊడ్చిన తర్వాత మట్టిని కుప్పలుగా రోడ్డుపైనే వదిలేసి వెళ్తున్నారు", "శానిటేషన్ సిబ్బంది ఊడ్చిన చెత్తను మురుగు కాలువల్లోకి నెట్టేస్తున్నారు ఆపండి", "ఊడ్చిన మట్టి చెత్తను వెంటనే ట్రాలీలో ఎత్తించి తరలించేలా చూడండి"],
            'te_latn': ["Street sweepers sweeping dirt into drains instead of lifting in trolley", "Piles of swept road dust left on kerb blowing back clean dust piles", "Sanitation sweepers road sweeping waste lifting regularize"]
        },
        {
            'id': 'SN_20', 'type': 'public_sanitation_issue', 'is_emg': False, 'sev': 2,
            'en': ["Community open defecation along railway boundary due to locked public toilets", "Public e-toilet locked and abandoned, slum residents forced to defecate openly", "Unlock and restore water connection to municipal community toilet block"],
            'te': ["పబ్లిక్ టాయిలెట్ కు తాళం వేసి ఉంచడంతో ప్రజలు రోడ్డు పక్కన బహిరంగ మలవిసర్జన చేస్తున్నారు", "మునిసిపల్ కమ్యూనిటీ టాయిలెట్ ను వెంటనే తెరిపించి నీటి సరఫరా పునరుద్ధరించండి", "పరిసరాల పరిశుభ్రత కాపాడటానికి పబ్లిక్ టాయిలెట్లను రోజూ మెయింటైన్ చేయాలి"],
            'te_latn': ["Community public toilet locked open defecation happening along tracks", "Unlock public toilet block restore water supply sanitation hazard", "Municipal community toilet maintenance and reopening urgently required"]
        },
        {
            'id': 'SN_21', 'type': 'public_sanitation_issue', 'is_emg': False, 'sev': 2,
            'en': ["Chemical bleaching powder and antilarval spray not applied after recent rain", "Municipal health workers not sprinkled lime and bleaching on stagnant puddles", "Vector borne disease risk: request comprehensive ward sanitation and bleaching spray"],
            'te': ["వర్షాలు పడినా కాలనీ రోడ్లపై బ్లీచింగ్ పౌడర్ చల్లలేదు దోమల నివారణ చేపట్టలేదు", "మురికి నీటి నిల్వల వద్ద యాంటీ లార్వా మందులు స్ప్రే చేయాల్సిందిగా కోరుతున్నాం", "ఆరోగ్య విభాగం సిబ్బంది వచ్చి వీధుల్లో సున్నం మరియు బ్లీచింగ్ చల్లాలి"],
            'te_latn': ["Bleaching powder and antilarval chemical spray not applied after rain", "Stagnant puddles breeding mosquitoes spray anti larva chemical fast", "Ward health workers bleaching powder sprinkling drive needed"]
        },
        # Other Civic Issues (Clusters 22-25)
        {
            'id': 'SN_22', 'type': 'other_civic_issue', 'is_emg': False, 'sev': 2,
            'en': ["Pack of aggressive stray dogs chasing two-wheelers and biting pedestrians", "Stray dog menace near primary school gate, children getting attacked", "Rabid dog roaming residential colony, dog catching vehicle squad needed"],
            'te': ["వీధి కుక్కలు గుంపులుగా చేరి బైకర్లను వెంబడిస్తున్నాయి పాదచారులను కరుస్తున్నాయి", "పాఠశాల సమీపంలో కుక్కల బెడద ఎక్కువైంది పిల్లలు బయటకు రావడానికి భయపడుతున్నారు", "మున్సిపల్ డాగ్ క్యాచింగ్ వ్యాన్ పంపించి కుక్కలను పట్టుకోవాల్సిందిగా విజ్ఞప్తి"],
            'te_latn': ["Stray dogs pack chasing bikes and biting pedestrians dog catching van needed", "Street dog menace near school kids getting attacked catch dogs urgently", "Colony lo dogs terror ekkuva ayindi municipal dog squad pampandi"]
        },
        {
            'id': 'SN_23', 'type': 'other_civic_issue', 'is_emg': False, 'sev': 2,
            'en': ["Commercial open burning of plastic waste producing suffocating toxic black smoke", "Vacant plot being used to burn chemical trash, residents having breathing issues", "Illegal bonfire of plastic bags and dry leaves in residential neighborhood"],
            'te': ["ఖాళీ స్థలంలో ప్లాస్టిక్ వ్యర్థాలను తగులబెడుతున్నారు వెలువడే విషపూరిత పొగతో ఊపిరాడటం లేదు", "రాత్రిళ్లు చెత్తను కాల్చడం వల్ల కాలనీ అంతా దట్టమైన పొగ కమ్ముకుంటోంది ఆపండి", "చెత్త కాల్చే వారిపై జరిమానా విధించి కాలుష్యాన్ని అరికట్టండి"],
            'te_latn': ["Open plot lo plastic waste burning toxic black smoke suffocating residents", "Illegal trash burning causing breathing problems stop it and fine them", "Plastic waste burning night time air pollution stop immediately"]
        },
        {
            'id': 'SN_24', 'type': 'other_civic_issue', 'is_emg': False, 'sev': 2,
            'en': ["Stray cattle roaming on busy highway junction causing dangerous traffic jams", "Unattended cows and bulls sitting in middle of road at night causing fatal crashes", "Municipal cattle impound squad needed to clear stray cows from arterial road"],
            'te': ["ప్రధాన రహదారిపై ఆవులు మరియు ఎద్దులు అడ్డంగా కూర్చుని ట్రాఫిక్ కు అంతరాయం కలిగిస్తున్నాయి", "రాత్రి సమయంలో రోడ్డు మధ్యలో పశువులు కనిపించక వాహనాలు ఢీకొంటున్నాయి", "పశువుల యజమానులకు జరిమానా వేసి పశువులను మునిసిపల్ కట్టడి దొడ్డికి తరలించండి"],
            'te_latn': ["Stray cattle roaming on busy highway junction causing fatal accidents", "Cows and bulls sitting in road middle at night impound cattle", "Municipal cattle catching squad clear stray cows from road"]
        },
        {
            'id': 'SN_25', 'type': 'other_civic_issue', 'is_emg': False, 'sev': 2,
            'en': ["Public park children playground swing and slide broken with sharp edges", "Municipal park equipment rusted and broken, children getting lacerations", "Children park swings broken and safety fence fallen repair recreation ground"],
            'te': ["మున్సిపల్ పార్కులో పిల్లల ఉయ్యాలలు మరియు జారుడు బల్లలు విరిగిపోయి ప్రమాదకరంగా ఉన్నాయి", "తుప్పు పట్టిన ఇనుప ఆట వస్తువుల వల్ల పిల్లల చేతులు తెగుతున్నాయి రిపేర్ చేయించండి", "పార్క్ లోని పరికరాలను బాగుచేసి పిల్లలకు సురక్షితమైన వాతావరణం కల్పించండి"],
            'te_latn': ["Public park playground swing and slide broken sharp iron edges danger", "Children getting hurt from broken park equipment repair playground", "Park recreation facilities broken replace swings and repair fence"]
        }
    ]
}

def build_dataset():
    records = []
    rec_counter = 1
    
    # Process all departments and clusters
    for dept, clusters in CLUSTERS_DATA.items():
        print(f"Compiling Department: {dept} ({len(clusters)} clusters)...")
        for cl in clusters:
            cid = cl['id']
            ctype = cl['type']
            sev = cl['sev']
            is_emg = cl['is_emg']
            
            # Select random municipal context
            ulb = random.choice(AP_ULBS)
            ward_num = random.randint(1, 35)
            ward_str = f"Ward {ward_num}"
            
            # English variants (3 basic + 2 contextualized)
            for txt in cl['en']:
                records.append({
                    'complaint_id': f"NXC_{rec_counter:05d}",
                    'cluster_id': cid,
                    'complaint_text': txt.strip(),
                    'language_style': 'en',
                    'department': dept,
                    'complaint_type': ctype,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_counter += 1
                
                # Contextualized variant with municipality landmark
                loc_text = f"{txt.strip()} (near {ulb['code']} {ward_str})"
                records.append({
                    'complaint_id': f"NXC_{rec_counter:05d}",
                    'cluster_id': cid,
                    'complaint_text': loc_text,
                    'language_style': 'en',
                    'department': dept,
                    'complaint_type': ctype,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_counter += 1
                
            # Native Telugu variants (3 basic + 2 contextualized)
            for txt in cl['te']:
                norm_te = unicodedata.normalize('NFC', txt.strip())
                records.append({
                    'complaint_id': f"NXC_{rec_counter:05d}",
                    'cluster_id': cid,
                    'complaint_text': norm_te,
                    'language_style': 'te',
                    'department': dept,
                    'complaint_type': ctype,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_counter += 1
                
                loc_te = f"{norm_te} ({ulb['name']} పరిధిలోని వార్డు నెం.{ward_num})"
                records.append({
                    'complaint_id': f"NXC_{rec_counter:05d}",
                    'cluster_id': cid,
                    'complaint_text': loc_te,
                    'language_style': 'te',
                    'department': dept,
                    'complaint_type': ctype,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_counter += 1
                
            # Romanized Telugu variants (3 basic + 2 contextualized)
            for txt in cl['te_latn']:
                records.append({
                    'complaint_id': f"NXC_{rec_counter:05d}",
                    'cluster_id': cid,
                    'complaint_text': txt.strip(),
                    'language_style': 'te_latn',
                    'department': dept,
                    'complaint_type': ctype,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_counter += 1
                
                loc_latn = f"{txt.strip()} ({ulb['code']} area ward {ward_num})"
                records.append({
                    'complaint_id': f"NXC_{rec_counter:05d}",
                    'cluster_id': cid,
                    'complaint_text': loc_latn,
                    'language_style': 'te_latn',
                    'department': dept,
                    'complaint_type': ctype,
                    'severity_level': sev,
                    'is_emergency': int(is_emg),
                    'municipality': ulb['name'],
                    'ward': ward_str,
                    'district': ulb['district']
                })
                rec_counter += 1

    df = pd.DataFrame(records)
    print(f"\nTotal raw generated records: {len(df)} across {df['cluster_id'].nunique()} clusters.")
    
    # Add authentic Compound / Boundary Dilemma Cases to specifically test cross-departmental robustness
    COMPOUND_CASES = [
        # Sewage overflowing eroding road asphalt (True Dept: road)
        ("Sewage water overflowing from drain has created massive potholes and eroded asphalt on the colony road", "en", "road", "potholes", 3, 0),
        ("తారు రోడ్డుపై మురుగు నీరు నిరంతరం పారడం వల్ల పెద్ద గుంతలు పడి రోడ్డు ధ్వంసమైంది ప్యాచ్ వర్క్ చేయాలి", "te", "road", "potholes", 3, 0),
        ("Drainage water road meeda flow avvadam valla road motham damage ayi guntalu paddayi repair required", "te_latn", "road", "potholes", 3, 0),
        # Garbage blocking stormwater canal (True Dept: drainage)
        ("Rotting municipal garbage and plastic covers dumped into open stormwater canal causing drainage overflow", "en", "drainage", "blocked_drainage", 2, 0),
        ("చెత్త కుప్పలు డ్రైనేజీ కాలువలో వేయడం వల్ల కాలువ పూడిపోయి మురుగు నీరు ముందుకు పోవడం లేదు", "te", "drainage", "blocked_drainage", 2, 0),
        ("Chetha kuppalu open drain lo dump cheyadam valla drainage canal block ayi overflow avtundi", "te_latn", "drainage", "blocked_drainage", 2, 0),
        # Drinking water pipe burst undermining street road (True Dept: water_supply)
        ("Drinking water distribution pipeline leaking right next to road drainage canal risking contamination", "en", "water_supply", "pipeline_leakage", 3, 0),
        ("మంచినీటి పైపు పగిలి రోడ్డు మీద డ్రైనేజీ పక్కగా ప్రవహిస్తోంది తాగునీరు కలుషితం కాకముందే ఆపండి", "te", "water_supply", "pipeline_leakage", 3, 0),
        ("Drinking water pipe burst ayi road kindha soil wash out ayi sinkhole padindi fix pipe urgently", "te_latn", "water_supply", "pipeline_leakage", 3, 0),
        # Fallen electric pole blocking road traffic (True Dept: street_lights)
        ("Electric street light pole collapsed across colony road blocking cars and snapping wires", "en", "street_lights", "damaged_electric_pole", 4, 1),
        ("విద్యుత్ స్తంభం విరిగి రోడ్డుపై పడిపోయింది వైర్లు డ్రైనేజీలో పడ్డాయి అత్యవసర సహాయం", "te", "street_lights", "damaged_electric_pole", 4, 1),
        ("Current pole nundi live wire tegipoyi colony road water puddle lo padindi shock danger", "te_latn", "street_lights", "exposed_electrical_wires", 4, 1),
        # Dead animal carcass rotting in open drain (True Dept: others)
        ("Dead street dog carcass dumped into open municipal drainage canal emitting unbearable decaying stench", "en", "others", "dead_animal_removal", 3, 1),
        ("మురుగు కాలువలో చనిపోయిన పంది కళేబరం పడి కుళ్లిపోతోంది దుర్వాసనతో ప్రజలు రోడ్డుపై వెళ్లలేకపోతున్నారు", "te", "others", "dead_animal_removal", 3, 1),
        ("Dead animal carcass road drain lo padindi flies and bad smell unbearable municipal squad clear fast", "te_latn", "others", "dead_animal_removal", 3, 1)
    ]
    
    # Put compound cases into their own dedicated boundary clusters
    for b_idx, (b_txt, b_lang, b_dept, b_ctype, b_sev, b_emg) in enumerate(COMPOUND_CASES):
        cid = f"BND_{b_dept[:2].upper()}_{b_idx:02d}"
        ulb = random.choice(AP_ULBS)
        records.append({
            'complaint_id': f"NXC_{rec_counter:05d}",
            'cluster_id': cid,
            'complaint_text': b_txt,
            'language_style': b_lang,
            'department': b_dept,
            'complaint_type': b_ctype,
            'severity_level': b_sev,
            'is_emergency': b_emg,
            'municipality': ulb['name'],
            'ward': 'Ward 10',
            'district': ulb['district']
        })
        rec_counter += 1
        
        # Add a short informal version
        short_txt = " ".join(b_txt.split()[:8])
        records.append({
            'complaint_id': f"NXC_{rec_counter:05d}",
            'cluster_id': cid,
            'complaint_text': short_txt,
            'language_style': b_lang,
            'department': b_dept,
            'complaint_type': b_ctype,
            'severity_level': b_sev,
            'is_emergency': b_emg,
            'municipality': ulb['name'],
            'ward': 'Ward 10',
            'district': ulb['district']
        })
        rec_counter += 1

    df = pd.DataFrame(records)
    print(f"Total records with boundary clusters: {len(df)} across {df['cluster_id'].nunique()} clusters.")

    # -------------------------------------------------------------------------
    # STRICT STRATIFIED GROUP PARTITIONING (70% Train, 15% Validation, 15% Test)
    # Guaranteed 0% overlap of cluster_id or underlying incident across splits!
    # -------------------------------------------------------------------------
    cluster_df = df[['cluster_id', 'department']].drop_duplicates().sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    
    train_clusters = []
    val_clusters = []
    test_clusters = []
    
    for dept in df['department'].unique():
        dept_cl = cluster_df[cluster_df['department'] == dept]['cluster_id'].tolist()
        n = len(dept_cl)
        n_train = int(round(n * 0.70))
        n_val = int(round(n * 0.15))
        n_test = n - n_train - n_val
        if n_val == 0 and n >= 3: n_val = 1
        if n_test == 0 and n >= 3: n_test = 1; n_train -= 1
        
        train_clusters.extend(dept_cl[:n_train])
        val_clusters.extend(dept_cl[n_train:n_train + n_val])
        test_clusters.extend(dept_cl[n_train + n_val:])
        
    print(f"\nCluster allocation: {len(train_clusters)} Train, {len(val_clusters)} Validation, {len(test_clusters)} Test")
    
    def assign_split(cid):
        if cid in train_clusters:
            return 'train'
        elif cid in val_clusters:
            return 'validation'
        else:
            return 'test'
            
    df['split'] = df['cluster_id'].apply(assign_split)
    
    # Verify zero duplicate texts between train, validation, and test
    train_texts = set(df[df['split'] == 'train']['complaint_text'].str.strip())
    val_texts = set(df[df['split'] == 'validation']['complaint_text'].str.strip())
    test_texts = set(df[df['split'] == 'test']['complaint_text'].str.strip())
    
    assert len(train_texts.intersection(val_texts)) == 0, "TRAIN-VAL LEAKAGE!"
    assert len(train_texts.intersection(test_texts)) == 0, "TRAIN-TEST LEAKAGE!"
    assert len(val_texts.intersection(test_texts)) == 0, "VAL-TEST LEAKAGE!"
    print("✅ MATHEMATICAL ZERO-LEAKAGE VERIFIED: 0 intersecting texts between all splits.")
    
    # Save datasets
    out_dir = os.path.join("ai", "datasets", "cleaned")
    os.makedirs(out_dir, exist_ok=True)
    
    df.to_csv(os.path.join(out_dir, "nexciv_multilingual_cleaned.csv"), index=False, encoding='utf-8')
    train_df = df[df['split'] == 'train'].reset_index(drop=True)
    val_df = df[df['split'] == 'validation'].reset_index(drop=True)
    test_df = df[df['split'] == 'test'].reset_index(drop=True)
    
    train_df.to_csv(os.path.join(out_dir, "train.csv"), index=False, encoding='utf-8')
    val_df.to_csv(os.path.join(out_dir, "validation.csv"), index=False, encoding='utf-8')
    test_df.to_csv(os.path.join(out_dir, "test.csv"), index=False, encoding='utf-8')
    
    # Update standard ai/datasets paths for pipeline integration
    train_df.to_csv(os.path.join("ai", "datasets", "train.csv"), index=False, encoding='utf-8')
    val_df.to_csv(os.path.join("ai", "datasets", "validation.csv"), index=False, encoding='utf-8')
    test_df.to_csv(os.path.join("ai", "datasets", "test.csv"), index=False, encoding='utf-8')
    
    print("\nDataset Summary:")
    print(f"- Total records: {len(df)}")
    print(f"- Train records: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"- Validation records: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"- Test records: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
    
    print("\nTest split department balance:")
    print(test_df['department'].value_counts())
    print("\nTest split language balance:")
    print(test_df['language_style'].value_counts())
    return df

if __name__ == '__main__':
    build_dataset()
