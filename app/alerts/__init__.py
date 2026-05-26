"""Alert detection for the portfolio. Checks thresholds and returns alert dicts."""
from app.alerts.thresholds import check_all_alerts

__all__ = ["check_all_alerts"]
