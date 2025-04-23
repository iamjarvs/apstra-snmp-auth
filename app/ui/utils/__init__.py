"""
UI utilities package initialization.
This allows the ui/utils directory to be imported as a Python package.
"""

from app.ui.utils.session_state import initialize_session_state, set_page_config

__all__ = [
    'initialize_session_state',
    'set_page_config'
]