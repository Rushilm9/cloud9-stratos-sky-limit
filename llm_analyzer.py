import json
import os
import re
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
import streamlit as st
load_dotenv(override=True)

def get_env(key):
    # 1. Try Streamlit Secrets (for Cloud deployment)
    try:
        if key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # 2. Try OS Environment (Local .env)
    val = os.getenv(key)
    if val: return val.strip().strip("'").strip('"')
    return val

def get_llm():
    """Initializes the LLM only when needed to prevent startup crashes."""
    key = get_env("AZURE_OPENAI_KEY")
    endpoint = get_env("AZURE_OPENAI_ENDPOINT")
    deployment = get_env("AZURE_OPENAI_DEPLOYMENT")
    version = get_env("AZURE_OPENAI_VERSION")
    
    if not (key and endpoint and deployment):
        return None

    return AzureChatOpenAI(
        api_key=key,
        azure_endpoint=endpoint,
        deployment_name=deployment,
        api_version=version or "2024-02-15-preview",
        temperature=0.2
    )

def extract_section(text, tag):
    """Robustly extracts text between [[TAG]] and [[/TAG]]."""
    pattern = rf"\[\[{tag}\]\](.*?)\[\[/{tag}\]\]"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else f"No {tag} data available."

def generate_scouting_report(team_name, raw_data_dict):
    """
    Uses a hybrid approach:
    - Custom Tags for long tactical text (avoids JSON parsing errors).
    - JSON for short structured UI stats.
    """
    if not raw_data_dict or not raw_data_dict.get("series"):
        return {
            "vulnerability": "Insufficient signal captured.",
            "roster_threats": "Roster scanning incomplete.",
            "killer_strategy": "Maintain standard SOP.",
            "execution_plan": "Gather more intelligence."
        }, [], "Patterns inconsistent.", "Awaiting more data."

    data_str = json.dumps(raw_data_dict, indent=2)
    
    # --- PIPELINE 1: TACTICAL PLAYBOOK (TAGGED) ---
    playbook_prompt = f"""
You are a Lead Strategic Analyst. Produce a CLINICAL TACTICAL PLAYBOOK for {team_name}.
DATA: {data_str}

Wrap your analysis in these SPECIFIC TAGS:
[[VULNERABILITY]]
Markdown text about losses and blue/red side weakness.
[[/VULNERABILITY]]

[[THREATS]]
Markdown text about star players and failure points.
[[/THREATS]]

[[STRATEGY]]
3 SPECIFIC actionable directives.
[[/STRATEGY]]

[[PLAN]]
Phase-by-phase execution timeline.
[[/PLAN]]

STRICT RULES:
- Use bullet points.
- NO headers like '### 1.' inside the tags.
- NO JSON. Just tags and markdown.
"""

    # --- PIPELINE 2: STRUCTURED INTEL (JSON) ---
    intel_prompt = f"""
Extract UI metadata for {team_name} based on this data: {data_str}

Return ONLY a valid JSON object:
{{
  "roster_analysis": [
    {{
      "name": "PLAYER_NAME",
      "category": "Killer" | "Attacker" | "Defender",
      "strength": "Brief strength",
      "weakness": "Brief weakness"
    }}
  ],
  "winning_trends": "1-sentence summary of why they win.",
  "counter_strategy": "1-sentence actionable strategy for US to win against them."
}}
IMPORTANT: Raw JSON only. No text.
"""

    try:
        llm = get_llm()
        if not llm:
            raise ValueError("LLM Credentials Missing")

        # Execute Tactical Pipeline (Tag-based, virtually uncrashable)
        playbook_res = llm.invoke([HumanMessage(content=playbook_prompt)]).content
        playbook_sections = {
            "vulnerability": extract_section(playbook_res, "VULNERABILITY"),
            "roster_threats": extract_section(playbook_res, "THREATS"),
            "killer_strategy": extract_section(playbook_res, "STRATEGY"),
            "execution_plan": extract_section(playbook_res, "PLAN")
        }
        
        # Execute Intel Pipeline (JSON-based, for short data)
        intel_res = llm.invoke([HumanMessage(content=intel_prompt)]).content
        clean_intel = re.sub(r'```json|```', '', intel_res).strip()
        
        try:
            parsed_intel = json.loads(clean_intel)
            structured_roster = parsed_intel.get("roster_analysis", [])
            winning_trends = parsed_intel.get("winning_trends", "Patterns inconsistent.")
            counter_strategy = parsed_intel.get("counter_strategy", "Strategy undefined.")
        except Exception as e:
            winning_match = re.search(r'"winning_trends":\s*"(.*?)"', clean_intel)
            counter_match = re.search(r'"counter_strategy":\s*"(.*?)"', clean_intel)
            winning_trends = winning_match.group(1) if winning_match else "Analyzing winning patterns..."
            counter_strategy = counter_match.group(1) if counter_match else "Formulating strategy..."
            
            # Simple fallback for roster if JSON fails
            structured_roster = []
            roster_matches = re.finditer(r'"name":\s*"(.*?)".*?"strength":\s*"(.*?)".*?"weakness":\s*"(.*?)"', clean_intel, re.DOTALL)
            for rm in roster_matches:
                structured_roster.append({
                    "name": rm.group(1),
                    "category": "Combatant",
                    "strength": rm.group(2),
                    "weakness": rm.group(3)
                })

        return playbook_sections, structured_roster, winning_trends, counter_strategy

    except Exception as e:
        fallback_playbook = {
            "vulnerability": "Extraction failure.",
            "roster_threats": "Metadata error.",
            "killer_strategy": "Check logs.",
            "execution_plan": "System restart required."
        }
        return fallback_playbook, [], "Error", "Error"

def generate_comparison_report(team_a_name, team_a_data, team_b_name, team_b_data):
    """
    Generates a high-fidelity, sectional comparison report.
    """
    comp_data = {
        "team_a": {"name": team_a_name, "stats": team_a_data},
        "team_b": {"name": team_b_name, "stats": team_b_data}
    }
    data_str = json.dumps(comp_data, indent=2)

    prompt = f"""
You are a World-Class Esports Analyst. Compare {team_a_name} vs {team_b_name}.
DATA: {data_str}

Return a sectional analysis using these EXACT tags:

[[MATCHUP_VERDICT]]
A clinical decision on who wins and % confidence. 1 sentence reason.
[[/MATCHUP_VERDICT]]

[[PLAYER_WAR]]
Identify the 'Best Player' on both sides and explain the 1v1 battle that defines the game.
[[/PLAYER_WAR]]

[[TACTICAL_GAP]]
Identify one specific side-lane or objective gap where Team A beats Team B or vice versa.
[[/TACTICAL_GAP]]

[[PRIORITY_TARGETS]]
Provide exactly two lines (one for each team's perspective) in this format:
TEAM_NAME_WHO_IS_ATTACKING | TARGET_PLAYER_ON_OTHER_TEAM | STRATEGIC_REASON_FOR_TARGETING
[[/PRIORITY_TARGETS]]

[[KILL_STRATEGY]]
A 2-point actionable strategy for BOTH teams to win this specific match.
[[/KILL_STRATEGY]]

STRICT RULES:
- Clinical tone.
- Markdown bullets.
- NO high-level headers inside tags.
"""

    try:
        llm = get_llm()
        if not llm:
            return { "verdict": "OpenAI Credentials Missing on Server.", "player_war": "N/A", "gap": "N/A", "priority": "N/A", "strategy": "N/A" }
            
        response = llm.invoke([HumanMessage(content=prompt)]).content
        return {
            "verdict": extract_section(response, "MATCHUP_VERDICT"),
            "player_war": extract_section(response, "PLAYER_WAR"),
            "gap": extract_section(response, "TACTICAL_GAP"),
            "priority": extract_section(response, "PRIORITY_TARGETS"),
            "strategy": extract_section(response, "KILL_STRATEGY")
        }
    except Exception as e:
        return {
            "verdict": "Combat data mismatch.",
            "player_war": "Intel unreliable.",
            "gap": "Analysis aborted.",
            "strategy": "Proceed with extreme caution."
        }
