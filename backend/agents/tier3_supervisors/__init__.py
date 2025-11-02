"""
Tier 3 Supervisors - Team Lead Agents (20 instances)
Each supervises ~8-9 scanner agents (167 scanners / 20 leads)
"""

from .team_lead import TeamLead, get_team_lead_pool

__all__ = ["TeamLead", "get_team_lead_pool"]
