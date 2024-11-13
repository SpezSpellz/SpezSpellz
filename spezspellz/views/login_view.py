"""Implement the login view"""
from allauth.account.views import LoginView


class CustomLoginView(LoginView):
    """Take the user login"""
    template_name = 'registration/login.html'

    def form_valid(self, form):
        """Validate the form"""
        return super().form_valid(form)
