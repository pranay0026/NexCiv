"""
generate_ch7_diagrams.py
Generates Figure 7.1 and Figure 7.2 as clean, human-designed architectural diagrams
using matplotlib shapes and modern professional styling.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Ellipse

os.makedirs('docs/diagrams', exist_ok=True)

# -----------------------------------------------------------------------------
# FIGURE 7.1: Multimodal NLP and Department Classification Flowchart
# -----------------------------------------------------------------------------
def generate_fig7_1():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#94A3B8", fc="#F8FAFC", lw=1.5)
    ax.add_patch(bg)

    ax.text(50, 95, "Figure 7.1: Multilingual NLP Ingestion & Multi-Task Department Classification", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1E3A8A', fontfamily='sans-serif')

    # Step 1: Raw Ingestion Box
    b1 = FancyBboxPatch((5, 52), 18, 22, boxstyle="round,pad=0.8", ec="#2563EB", fc="#EFF6FF", lw=1.8)
    ax.add_patch(b1)
    ax.text(14, 66, "Raw Input Narrative", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1E40AF')
    ax.text(14, 57, "• Trilingual Text\n  (EN / TE / TE-Latn)\n• Potholes, Drains, Pipes\n• GPS & Timestamp", 
            ha='center', va='center', fontsize=8.5, color='#334155')

    # Step 2: Linguistic Normalization
    b2 = FancyBboxPatch((28, 52), 18, 22, boxstyle="round,pad=0.8", ec="#0D9488", fc="#CCFBF1", lw=1.8)
    ax.add_patch(b2)
    ax.text(37, 66, "Text Normalizer", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#0F766E')
    ax.text(37, 57, "• Unicode Normalization\n• Telugu Stemming\n• Punctuation Cleaning\n• Stop-word Filtering", 
            ha='center', va='center', fontsize=8.5, color='#334155')

    # Step 3: Feature Extraction
    b3 = FancyBboxPatch((51, 52), 20, 22, boxstyle="round,pad=0.8", ec="#D97706", fc="#FEF3C7", lw=1.8)
    ax.add_patch(b3)
    ax.text(61, 66, "Sublinear TF-IDF", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#B45309')
    ax.text(61, 57, "• Word n-grams (1 - 2)\n• Char n-grams (3 - 5)\n• Sub-word n-gram matrix\n• 45,000 Dimensions", 
            ha='center', va='center', fontsize=8.5, color='#334155')

    # Step 4: Calibrated Classifier
    b4 = FancyBboxPatch((76, 52), 19, 22, boxstyle="round,pad=0.8", ec="#7C3AED", fc="#F5F3FF", lw=1.8)
    ax.add_patch(b4)
    ax.text(85.5, 66, "Linear SVM (Model B)", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#6D28D9')
    ax.text(85.5, 57, "• SGD Modified Huber Loss\n• Platt Probability Scaling\n• L2 Regularization (a=1e-5)\n• 0.258 ms CPU Latency", 
            ha='center', va='center', fontsize=8.5, color='#334155')

    # Arrows horizontally across top pipeline
    arr = dict(arrowstyle="->", lw=1.8, color="#1E3A8A", mutation_scale=15)
    ax.annotate("", xy=(28, 63), xytext=(23, 63), arrowprops=arr)
    ax.annotate("", xy=(51, 63), xytext=(46, 63), arrowprops=arr)
    ax.annotate("", xy=(76, 63), xytext=(71, 63), arrowprops=arr)

    # Downward branching to 5 Municipal Wings Output
    ax.annotate("", xy=(50, 40), xytext=(85.5, 52), arrowprops=dict(arrowstyle="->", lw=1.8, color="#7C3AED", connectionstyle="arc3,rad=0.2", mutation_scale=15))
    ax.text(78, 44, "Predicted Posterior Probabilities", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#6D28D9')

    # 5 Output Department Badges
    depts = [
        (12, 22, "Roads & Buildings\n(road)\nAcc: 87.5%", "#1E3A8A", "#DBEAFE"),
        (31, 22, "Public Health & Drain\n(drainage)\nAcc: 85.7%", "#0D9488", "#CCFBF1"),
        (50, 22, "Water Supply\n(water_supply)\nAcc: 88.9%", "#2563EB", "#EFF6FF"),
        (69, 22, "Electrical & Lighting\n(street_lights)\nAcc: 91.1%", "#D97706", "#FEF3C7"),
        (88, 22, "Sanitation & Waste\n(others)\nAcc: 87.5%", "#059669", "#DCFCE7")
    ]

    for x, y, label, ec_c, fc_c in depts:
        d_box = FancyBboxPatch((x-8.5, y-10), 17, 18, boxstyle="round,pad=0.6", ec=ec_c, fc=fc_c, lw=1.8)
        ax.add_patch(d_box)
        ax.text(x, y-1, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color=ec_c)

    # Connecting horizontal dispatch bus
    ax.plot([12, 88], [35, 35], color='#64748B', lw=1.5, linestyle='--')
    for x, y, l, ec, fc in depts:
        ax.annotate("", xy=(x, y+8), xytext=(x, 35), arrowprops=dict(arrowstyle="->", lw=1.4, color='#64748B'))

    plt.tight_layout()
    plt.savefig('docs/diagrams/fig7_1_nlp_flowchart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig7_1_nlp_flowchart.png")

# -----------------------------------------------------------------------------
# FIGURE 7.2: 3-Layer Duplicate Detection Architecture
# -----------------------------------------------------------------------------
def generate_fig7_2():
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg = FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=1", ec="#94A3B8", fc="#F8FAFC", lw=1.5)
    ax.add_patch(bg)

    ax.text(50, 96, "Figure 7.2: 3-Layer Hybrid Geospatial-Semantic Duplicate Detection Architecture", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1E3A8A', fontfamily='sans-serif')

    # Incoming Complaint Input (Top Center)
    in_box = FancyBboxPatch((36, 81), 28, 11, boxstyle="round,pad=0.6", ec="#1E3A8A", fc="#EFF6FF", lw=2)
    ax.add_patch(in_box)
    ax.text(50, 88, "Incoming Citizen Grievance (c_i)", ha='center', va='center', fontsize=11, fontweight='bold', color='#1E3A8A')
    ax.text(50, 83.5, "Text, GPS (lat, lng), Timestamp, Photo", ha='center', va='center', fontsize=8.5, color='#475569')

    # Layer 1: Spatio-Temporal Filter
    l1_box = FancyBboxPatch((5, 52), 26, 20, boxstyle="round,pad=0.8", ec="#0D9488", fc="#CCFBF1", lw=1.8)
    ax.add_patch(l1_box)
    ax.text(18, 67, "Layer 1: Spatio-Temporal", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#0F766E')
    ax.text(18, 59, "• Haversine Distance <= 100m\n• Time Delta <= 72 Hours\n• Candidate Pruning Index\n• Mean Latency: 0.13 ms", 
            ha='center', va='center', fontsize=8.5, color='#334155')

    # Layer 2: Semantic S-BERT
    l2_box = FancyBboxPatch((37, 52), 26, 20, boxstyle="round,pad=0.8", ec="#2563EB", fc="#EFF6FF", lw=1.8)
    ax.add_patch(l2_box)
    ax.text(50, 67, "Layer 2: Dense Semantic", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1E40AF')
    ax.text(50, 59, "• Sentence-BERT (MiniLM-L12)\n• 384-d Dense Embedding\n• Cosine Similarity S >= 0.70\n• Mean Latency: 40.09 ms", 
            ha='center', va='center', fontsize=8.5, color='#334155')

    # Layer 3: Image Hash (dHash)
    l3_box = FancyBboxPatch((69, 52), 26, 20, boxstyle="round,pad=0.8", ec="#D97706", fc="#FEF3C7", lw=1.8)
    ax.add_patch(l3_box)
    ax.text(82, 67, "Layer 3: Visual Perceptual", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#B45309')
    ax.text(82, 59, "• 64-bit Difference Hash (dHash)\n• Hamming Distance H <= 10\n• Edge Gradient Similarity\n• Mean Latency: 0.85 ms", 
            ha='center', va='center', fontsize=8.5, color='#334155')

    # Input distributor arrows
    arr = dict(arrowstyle="->", lw=1.6, color="#1E3A8A", mutation_scale=14)
    ax.annotate("", xy=(18, 72), xytext=(40, 81), arrowprops=arr)
    ax.annotate("", xy=(50, 72), xytext=(50, 81), arrowprops=arr)
    ax.annotate("", xy=(82, 72), xytext=(60, 81), arrowprops=arr)

    # Decision Fusion Center
    fuse_box = FancyBboxPatch((28, 29), 44, 14, boxstyle="round,pad=0.8", ec="#4338CA", fc="#E0E7FF", lw=2)
    ax.add_patch(fuse_box)
    ax.text(50, 39, "Hybrid Decision Fusion Engine", ha='center', va='center', fontsize=11, fontweight='bold', color='#3730A3')
    ax.text(50, 33.5, "Composite Score = 0.35*GeoDist + 0.40*SBERT + 0.15*dHash + 0.10*TimeDelta", 
            ha='center', va='center', fontsize=8.5, color='#1E293B', fontweight='semibold')

    # Arrows to Decision Fusion
    ax.annotate("", xy=(38, 43), xytext=(18, 52), arrowprops=arr)
    ax.annotate("", xy=(50, 43), xytext=(50, 52), arrowprops=arr)
    ax.annotate("", xy=(62, 43), xytext=(82, 52), arrowprops=arr)

    # 3 Decision Outcomes (Bottom)
    outcomes = [
        (16, 12, "Score >= 0.85\n\nAUTO-LINK DUPLICATE\n(Precision: 91.80%, FPR: 0.0090)\nIncrement Master Ticket Upvote", "#059669", "#DCFCE7"),
        (50, 12, "0.65 <= Score < 0.85\n\nHUMAN SUPERVISOR REVIEW\n(Flagged in Ward Dispatch)\nPrevent Adjacent False Merges", "#D97706", "#FEF3C7"),
        (84, 12, "Score < 0.65\n\nUNIQUE COMPLAINT\n(New Master Ticket)\nProceed to Priority Engine", "#2563EB", "#EFF6FF")
    ]

    for x, y, label, ec_c, fc_c in outcomes:
        o_box = FancyBboxPatch((x-12, y-8), 24, 16, boxstyle="round,pad=0.6", ec=ec_c, fc=fc_c, lw=1.8)
        ax.add_patch(o_box)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold', color=ec_c)

    # Connect Fusion to 3 Outcomes
    ax.annotate("", xy=(16, 20), xytext=(35, 29), arrowprops=dict(arrowstyle="->", lw=1.6, color="#059669", mutation_scale=14))
    ax.annotate("", xy=(50, 20), xytext=(50, 29), arrowprops=dict(arrowstyle="->", lw=1.6, color="#D97706", mutation_scale=14))
    ax.annotate("", xy=(84, 20), xytext=(65, 29), arrowprops=dict(arrowstyle="->", lw=1.6, color="#2563EB", mutation_scale=14))

    plt.tight_layout()
    plt.savefig('docs/diagrams/fig7_2_duplicate_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig7_2_duplicate_architecture.png")

if __name__ == "__main__":
    generate_fig7_1()
    generate_fig7_2()
