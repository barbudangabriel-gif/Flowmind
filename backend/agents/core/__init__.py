"""
FlowMind CORE ENGINE - Agent System Core Components

This package contains the foundational infrastructure for the 200-agent hierarchical system:
- Data Layer: Redis Streams, TimeSeries, caching
- WebSocket Manager: Real-time frontend updates
- News Aggregator: Multi-source news intelligence

Author: FlowMind Team
Created: November 2, 2025
"""

from .data_layer import (
    RedisStreamsManager,
    RedisTimeSeriesManager,
    get_data_layer,
)

__all__ = [
    "RedisStreamsManager",
    "RedisTimeSeriesManager",
    "get_data_layer",
]
