"""
Tier 1 Director - Master Decision Authority (1 instance)
Final validation with GPT-4o LLM reasoning
"""

from .master_director import MasterDirector, get_master_director

__all__ = ["MasterDirector", "get_master_director"]
