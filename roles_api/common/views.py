from django.contrib.auth.mixins import UserPassesTestMixin


class TitleMixin():
    tittle = None

    def get_context_data(self, **kwargs):
        context = super(TitleMixin, self).get_context_data(**kwargs)
        context['title'] = self.tittle
        return context
