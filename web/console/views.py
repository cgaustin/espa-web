import time

from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.edit import FormView

from forms import StatusMessageForm
from ordering.models.configuration import Configuration

from reports import stats

class Index(View):
    template = 'console/index.html'

    def get(self, request, *args, **kwargs):

        user = User.objects.get(username=request.user.username)

        if not user.is_staff:
            return HttpResponseRedirect(reverse('login'))

        ctx = {}
        
        listing = stats.listing()

        for key, value in listing.iteritems():
            stat = stats.get(key)
            ctx[value['display_name']] = {
                'description': value['description'],
                'statistic': stat
            }
        
        
        return render(request=request,
                      template=self.template,
                      context={'stats': ctx})

class StatusMessage(SuccessMessageMixin, FormView):
    template_name = 'console/statusmsg.html'
    form_class = StatusMessageForm
    success_url = 'statusmsg'
    success_message = 'Status message updated'

    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        if not user.is_staff:
            return HttpResponseRedirect(reverse('login'))

        return super(StatusMessage, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        if not user.is_staff:
            return HttpResponseRedirect(reverse('login'))

        return super(StatusMessage, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatusMessage, self).get_context_data(**kwargs)

        try:
            update_date = Configuration.get('msg.system_message_updated_date')
            context['update_date'] = update_date
        except Configuration.DoesNotExist:
            context['update_date'] = 'n/a'

        try:
            updated_by = Configuration.get('msg.system_message_updated_by')
            context['updated_by'] = updated_by
        except Configuration.DoesNotExist:
            context['updated_by'] = 'n/a'

        return context


    def get_initial(self):
        return_data = {}
        try:
            title = Configuration.get('msg.system_message_title')
            return_data['title'] = title
        except Configuration.DoesNotExist:
            return_data['title'] = ''

        try:
            message = Configuration.get('msg.system_message_body')
            return_data['message'] = message
        except Configuration.DoesNotExist:
            return_data['message'] = ''

        try:
            display = Configuration.get('system.display_system_message')
            if display.lower() == 'true':
                return_data['display'] = True
            else:
                return_data['display'] = False
        except Configuration.DoesNotExist:
            return_data['display'] = False

        return return_data



    def form_valid(self, form):
        title, created = Configuration.objects.get_or_create(key="msg.system_message_title")
        title.value = form.cleaned_data['title']
        title.save()

        message, created = Configuration.objects.get_or_create(key="msg.system_message_body")
        message.value = form.cleaned_data['message']
        message.save()

        display, created = Configuration.objects.get_or_create(key="system.display_system_message")
        display.value = form.cleaned_data['display']
        display.save()

        date_updated, created = Configuration.objects.get_or_create(key="msg.system_message_updated_date")
        date_updated.value = time.strftime('%a %b %d %Y %X')
        date_updated.save()

        username, created = Configuration.objects.get_or_create(key="msg.system_message_updated_by")
        username.value = self.request.user.username
        username.save()
        
        return super(StatusMessage, self).form_valid(form)
