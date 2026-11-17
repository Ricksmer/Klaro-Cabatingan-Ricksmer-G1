from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*roles):
    """Login required, and the user's role must be one of `roles`.
    Wrong role: send them back to their own dashboard."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, "You don't have access to that page.")
                return redirect(request.user.get_dashboard_url())
            return view_func(request, *args, **kwargs)
        return login_required(_wrapped)
    return decorator