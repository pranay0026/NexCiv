"""
generate_human_diagrams.py
Generates 5 publication-grade architectural diagrams (DFD 0, DFD 1, UML Use Case, UML Sequence, Database ER)
using matplotlib vector shapes, mimicking clean Microsoft Word Shapes / Visio diagrams created by a senior human engineer.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle, FancyArrowPatch, ConnectionPatch

os.makedirs('docs/diagrams', exist_ok=True)

# -------------------------------------------------------------------------------------------------
# FIGURE 4.2: DFD LEVEL 0 (CONTEXT DIAGRAM)
# -------------------------------------------------------------------------------------------------
def generate_dfd_level0():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background subtle card
    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#94A3B8", fc="#F8FAFC", lw=1.5)
    ax.add_patch(bg)

    # Title
    ax.text(50, 95, "Figure 4.2: Data Flow Diagram (DFD Level 0 - Context Level)", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1E3A8A', fontfamily='sans-serif')

    # Central System: Process 0.0
    sys_box = FancyBboxPatch((35, 36), 30, 26, boxstyle="round,pad=1.5", ec="#1E3A8A", fc="#EFF6FF", lw=2.5)
    ax.add_patch(sys_box)
    ax.text(50, 52, "0.0\nNEXCIV PLATFORM", ha='center', va='center', fontsize=12, fontweight='bold', color='#1E3A8A')
    ax.text(50, 42, "AI-Driven Urban Civic Issue\nPrioritization & Workforce\nAllocation Engine", 
            ha='center', va='center', fontsize=9.5, color='#334155', style='italic')

    # External Entity: Citizen (Left)
    cit_box = FancyBboxPatch((4, 38), 18, 22, boxstyle="square,pad=0.8", ec="#3B82F6", fc="#FFFFFF", lw=2)
    ax.add_patch(cit_box)
    ax.text(13, 51, "CITIZEN", ha='center', va='center', fontsize=11, fontweight='bold', color='#1E40AF')
    ax.text(13, 44, "Multimodal User\n(Mobile / Web App\nEnglish / Telugu)", ha='center', va='center', fontsize=8.5, color='#475569')

    # External Entity: Municipal Worker (Right)
    wrk_box = FancyBboxPatch((78, 38), 18, 22, boxstyle="square,pad=0.8", ec="#059669", fc="#FFFFFF", lw=2)
    ax.add_patch(wrk_box)
    ax.text(87, 51, "FIELD WORKER", ha='center', va='center', fontsize=11, fontweight='bold', color='#065F46')
    ax.text(87, 44, "Municipal Cadre\n(Sanitation, Roads,\nDrainage, Electrical)", ha='center', va='center', fontsize=8.5, color='#475569')

    # External Entity: Department Head / Admin (Top)
    adm_box = FancyBboxPatch((36, 73), 28, 16, boxstyle="square,pad=0.8", ec="#7C3AED", fc="#FFFFFF", lw=2)
    ax.add_patch(adm_box)
    ax.text(50, 83, "MUNICIPAL OFFICIAL / ADMIN", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#5B21B6')
    ax.text(50, 77, "Ward Officers, HoDs, Municipal Commissioner", ha='center', va='center', fontsize=8.5, color='#475569')

    # External Entity: GIS & SMS Gateway (Bottom)
    ext_box = FancyBboxPatch((36, 9), 28, 16, boxstyle="square,pad=0.8", ec="#D97706", fc="#FFFFFF", lw=2)
    ax.add_patch(ext_box)
    ax.text(50, 19, "EXTERNAL TELEMETRY & SMS", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#92400E')
    ax.text(50, 13, "GPS Geocoder, Reverse Geocoding, SMS Alerts", ha='center', va='center', fontsize=8.5, color='#475569')

    # Arrows Citizen <-> NexCiv
    arrow_props = dict(arrowstyle="->", lw=1.8, color="#2563EB", mutation_scale=15)
    ax.annotate("", xy=(35, 52), xytext=(22, 52), arrowprops=arrow_props)
    ax.text(28.5, 55, "Complaint Details\n(Text, Photo, GPS)", ha='center', va='bottom', fontsize=8, color='#1E40AF', fontweight='semibold')

    arrow_props_back = dict(arrowstyle="->", lw=1.8, color="#2563EB", mutation_scale=15)
    ax.annotate("", xy=(22, 44), xytext=(35, 44), arrowprops=arrow_props_back)
    ax.text(28.5, 41, "Ticket ID, Live SLA,\nStatus Updates", ha='center', va='top', fontsize=8, color='#1E40AF', fontweight='semibold')

    # Arrows NexCiv <-> Worker
    arrow_props_wrk = dict(arrowstyle="->", lw=1.8, color="#059669", mutation_scale=15)
    ax.annotate("", xy=(78, 52), xytext=(65, 52), arrowprops=arrow_props_wrk)
    ax.text(71.5, 55, "Dispatched Work Order\n& Priority Navigation", ha='center', va='bottom', fontsize=8, color='#065F46', fontweight='semibold')

    arrow_props_wrk_back = dict(arrowstyle="->", lw=1.8, color="#059669", mutation_scale=15)
    ax.annotate("", xy=(65, 44), xytext=(78, 44), arrowprops=arrow_props_wrk_back)
    ax.text(71.5, 41, "Geotagged Repair Photo\n& Task Closure Event", ha='center', va='top', fontsize=8, color='#065F46', fontweight='semibold')

    # Arrows NexCiv <-> Admin
    arrow_props_adm = dict(arrowstyle="->", lw=1.8, color="#7C3AED", mutation_scale=15)
    ax.annotate("", xy=(46, 73), xytext=(46, 62), arrowprops=arrow_props_adm)
    ax.text(42, 67.5, "Live Command Heatmap,\nSLA Breach Alerts", ha='right', va='center', fontsize=8, color='#5B21B6', fontweight='semibold')

    arrow_props_adm_down = dict(arrowstyle="->", lw=1.8, color="#7C3AED", mutation_scale=15)
    ax.annotate("", xy=(54, 62), xytext=(54, 73), arrowprops=arrow_props_adm_down)
    ax.text(58, 67.5, "Roster Updates,\nPriority Override", ha='left', va='center', fontsize=8, color='#5B21B6', fontweight='semibold')

    # Arrows NexCiv <-> Telemetry
    arrow_props_ext = dict(arrowstyle="->", lw=1.8, color="#D97706", mutation_scale=15)
    ax.annotate("", xy=(50, 25), xytext=(50, 36), arrowprops=arrow_props_ext)
    ax.text(50, 30.5, "Trigger OTP / SMS Notifications & Coordinates", ha='center', va='center', fontsize=8, color='#92400E', fontweight='semibold')

    plt.tight_layout()
    plt.savefig('docs/diagrams/fig4_2_dfd_level0.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig4_2_dfd_level0.png")

# -------------------------------------------------------------------------------------------------
# FIGURE 4.3: DFD LEVEL 1 (DECOMPOSITION)
# -------------------------------------------------------------------------------------------------
def generate_dfd_level1():
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#94A3B8", fc="#F8FAFC", lw=1.5)
    ax.add_patch(bg)

    ax.text(50, 96, "Figure 4.3: Data Flow Diagram (DFD Level 1 - Operational Process Decomposition)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1E3A8A', fontfamily='sans-serif')

    # Processes: 5 circular/curved rectangles
    procs = [
        (16, 72, "1.0 Ingestion &\nClassification\n(Multilingual SVM)", "#1E40AF", "#DBEAFE"),
        (50, 72, "2.0 Duplicate\nDetection Engine\n(Spatio-Temporal+SBERT)", "#0D9488", "#CCFBF1"),
        (84, 72, "3.0 Priority Scoring\n& SLA Urgency\n(3-Tier + LightGBM)", "#B45309", "#FEF3C7"),
        (32, 28, "4.0 Workforce\nOptimization Engine\n(OR-Tools CP-SAT)", "#4338CA", "#E0E7FF"),
        (68, 28, "5.0 Resolution\nVerification Engine\n(SSIM & Geo-Fence)", "#15803D", "#DCFCE7")
    ]

    for x, y, label, border, fill in procs:
        p_box = FancyBboxPatch((x-11, y-10), 22, 19, boxstyle="round,pad=1.2", ec=border, fc=fill, lw=2)
        ax.add_patch(p_box)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold', color=border)

    # Data Stores (D1 to D4)
    stores = [
        (16, 48, "D1: Citizen & Auth Store", "#475569", "#F1F5F9"),
        (50, 48, "D2: Grievances & Incident Clusters", "#475569", "#F1F5F9"),
        (84, 48, "D3: Cadre Workers & Work Orders", "#475569", "#F1F5F9"),
        (50, 8, "D4: Resolution Audit & Proof Archive", "#475569", "#F1F5F9")
    ]

    for x, y, label, border, fill in stores:
        # Datastore styling: two parallel horizontal lines with open ends
        s_box = FancyBboxPatch((x-13, y-4), 26, 8, boxstyle="square,pad=0.2", ec=border, fc=fill, lw=1.5)
        ax.add_patch(s_box)
        # draw double lines top and bottom
        ax.plot([x-13, x+13], [y+4, y+4], color='#1E293B', lw=2)
        ax.plot([x-13, x+13], [y-4, y-4], color='#1E293B', lw=2)
        ax.text(x, y, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E293B')

    # Connectors
    # 1.0 -> D1 & 1.0 -> 2.0
    arr = dict(arrowstyle="->", lw=1.6, color="#1E3A8A", mutation_scale=14)
    ax.annotate("", xy=(39, 72), xytext=(27, 72), arrowprops=arr)
    ax.text(33, 75, "Department &\nRaw Complaint", ha='center', va='bottom', fontsize=7.5, color='#1E3A8A', fontweight='semibold')

    # 2.0 -> D2 & 2.0 -> 3.0
    ax.annotate("", xy=(73, 72), xytext=(61, 72), arrowprops=arr)
    ax.text(67, 75, "Unique Ticket /\nCluster Merged", ha='center', va='bottom', fontsize=7.5, color='#0D9488', fontweight='semibold')

    # 1.0 -> D1
    ax.annotate("", xy=(16, 52), xytext=(16, 62), arrowprops=arr)

    # 2.0 <-> D2
    ax.annotate("", xy=(50, 52), xytext=(50, 62), arrowprops=arr)
    ax.annotate("", xy=(50, 62), xytext=(50, 52), arrowprops=arr)

    # 3.0 -> D2 (Store priority)
    ax.annotate("", xy=(63, 49), xytext=(78, 62), arrowprops=arr)
    ax.text(74, 54, "Assigned Priority\n& Max SLA", ha='center', va='center', fontsize=7.5, color='#B45309', fontweight='semibold')

    # D2 -> 4.0 (Fetch pending tickets)
    ax.annotate("", xy=(32, 37), xytext=(45, 44), arrowprops=arr)
    ax.text(34, 43, "Pending Tickets", ha='center', va='center', fontsize=7.5, color='#4338CA', fontweight='semibold')

    # D3 <-> 4.0 (Cadre availability)
    ax.annotate("", xy=(43, 28), xytext=(74, 44), arrowprops=arr)
    ax.text(62, 35, "Worker Roster &\nLocation Bounds", ha='center', va='center', fontsize=7.5, color='#4338CA', fontweight='semibold')

    # 4.0 -> D3 (Store assignments)
    ax.annotate("", xy=(84, 44), xytext=(43, 25), arrowprops=arr)

    # Worker completes -> 5.0
    ax.annotate("", xy=(68, 37), xytext=(84, 44), arrowprops=arr)
    ax.text(79, 35, "After-Repair Photo", ha='center', va='center', fontsize=7.5, color='#15803D', fontweight='semibold')

    # 5.0 -> D4 (Archive proof)
    ax.annotate("", xy=(55, 12), xytext=(64, 20), arrowprops=arr)
    ax.text(65, 14, "Verified Closure Certificate", ha='center', va='center', fontsize=7.5, color='#15803D', fontweight='semibold')

    plt.tight_layout()
    plt.savefig('docs/diagrams/fig4_3_dfd_level1.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig4_3_dfd_level1.png")

# -------------------------------------------------------------------------------------------------
# FIGURE 4.4: UML USE CASE DIAGRAM
# -------------------------------------------------------------------------------------------------
def generate_uml_usecase():
    fig, ax = plt.subplots(figsize=(12, 8.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#94A3B8", fc="#F8FAFC", lw=1.5)
    ax.add_patch(bg)

    ax.text(50, 96, "Figure 4.4: UML Use Case Model (Actors & Primary Operational Boundary)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1E3A8A', fontfamily='sans-serif')

    # System boundary box
    sys_bound = FancyBboxPatch((28, 6), 46, 85, boxstyle="square,pad=1", ec="#1E3A8A", fc="#FFFFFF", lw=2, linestyle='--')
    ax.add_patch(sys_bound)
    ax.text(51, 88.5, "NexCiv Core Platform Boundary", ha='center', va='center', fontsize=11, fontweight='bold', color='#1E3A8A')

    # Use Cases (Ellipses)
    ucs = [
        (51, 80, "UC-01: Submit Grievance\n(Text, Photo, GPS, Multilingual)"),
        (51, 68, "UC-02: Live Tracking &\nSMS Closure Updates"),
        (51, 56, "UC-03: Auto-Route &\nDuplicate Incident Merge"),
        (51, 44, "UC-04: Accept Work Order &\nNavigate Incident Location"),
        (51, 32, "UC-05: Upload Before/After\nRepair Photo & Geo-Tag"),
        (51, 20, "UC-06: Operations Heatmap &\nPriority Override Triage"),
        (51, 9, "UC-07: Configure Ward Boundary,\nRosters & SLA Thresholds")
    ]

    for x, y, text in ucs:
        el = Ellipse((x, y), 38, 7.8, ec="#2563EB", fc="#EFF6FF", lw=1.5)
        ax.add_patch(el)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.5, color='#1E293B', fontweight='medium')

    # Actors: Function to draw clean stick figure
    def draw_actor(ax, x, y, label, color):
        # Head
        head = Ellipse((x, y+4), 3, 3, ec=color, fc=color)
        ax.add_patch(head)
        # Body
        ax.plot([x, x], [y+2.5, y-2], color=color, lw=2.2)
        # Arms
        ax.plot([x-2.5, x+2.5], [y+1, y+1], color=color, lw=2.2)
        # Legs
        ax.plot([x, x-2], [y-2, y-5], color=color, lw=2.2)
        ax.plot([x, x+2], [y-2, y-5], color=color, lw=2.2)
        # Label
        ax.text(x, y-7.5, label, ha='center', va='top', fontsize=9.5, fontweight='bold', color=color)

    # Actor 1: Citizen (Left)
    draw_actor(ax, 14, 73, "CITIZEN\n(Public User)", "#1E40AF")
    # Actor 2: Field Worker (Right Top)
    draw_actor(ax, 88, 53, "CADRE WORKER\n(Sanitation/Road/Elect)", "#065F46")
    # Actor 3: Municipal Officer (Right Mid)
    draw_actor(ax, 88, 27, "DEPARTMENT\nOFFICER", "#5B21B6")
    # Actor 4: System Admin (Right Bottom)
    draw_actor(ax, 88, 11, "SYSTEM ADMIN", "#92400E")

    # Association lines
    line_kw = dict(color="#64748B", lw=1.5)
    # Citizen -> UC-01, UC-02
    ax.plot([17, 32], [73, 80], **line_kw)
    ax.plot([17, 32], [71, 68], **line_kw)

    # Worker -> UC-04, UC-05
    ax.plot([85, 70], [53, 44], **line_kw)
    ax.plot([85, 70], [50, 32], **line_kw)

    # Officer -> UC-06, UC-02
    ax.plot([85, 70], [27, 20], **line_kw)
    ax.plot([85, 70], [29, 44], **line_kw)

    # Admin -> UC-07
    ax.plot([85, 70], [11, 9], **line_kw)

    # System Internal -> UC-03
    ax.text(51, 61.5, "<<system automatic>>", ha='center', va='center', fontsize=7.5, color='#64748B', style='italic')
    ax.annotate("", xy=(51, 59.9), xytext=(51, 64.1), arrowprops=dict(arrowstyle="->", lw=1.2, color="#64748B", linestyle="--"))

    plt.tight_layout()
    plt.savefig('docs/diagrams/fig4_4_use_case.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig4_4_use_case.png")

# -------------------------------------------------------------------------------------------------
# FIGURE 4.5: UML SEQUENCE DIAGRAM
# -------------------------------------------------------------------------------------------------
def generate_uml_sequence():
    fig, ax = plt.subplots(figsize=(13, 9.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#94A3B8", fc="#F8FAFC", lw=1.5)
    ax.add_patch(bg)

    ax.text(50, 96.5, "Figure 4.5: UML Sequence Diagram (End-to-End Civic Grievance Lifecycle)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1E3A8A', fontfamily='sans-serif')

    # Lifeline objects
    cols = [
        (10, "Citizen\n(User)"),
        (26, "Citizen UI\n(React Portal)"),
        (42, "FastAPI\nGateway"),
        (58, "AI Engines\n(NLP/S-BERT/CP)"),
        (74, "PostgreSQL\nDatabase"),
        (90, "Cadre App\n(Field Crew)")
    ]

    for x, title in cols:
        # Header box
        h_box = FancyBboxPatch((x-6.5, 87), 13, 6, boxstyle="round,pad=0.5", ec="#1E3A8A", fc="#EFF6FF", lw=1.8)
        ax.add_patch(h_box)
        ax.text(x, 90, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E3A8A')
        # Dashed lifeline
        ax.plot([x, x], [87, 8], color='#94A3B8', linestyle='--', lw=1.2)

    # Lifeline activation bars
    activations = [
        (10, 83, 14, "#93C5FD"),
        (26, 83, 16, "#93C5FD"),
        (42, 82, 19, "#93C5FD"),
        (58, 80, 24, "#93C5FD"),
        (74, 69, 12, "#93C5FD"),
        (90, 48, 22, "#86EFAC"),
        (42, 38, 20, "#93C5FD"),
        (58, 35, 12, "#93C5FD"),
        (74, 25, 8, "#93C5FD")
    ]
    for x, y_top, height, fill in activations:
        act = Rectangle((x-0.9, y_top-height), 1.8, height, ec="#1E3A8A", fc=fill, lw=1)
        ax.add_patch(act)

    # Sequence Messages
    messages = [
        (83, 10, 26, "1: Submit Complaint (Text, Image, GPS)", False),
        (80, 26, 42, "2: POST /api/v1/complaints", False),
        (77, 42, 58, "3: classify_dept() & detect_duplicates()", False),
        (73, 58, 58, "4: S-BERT Sim & 3-Tier Priority Score", False, True),
        (69, 58, 74, "5: INSERT ticket, update cluster count", False),
        (65, 42, 26, "6: HTTP 201 Created (TrackID, SLA: 24h)", True),
        (61, 26, 10, "7: Display Tracking Dashboard & SMS OTP", True),
        (55, 58, 74, "8: OR-Tools CP-SAT Worker Allocation", False),
        (48, 74, 90, "9: Push Notification: Work Order Assigned", False),
        (40, 90, 42, "10: POST /resolve (Geotagged After-Photo)", False),
        (34, 42, 58, "11: verify_repair() -> SSIM & Geofence Match", False),
        (27, 58, 74, "12: UPDATE status='Resolved', SLA Audit Log", False),
        (20, 42, 10, "13: SMS Alert: Grievance Resolved + Certificate", True)
    ]

    for item in messages:
        if len(item) == 5:
            y, x1, x2, label, is_return = item
            is_self = False
        else:
            y, x1, x2, label, is_return, is_self = item

        if is_self:
            # Self-loop arrow
            ax.annotate("", xy=(x1+1, y-2), xytext=(x1+1, y+1),
                        arrowprops=dict(arrowstyle="->", lw=1.4, color="#1E3A8A", 
                                        connectionstyle="arc3,rad=-1.2", mutation_scale=12))
            ax.text(x1+2.5, y-0.5, label, va='center', fontsize=7.5, color='#1E293B', fontweight='semibold')
        else:
            style = "->"
            ls = "--" if is_return else "-"
            color = "#059669" if is_return else "#1E3A8A"
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle=style, lw=1.4, color=color, linestyle=ls, mutation_scale=12))
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y+1.2, label, ha='center', va='bottom', fontsize=7.5, color='#1E293B', fontweight='semibold')

    plt.tight_layout()
    plt.savefig('docs/diagrams/fig4_5_sequence_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig4_5_sequence_diagram.png")

# -------------------------------------------------------------------------------------------------
# FIGURE 4.6: DATABASE ER SCHEMA
# -------------------------------------------------------------------------------------------------
def generate_er_schema():
    fig, ax = plt.subplots(figsize=(13.5, 9.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#94A3B8", fc="#F8FAFC", lw=1.5)
    ax.add_patch(bg)

    ax.text(50, 96.5, "Figure 4.6: Database Entity-Relationship (ER) Relational Schema", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1E3A8A', fontfamily='sans-serif')

    # Draw table function
    def draw_entity(ax, x, y, width, height, title, attributes, header_color="#1E3A8A"):
        # Header box
        h_h = 4.5
        box = FancyBboxPatch((x, y-height), width, height, boxstyle="square,pad=0.2", ec="#64748B", fc="#FFFFFF", lw=1.5)
        ax.add_patch(box)
        head = Rectangle((x, y-h_h), width, h_h, ec="#64748B", fc=header_color, lw=1.5)
        ax.add_patch(head)
        ax.text(x + width/2, y - h_h/2, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#FFFFFF')

        # Attributes
        curr_y = y - h_h - 1.8
        for attr in attributes:
            is_pk = "PK" in attr
            is_fk = "FK" in attr
            fweight = 'bold' if (is_pk or is_fk) else 'normal'
            fcolor = '#1E3A8A' if is_pk else ('#7C3AED' if is_fk else '#334155')
            ax.text(x + 1.2, curr_y, attr, ha='left', va='center', fontsize=7.8, color=fcolor, fontweight=fweight)
            curr_y -= 2.5

    # Tables
    # 1. CITIZENS (Top Left)
    draw_entity(ax, 4, 88, 25, 23, "citizens", [
        "citizen_id : UUID [PK]",
        "phone_number : VARCHAR(15)",
        "full_name : VARCHAR(100)",
        "preferred_language : VARCHAR(10)",
        "ward_number : INT",
        "created_at : TIMESTAMP",
        "verified_status : BOOLEAN"
    ], "#1E3A8A")

    # 2. COMPLAINTS (Center)
    draw_entity(ax, 37, 88, 30, 42, "complaints", [
        "complaint_id : UUID [PK]",
        "tracking_token : VARCHAR(16) [UQ]",
        "citizen_id : UUID [FK]",
        "department_id : INT [FK]",
        "cluster_id : UUID [FK]",
        "raw_description : TEXT",
        "language_detected : VARCHAR(10)",
        "latitude : NUMERIC(9,6)",
        "longitude : NUMERIC(9,6)",
        "before_photo_url : VARCHAR(255)",
        "priority_score : NUMERIC(5,2)",
        "priority_tier : VARCHAR(10)",
        "status : VARCHAR(20)",
        "sla_deadline : TIMESTAMP",
        "created_at : TIMESTAMP"
    ], "#1E40AF")

    # 3. DEPARTMENTS (Top Right)
    draw_entity(ax, 74, 88, 22, 18, "departments", [
        "department_id : INT [PK]",
        "department_name : VARCHAR(80)",
        "code : VARCHAR(10)",
        "base_sla_hours : INT",
        "active_status : BOOLEAN"
    ], "#0D9488")

    # 4. DUPLICATE_CLUSTERS (Bottom Left)
    draw_entity(ax, 4, 55, 25, 21, "duplicate_clusters", [
        "cluster_id : UUID [PK]",
        "master_complaint_id : UUID [FK]",
        "department_id : INT [FK]",
        "incident_count : INT",
        "centroid_lat : NUMERIC(9,6)",
        "centroid_lng : NUMERIC(9,6)",
        "last_incident_at : TIMESTAMP"
    ], "#D97706")

    # 5. MUNICIPAL_WORKERS (Bottom Right)
    draw_entity(ax, 74, 62, 22, 25, "municipal_workers", [
        "worker_id : UUID [PK]",
        "department_id : INT [FK]",
        "full_name : VARCHAR(100)",
        "cadre_wing : VARCHAR(40)",
        "current_latitude : NUMERIC(9,6)",
        "current_longitude : NUMERIC(9,6)",
        "active_work_orders : INT",
        "shift_status : VARCHAR(15)"
    ], "#059669")

    # 6. ASSIGNMENTS & WORK ORDERS (Bottom Center)
    draw_entity(ax, 37, 39, 30, 22, "assignments", [
        "assignment_id : UUID [PK]",
        "complaint_id : UUID [FK]",
        "worker_id : UUID [FK]",
        "assigned_at : TIMESTAMP",
        "dispatched_lat : NUMERIC(9,6)",
        "dispatched_lng : NUMERIC(9,6)",
        "completion_status : VARCHAR(20)"
    ], "#4338CA")

    # 7. RESOLUTION_PROOFS (Bottom Center Lower)
    draw_entity(ax, 4, 27, 25, 22, "resolution_proofs", [
        "proof_id : UUID [PK]",
        "complaint_id : UUID [FK]",
        "worker_id : UUID [FK]",
        "after_photo_url : VARCHAR(255)",
        "ssim_similarity_score : NUMERIC(4,3)",
        "geo_distance_meters : NUMERIC(6,2)",
        "verified_by_officer_id : UUID [FK]",
        "resolved_timestamp : TIMESTAMP"
    ], "#B45309")

    # Foreign Key Relationship Lines
    rel_kw = dict(color="#64748B", lw=1.6)
    # citizens -> complaints (1:N)
    ax.plot([29, 37], [76, 76], **rel_kw)
    ax.text(30, 77.2, "1", fontsize=8.5, fontweight='bold', color='#1E3A8A')
    ax.text(35.5, 77.2, "N", fontsize=8.5, fontweight='bold', color='#1E3A8A')

    # departments -> complaints (1:N)
    ax.plot([74, 67], [76, 76], **rel_kw)
    ax.text(72.5, 77.2, "1", fontsize=8.5, fontweight='bold', color='#0D9488')
    ax.text(68, 77.2, "N", fontsize=8.5, fontweight='bold', color='#0D9488')

    # duplicate_clusters -> complaints (1:N)
    ax.plot([29, 37], [45, 60], **rel_kw)
    ax.text(30, 46, "1", fontsize=8.5, fontweight='bold', color='#D97706')
    ax.text(35, 59, "N", fontsize=8.5, fontweight='bold', color='#D97706')

    # complaints -> assignments (1:N)
    ax.plot([52, 52], [46, 39], **rel_kw)
    ax.text(50.5, 44.5, "1", fontsize=8.5, fontweight='bold', color='#4338CA')
    ax.text(50.5, 40.5, "N", fontsize=8.5, fontweight='bold', color='#4338CA')

    # municipal_workers -> assignments (1:N)
    ax.plot([74, 67], [35, 35], **rel_kw)
    ax.text(72.5, 36.2, "1", fontsize=8.5, fontweight='bold', color='#059669')
    ax.text(68, 36.2, "N", fontsize=8.5, fontweight='bold', color='#059669')

    # complaints -> resolution_proofs (1:1)
    ax.plot([37, 29], [48, 22], **rel_kw)
    ax.text(35.5, 46, "1", fontsize=8.5, fontweight='bold', color='#B45309')
    ax.text(30, 23, "1", fontsize=8.5, fontweight='bold', color='#B45309')

    plt.tight_layout()
    plt.savefig('docs/diagrams/fig4_6_er_schema.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig4_6_er_schema.png")

if __name__ == "__main__":
    generate_dfd_level0()
    generate_dfd_level1()
    generate_uml_usecase()
    generate_uml_sequence()
    generate_er_schema()
    print("All 5 human-designed architectural diagrams successfully generated.")
