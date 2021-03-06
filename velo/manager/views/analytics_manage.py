from django.db.models import Count, F

from velo.manager.tables import ManageParticipantTable, ManageResultNonParticipantTable, ManageFindNumberViewTable, \
    ManageApplicationTable, HelperResultsMatchViewTable
from velo.manager.tables.tables import ManageParticipantDifferSlugTable, ManageParticipantToNumberTable
from velo.manager.views.permission_view import ManagerPermissionMixin
from velo.registration.models import Participant, Number, Application
from velo.results.models import Result, HelperResults
from velo.velo.mixins.views import SingleTableViewWithRequest

__all__ = [
    'MultipleSameSlugView', 'MultipleNumbersView', 'ResultAssignedToInactiveParticipant', 'DifferNumberSlugView',
    'MatchParticipantToNumberView', 'FindNumberView', 'PayedAmountNotEqualView', 'MatchResultParticipantView'
]


class PayedAmountNotEqualView(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Application
    table_class = ManageApplicationTable
    template_name = 'bootstrap/manager/table.html'
    table_pagination = False

    def get_queryset(self):
        queryset = super(PayedAmountNotEqualView, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        queryset = queryset.extra(
            # select={
            #     'participant_payment_sum': "Select sum(pp.final_price) from registration_participant pp where pp.application_id = registration_application.id",
            #     'payment_amount': 'Select ppp2.total from payment_payment ppp2 where ppp2.object_id=registration_application.id and ppp2.content_type_id=19 and ppp2.status=30 Limit 1'},
            where=[
                "(Select sum(pp.final_price) from registration_participant pp where pp.application_id = registration_application.id) != (Select max(ppp2.total) from payment_payment ppp2 where ppp2.object_id=registration_application.id and ppp2.content_type_id=19 and ppp2.status=30 Limit 1)"],
        )

        # queryset = queryset.values("competition", "payment_status", "discount_code", "email", "external_invoice_nr", "participant_payment_sum", "payment_amount")

        return queryset


class MultipleSameSlugView(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Participant
    table_class = ManageParticipantTable
    template_name = 'bootstrap/manager/table.html'

    def get_queryset(self):
        double_participants = Participant.objects.filter(is_participating=True,
                                                         competition_id__in=self.competition.get_ids()).order_by('slug',
                                                                                                                 'distance').values(
            'slug').annotate(c=Count('id')).filter(c__gt=1).values('slug')
        slugs = [slug.get('slug') for slug in double_participants]

        queryset = super(MultipleSameSlugView, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids(), slug__in=slugs)
        queryset = queryset.select_related('distance')
        return queryset


# Not used
class DifferNumberSlugView(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Participant
    table_class = ManageParticipantDifferSlugTable
    template_name = 'bootstrap/manager/table.html'

    def get_queryset(self):
        child_ids = [competition.id for competition in self.competition.parent.get_children()] + [
            self.competition.parent.id, ]

        queryset = super(DifferNumberSlugView, self).get_queryset()
        queryset = queryset.filter(competition_id__in=child_ids, is_participating=True)
        queryset = queryset.exclude(primary_number__participant_slug=F('slug'))
        queryset = queryset.exclude(primary_number=None)

        queryset = queryset.select_related('distance', 'primary_number')
        return queryset


class MatchParticipantToNumberView(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Number
    table_class = ManageParticipantToNumberTable
    template_name = 'bootstrap/manager/table.html'

    def get_queryset(self):
        queryset = super(MatchParticipantToNumberView, self).get_queryset()
        queryset = queryset.exclude(participant_slug='')
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())
        queryset = queryset.exclude(participant_slug=F('participant__slug'))
        queryset = queryset.values('id', 'number', 'participant_slug', 'group', 'participant__slug',
                                   'participant__first_name', 'participant__last_name', 'participant__id')
        return queryset


class MultipleNumbersView(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Participant
    table_class = ManageParticipantTable
    template_name = 'bootstrap/manager/table.html'

    def get_queryset(self):
        multiple_numbers = Number.objects.filter(competition_id__in=self.competition.get_ids()).exclude(
            participant_slug='').order_by('distance', 'group', 'participant_slug').values('participant_slug').annotate(
            c=Count('id')).filter(c__gt=1)

        slugs = [slug.get('participant_slug') for slug in multiple_numbers]

        queryset = super(MultipleNumbersView, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids(), slug__in=slugs, is_participating=True)
        queryset = queryset.select_related('distance')
        return queryset


class ResultAssignedToInactiveParticipant(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Result
    table_class = ManageResultNonParticipantTable
    template_name = 'bootstrap/manager/table.html'

    def get_queryset(self):
        queryset = super(ResultAssignedToInactiveParticipant, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())
        queryset = queryset.filter(participant__is_participating=False)
        queryset = queryset.select_related('participant__distance', 'competition', 'participant')
        return queryset


class FindNumberView(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Participant
    table_class = ManageFindNumberViewTable
    template_name = 'bootstrap/manager/table.html'

    def get_queryset(self):
        queryset = super(FindNumberView, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids(), is_participating=True,
                                   primary_number=None)
        queryset = queryset.select_related('distance', 'competition')
        return queryset


class MatchResultParticipantView(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = HelperResults
    table_class = HelperResultsMatchViewTable
    template_name = 'bootstrap/manager/table.html'

    def get_queryset(self):
        queryset = super(MatchResultParticipantView, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids()).exclude(matches_slug='')

        queryset = queryset.select_related('competition', 'participant')
        return queryset
