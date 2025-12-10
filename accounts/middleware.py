from django.shortcuts import redirect
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

class LoginRequiredMiddleware:
    """
    - Allows only HOME, LOGIN, and ADMIN LOGIN pages without authentication.
    - Blocks all other routes including /admin/* unless logged in.
    """
    def __init__(self, get_response):
        self.get_response = get_response

        self.exempt_urls = []

        # USER LOGIN
        try:
            self.login_url = reverse("accounts:login")
            self.exempt_urls.append(self.login_url)
        except NoReverseMatch:
            self.login_url = "/accounts/login/"

        # HOME URL
        try:
            self.home_url = reverse("home")
            self.exempt_urls.append(self.home_url)
        except NoReverseMatch:
            self.home_url = "/"

        # ADMIN LOGIN PAGE (must be allowed)
        self.admin_login_url = "/admin/login/"
        self.exempt_urls.append(self.admin_login_url)

    def __call__(self, request):
        path = request.path

        # If user is authenticated → allow everything
        if request.user.is_authenticated:
            return self.get_response(request)

        # Allow only the pages added in exempt_urls
        if path in self.exempt_urls:
            return self.get_response(request)

        # Block everything else → redirect to login page
        return redirect(self.login_url)
