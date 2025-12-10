"""
Views for serving the React frontend application.
"""
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from pathlib import Path
import os


@never_cache
def serve_react_app(request):
    """
    Serve the React app's index.html file.
    This view is used as a catch-all for React Router.
    """
    frontend_build_path = Path(settings.BASE_DIR.parent) / "frontend" / "dist" / "index.html"
    
    # If build doesn't exist, return a helpful message
    if not frontend_build_path.exists():
        return HttpResponse(
            """
            <html>
                <head><title>Frontend Not Built</title></head>
                <body>
                    <h1>Frontend Not Built</h1>
                    <p>Please build the frontend first:</p>
                    <pre>cd frontend && npm run build</pre>
                    <p>Or run the development server:</p>
                    <pre>cd frontend && npm run dev</pre>
                </body>
            </html>
            """,
            content_type="text/html; charset=utf-8"
        )
    
    # Read and return the index.html with proper headers
    try:
        with open(frontend_build_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Verify it's the React app HTML (should contain <div id="root">)
            if '<div id="root">' not in content:
                return HttpResponse(
                    f"""
                    <html>
                        <head><title>Error</title></head>
                        <body>
                            <h1>Error: React app HTML not found</h1>
                            <p>File exists but doesn't contain React app structure.</p>
                            <p>Path: {frontend_build_path}</p>
                            <p>File size: {len(content)} bytes</p>
                            <p>First 200 chars: {content[:200]}</p>
                        </body>
                    </html>
                    """,
                    content_type="text/html; charset=utf-8"
                )
            
            response = HttpResponse(content, content_type="text/html; charset=utf-8")
            # Add cache-control headers to prevent caching - VERY AGGRESSIVE
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Content-Type-Options'] = 'nosniff'
            # Add a header to identify this as React app
            response['X-Served-By'] = 'React-App'
            return response
    except Exception as e:
        return HttpResponse(
            f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Error serving React app</h1>
                    <p>Error: {str(e)}</p>
                    <p>Path: {frontend_build_path}</p>
                </body>
            </html>
            """,
            content_type="text/html; charset=utf-8"
        )

