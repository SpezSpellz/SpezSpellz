
from allauth.account.views import LoginView


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        return super().form_valid(form)