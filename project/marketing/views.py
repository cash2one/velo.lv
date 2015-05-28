from braces.views import CsrfExemptMixin, SuperuserRequiredMixin
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView
import hashlib
import hmac
import logging
from core.models import Log
from marketing.models import SMS
from registration.models import Participant, Application


class SMSReportView(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        smsid = request.GET.get('smId')
        status = request.GET.get('status')

        sms = SMS.objects.filter(response=smsid).exclude(status="DELIVRD")
        if sms:
            sms.update(status=status)

        return HttpResponse('ok')


def mailgun_verify(api_key, token, timestamp, signature):
    return signature == hmac.new(
        key=api_key,
        msg='{}{}'.format(timestamp, token),
        digestmod=hashlib.sha256).hexdigest()


@csrf_exempt
def mailgun_webhook(request):
    if not mailgun_verify(settings.MAILGUN_ACCESS_KEY, request.POST.get('token'), request.POST.get('timestamp'), request.POST.get('signature')):
        return HttpResponse()
    event = Log.from_mailgun_request(request)
    return HttpResponse()



class TestEmailTemplate(SuperuserRequiredMixin, TemplateView):
    template_name = 'registration/email/rm2015/number_email.html'

    def get_context_data(self, **kwargs):
        context = super(TestEmailTemplate, self).get_context_data(**kwargs)
        participants = Participant.objects.filter(competition_id=47, slug="agris-ameriks-1987")

        participants = Application.objects.get(id=33728).participant_set.order_by('primary_number__number')

        primary_competition = participants[0].competition


        context.update({
            'participants': participants,
            'domain': settings.MY_DEFAULT_DOMAIN,
            'competition': primary_competition,
            'application': True,
        })

        return context
