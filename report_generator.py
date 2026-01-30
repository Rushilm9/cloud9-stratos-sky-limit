import pandas as pd
from fpdf import FPDF
import io
import re

def clean_for_pdf(text):
    """Strips emojis and non-latin-1 characters that break standard FPDF fonts."""
    if not text: return ""
    text = re.sub(r'[^\x00-\xff]', '', str(text))
    text = text.replace('**', '').replace('#', '').replace('__', '')
    return text.strip()

def generate_markdown_report(team_name, enriched_data, playbook, structured_roster, winning_trends, counter_strategy):
    """Generates a clean Markdown report for team scouting."""
    twins = sum(1 for s in enriched_data["series"] if s["series_win"])
    tser = len(enriched_data["series"])
    win_rate = f"{round((twins/tser)*100,1) if tser > 0 else 0}%"
    record = f"{twins}W - {tser-twins}L"
    avg_kda = round(sum(p['avg_kda'] for p in enriched_data['top_players'])/len(enriched_data['top_players']),1) if enriched_data['top_players'] else 0

    md = f"""# 🎖️ STRATEGIC DOSSIER: {team_name.upper()}

## 📊 COMMANDER'S OVERVIEW
- **Win Rate:** {win_rate}
- **Record:** {record}
- **Combat Rating:** {avg_kda}
- **Map Win %:** {enriched_data.get('map_win_rate', 0)}%
- **Star Impact:** {enriched_data['top_players'][0]['impact_score'] if enriched_data['top_players'] else 0}
- **Winning Pattern:** {winning_trends}
- **Critical Counter Plan:** {counter_strategy}

## 👥 ROSTER INTELLIGENCE
"""
    ro_map = {p['name'].lower().strip(): p for p in structured_roster}
    for pr in enriched_data['top_players']:
        pa = ro_map.get(pr['name'].lower().strip(), {})
        cat = pa.get('category', 'PRO COMBATANT')
        md += f"### {pr['name']} ({cat})\n"
        md += f"- **Avg KDA:** {pr['avg_kda']}\n"
        md += f"- **Strength:** {pa.get('strength', 'N/A')}\n"
        md += f"- **Weakness:** {pa.get('weakness', 'N/A')}\n\n"

    md += "\n## 🧠 ELITE STRATEGIC PLAYBOOK\n"
    md += f"### ⚠️ VULNERABILITY REPORT\n{playbook.get('vulnerability', 'N/A')}\n\n"
    md += f"### ⚔️ KILLER STRATEGEMA\n{playbook.get('killer_strategy', 'N/A')}\n\n"
    md += f"### 👥 THREAT ASSESSMENT\n{playbook.get('roster_threats', 'N/A')}\n\n"
    md += f"### 🏁 OPERATION TIMELINE\n{playbook.get('execution_plan', 'N/A')}\n"

    return md

class PDFReport(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.primary_blue = (0, 71, 171) # Cloud9 Blue
        self.light_blue = (235, 245, 255)
        self.text_dark = (33, 37, 41)
        self.text_gray = (108, 117, 125)

    def header(self):
        # Header Bar
        self.set_fill_color(*self.primary_blue)
        self.rect(0, 0, 210, 35, 'F')
        
        self.set_font('Arial', 'B', 18)
        self.set_text_color(255, 255, 255)
        self.set_y(12)
        self.cell(0, 10, 'CLOUD9 AI STRATEGIC INTELLIGENCE', 0, 1, 'C')
        
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, 'POWERED BY GRID ESPORTS & JETBRAINS AI', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'CLASSIFIED DOSSIER - PAGE {self.page_no()}', 0, 0, 'C')

    def section_title(self, label):
        self.ln(5)
        self.set_x(20)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*self.primary_blue)
        self.cell(0, 10, label.upper(), 0, 1)
        self.set_draw_color(*self.primary_blue)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(3)

def generate_pdf_report(team_name, enriched_data, playbook, structured_roster, winning_trends, counter_strategy):
    """Generates a Premium Strategic Dossier for a single team."""
    pdf = PDFReport()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_page()
    
    # Target Title
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, f'ANALYSIS TARGET: {team_name.upper()}', 0, 1, 'C')
    
    # 1. SUMMARY BOX
    pdf.section_title('Operational Summary')
    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(20, pdf.get_y(), 170, 30, 'DF')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(100, 100, 100)
    
    twins = sum(1 for s in enriched_data["series"] if s["series_win"])
    tser = len(enriched_data["series"])
    wr = f"{round((twins/tser)*100,1) if tser > 0 else 0}%"
    
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_x(25)
    pdf.cell(50, 7, f"WIN RATE: {wr}", 0, 0)
    pdf.cell(60, 7, f"RECORD: {twins}W - {tser-twins}L", 0, 0)
    pdf.cell(50, 7, f"MAP DOMINANCE: {enriched_data.get('map_win_rate', 0)}%", 0, 1)
    
    pdf.set_x(25)
    impact = enriched_data['top_players'][0]['impact_score'] if enriched_data['top_players'] else 0
    pdf.cell(50, 7, f"STAR IMPACT: {impact}", 0, 0)
    pdf.cell(60, 7, f"DATA SAMPLES: {tser} SERIES", 0, 1)
    
    pdf.ln(10)
    
    # 2. KEY STRATEGIES
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(*pdf.primary_blue)
    pdf.set_x(20)
    pdf.cell(0, 8, 'WINNING PLAYSTYLE:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(40, 40, 40)
    pdf.set_x(20)
    pdf.multi_cell(170, 6, clean_for_pdf(winning_trends))
    
    pdf.ln(4)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(200, 50, 50) # Red for Counter
    pdf.set_x(20)
    pdf.cell(0, 8, 'MISSION COUNTER-STRATEGY:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(40, 40, 40)
    pdf.set_x(20)
    pdf.multi_cell(170, 6, clean_for_pdf(counter_strategy))

    # 3. MATCH HISTORY
    pdf.section_title('Tactical Engagement History')
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(0, 71, 171) # Blue header
    pdf.set_text_color(255, 255, 255)
    pdf.set_x(20)
    pdf.cell(25, 10, 'Date', 1, 0, 'C', True)
    pdf.cell(60, 10, 'Opponent', 1, 0, 'C', True)
    pdf.cell(20, 10, 'Result', 1, 0, 'C', True)
    pdf.cell(65, 10, 'Key Player (MVP)', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(33, 37, 41)
    for s in enriched_data["series"][:15]:
        res_str = "WIN" if s["series_win"] else "LOSS"
        pdf.set_x(20)
        pdf.cell(25, 8, str(s.get('date','N/A'))[:10], 1, 0, 'C')
        pdf.cell(60, 8, clean_for_pdf(s['opponent'])[:28], 1, 0, 'L')
        pdf.cell(20, 8, res_str, 1, 0, 'C')
        pdf.cell(65, 8, clean_for_pdf(s.get('key_player','N/A'))[:32], 1, 1, 'L')

    # 4. PLAYER ROSTER
    pdf.add_page()
    pdf.section_title('Elite Roster Intelligence')
    ro_map = {p['name'].lower().strip(): p for p in structured_roster}
    
    for pr in enriched_data['top_players']:
        p_name_norm = pr['name'].lower().strip()
        pa = ro_map.get(p_name_norm, {})
        
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(*pdf.primary_blue)
        pdf.cell(0, 8, f"{pr['name'].upper()} - {pa.get('category', 'PRO COMBATANT')}", 0, 1)
        
        pdf.set_x(20)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, f"Average KDA: {pr['avg_kda']} | Strategic Impact: {pr.get('impact_score',0)}", 0, 1)
        
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.set_x(20)
        pdf.multi_cell(170, 5, f"STRENGTH: {clean_for_pdf(pa.get('strength', 'High adaptability in team fights.'))}")
        pdf.set_x(20)
        pdf.multi_cell(170, 5, f"WEAKNESS: {clean_for_pdf(pa.get('weakness', 'Susceptible to early map pressure.'))}")
        pdf.ln(5)

    # 5. AI PLAYBOOK
    pdf.add_page()
    pdf.section_title('Cloud9 AI Tactical Playbook')
    
    p_sections = [
        ('1. OPERATIONAL VULNERABILITIES', playbook.get('vulnerability')),
        ('2. RECOMMENDED ENGAGEMENT STRATEGY', playbook.get('killer_strategy')),
        ('3. TARGET THREAT ASSESSMENT', playbook.get('roster_threats')),
        ('4. EXECUTION TIMELINE', playbook.get('execution_plan'))
    ]

    for title, content in p_sections:
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(*pdf.primary_blue)
        pdf.cell(0, 8, title, 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(40, 40, 40)
        pdf.set_x(20)
        pdf.multi_cell(170, 6, clean_for_pdf(content))
        pdf.ln(6)

    return bytes(pdf.output())

def generate_comparison_pdf(team_a_name, team_b_name, res, stats_comp=None):
    """Generates a premium Side-by-Side Matchup Dossier."""
    pdf = PDFReport()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_page()
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, f'STRATEGIC COMPARISON: {team_a_name} VS {team_b_name}', 0, 1, 'C')

    # 1. ANALYTICS TABLE
    pdf.section_title('Comparative Tactical Analytics')
    if stats_comp:
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(0, 71, 171)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(50, 10, 'Tactical Metric', 1, 0, 'C', True)
        pdf.cell(60, 10, clean_for_pdf(team_a_name)[:25], 1, 0, 'C', True)
        pdf.cell(60, 10, clean_for_pdf(team_b_name)[:25], 1, 1, 'C', True)
        
        pdf.set_text_color(33, 37, 41)
        pdf.set_font('Arial', '', 10)
        metrics = ["Win Rate", "Series Played", "Average KDA", "Map Win %"]
        for m in metrics:
            pdf.set_x(20)
            pdf.cell(50, 8, m, 1, 0, 'L')
            pdf.cell(60, 8, str(stats_comp['team_a'].get(m, 'N/A')), 1, 0, 'C')
            pdf.cell(60, 8, str(stats_comp['team_b'].get(m, 'N/A')), 1, 1, 'C')
    
    # 2. AI ANALYSIS
    comp_sections = [
        ('Battle Verdict', res['verdict']),
        ('Roster War Breakdown', res['player_war']),
        ('Strategic Gap Analysis', res['gap'])
    ]
    for title, content in comp_sections:
        pdf.section_title(title)
        pdf.set_x(20)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(170, 7, clean_for_pdf(content))

    # 3. TARGET MATRIX
    pdf.section_title('Mission Priority Target Matrix')
    pdf.set_x(20)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(0, 71, 171)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 10, 'Alpha Attacker', 1, 0, 'C', True)
    pdf.cell(40, 10, 'Beta Target', 1, 0, 'C', True)
    pdf.cell(90, 10, 'Tactical Rationale', 1, 1, 'C', True)

    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(33, 37, 41)
    p_data = res.get('priority', '')
    for line in p_data.split('\n'):
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                pdf.set_x(20)
                pdf.cell(40, 8, parts[0][:18], 1, 0, 'C')
                pdf.cell(40, 8, parts[1][:18], 1, 0, 'C')
                pdf.cell(90, 8, clean_for_pdf(parts[2])[:58], 1, 1, 'L')

    # 4. STRATEGY
    pdf.section_title('Final Mission Strategy')
    pdf.set_x(20)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(170, 7, clean_for_pdf(res['strategy']))

    return bytes(pdf.output())

def generate_comparison_markdown(team_a, team_b, res):
    """Generates a clean MD report for comparison."""
    md = f"""# ⚔️ BATTLE ANALYSIS DOSSIER
## {team_a} VS {team_b}

### 🏆 BATTLE VERDICT
{res['verdict']}

### 🎯 PLAYER WAR
{res['player_war']}

### 📉 TACTICAL GAP
{res['gap']}

### 🎯 PRIORITY TARGET IDENTIFICATION
{res.get('priority', 'N/A')}

### ⚔️ KILLER MATCH STRATEGY
{res['strategy']}
"""
    return md
