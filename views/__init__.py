# Lazy imports to avoid circular dependencies
def render_startpage():
    from .startpage import render_startpage as _render_startpage
    return _render_startpage()

def render_homepage():
    from .homepage import render_homepage as _render_homepage
    return _render_homepage()

__all__ = ["render_startpage", "render_homepage"]
