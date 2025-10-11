# Lazy imports to avoid circular dependencies
def show_startpage():
    from .startpage import show_startpage as _show_startpage
    return _show_startpage()

def show_homepage():
    from .homepage import show_homepage as _show_homepage
    return _show_homepage()

__all__ = ["show_startpage", "show_homepage"]
