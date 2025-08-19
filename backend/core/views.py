from django.conf import settings
from django.views.generic import TemplateView

class AppView(TemplateView):
    """
    Serves the base SPA shell. React mounts into #root.
    """
    template_name = "index.html"  # or "base/2017_design.html" if you prefer

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Public, non-secret values ONLY (safe to render into HTML)
        ctx.update({
            "APP_VERSION": getattr(settings, "APP_VERSION", ""),
            "DEV_MODE": getattr(settings, "DEV_MODE", False),
            # Useful extras
            "API_BASE_URL": getattr(settings, "API_BASE_URL", "/api"),
            "APP_ENV": getattr(settings, "APP_ENV", "dev"),
        })
        return ctx
