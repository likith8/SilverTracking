"""
URL configuration for silvertrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .frontend_views import serve_react_app
from accounts.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    # Serve frontend assets FIRST (before other routes)
    # This must be early to avoid middleware redirects
]

# Serve static files and frontend assets during development
if settings.DEBUG:
    from django.views.static import serve
    from pathlib import Path
    frontend_dist = Path(settings.BASE_DIR.parent) / "frontend" / "dist"
    if frontend_dist.exists():
        # Serve frontend assets at /assets/ path - must be before other patterns
        def serve_frontend_assets(request, path):
            return serve(request, path, document_root=str(frontend_dist / 'assets'))
        urlpatterns.insert(0, re_path(r'^assets/(?P<path>.*)$', serve_frontend_assets))
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add other URL patterns
urlpatterns += [
    # Django template views (for backward compatibility)
    path("accounts/", include("accounts.urls")),
    path('customers/', include('customers.urls', namespace='customers')),
    path('products/', include('products.urls', namespace='products')),
    path('transactions/', include('transactions.urls', namespace='transactions')),
    # API routes for frontend (same views, accessible via /api/ prefix)
    # Note: Namespace warnings are expected but won't affect functionality
    path('api/accounts/', include("accounts.urls")),
    path('api/customers/', include('customers.urls')),
    path('api/products/', include('products.urls')),
    path('api/transactions/', include('transactions.urls')),
    # Serve React app at root (for middleware compatibility, keep home name)
    path('', home, name='home'), 
    # Serve React app - catch-all route for all other paths (React Router)
    # This regex excludes admin, api, static, media, assets, and Django template paths
    re_path(r'^(?!admin|api|static|media|assets|accounts|customers|products|transactions).*$', serve_react_app, name='react_app'),
]
