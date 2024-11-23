"""Implements the register page."""
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView


class RegisterView(CreateView):
    """View for registration/signup."""

    form_class = UserCreationForm

    def get_success_url(self):
        """Redirect user to this url after a successful registration."""

        next_url = self.request.GET.get('next')
        if next_url:
            # Resolve the URL to avoid invalid redirection
            login_url = reverse_lazy("login")
            return f"{login_url}?{urlencode({'next': next_url})}"
        return reverse_lazy("login")  # Default fallback URL

    template_name = "registration/register.html"
