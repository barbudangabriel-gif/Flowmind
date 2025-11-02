"""
Tier 2 Validators - Sector Head Agents (10 instances)
Each supervises 2 team leads (20 team leads / 10 sectors)
"""

from .sector_head import SectorHead, get_sector_head_pool

__all__ = ["SectorHead", "get_sector_head_pool"]
