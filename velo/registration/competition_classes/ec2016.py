import datetime
from django.db import connection
from sitetree.utils import item

from velo.core.models import Log
from velo.registration.competition_classes.base import CompetitionScriptBase
from velo.registration.models import Application, Participant
from django import forms
from django.utils.translation import ugettext_lazy as _, activate
from velo.registration.tables import ParticipantTableWCountry
from velo.results.models import HelperResults, ChipScan, DistanceAdmin, Result, LapResult
from velo.results.tables import ResultRMGroupTable, ResultXCODistanceCheckpointTable
from velo.results.tasks import create_result_sms, recalculate_standing_for_result


class EC2016(CompetitionScriptBase):
    SPORTA_DISTANCE_ID = 48
    competition_index = 1

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M Elite', 'W Elite', ),
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 351, 'group': ''}, ],
        }

    def result_select_extra(self, distance_id):
        return {
            'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
            'l2': 'SELECT time FROM results_lapresult l2 WHERE l2.result_id = results_result.id and l2.index=2',
            'l3': 'SELECT time FROM results_lapresult l3 WHERE l3.result_id = results_result.id and l3.index=3',
            'l4': 'SELECT time FROM results_lapresult l4 WHERE l4.result_id = results_result.id and l4.index=4',
        }


    def get_startlist_table_class(self, distance=None):
        return ParticipantTableWCountry

    def _update_year(self, year):
        return year + 2

    def assign_group(self, distance_id, gender, birthday, participant=None):
        if gender == 'M':
            return 'M Elite'
        else:
            return 'W Elite'

    def payment_additional_checkboxes(self, application_id=None, application=None):
        if not application:
            application = Application.objects.get(id=application_id)

        if application.participant_set.filter(distance_id=self.SPORTA_DISTANCE_ID):
            return (('sport_approval', forms.BooleanField(label=_("I am informed that participation in UEC MTB Marathon requires licence. More info in Technical Guide."), required=True)), )

        return ()

    def create_helper_results(self, participants):

        for participant in participants:
            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant)

    def recalculate_all_standings(self):
        pass

    def process_chip_result(self, chip_id, sendsms=True, recalc=False):
        """
        Function processes chip result and recalculates all standings
        """
        chip = ChipScan.objects.get(id=chip_id)
        distance_admin = DistanceAdmin.objects.get(competition=chip.competition, distance=chip.nr.distance)

        zero_minus_10secs = (
        datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.timedelta(
            seconds=10)).time()
        if chip.time < zero_minus_10secs:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip scanned before start")
            return False

        if chip.nr.number > 350:  # Skip all results that have number > 300 those are from public ride.
            return False

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0, 0, 0))
        result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta).time()

        result_time_5back = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta - datetime.timedelta(minutes=5)).time()
        if result_time_5back > result_time:
            result_time_5back = datetime.time(0,0,0)
        result_time_5forw = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta + datetime.timedelta(minutes=5)).time()

        seconds = result_time.hour * 60 * 60 + result_time.minute * 60 + result_time.second

        # Do not process if finished in 10 minutes.
        if seconds < 10 * 60 or chip.time < distance_admin.zero: # 10 minutes
            Log.objects.create(content_object=chip, action="Chip process", message="Chip result less than 10 minutes. Ignoring.")
            return None

        if chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None

        participant = Participant.objects.get(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_ids(), distance=chip.nr.distance, is_participating=True)

        if participant.gender == 'F':
            result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta - datetime.timedelta(seconds=15*60 + 10)).time()

            result_time_5back = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta - datetime.timedelta(seconds=15*60 + 10) - datetime.timedelta(minutes=5)).time()
            if result_time_5back > result_time:
                result_time_5back = datetime.time(0,0,0)
            result_time_5forw = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta - datetime.timedelta(seconds=15*60 + 10) + datetime.timedelta(minutes=5)).time()


        participant_in_seb = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=(54, 51), distance_id=49, is_participating=True)
        result = result_seb = None
        m18 = False
        hidden_result = False
        if participant_in_seb:
            result_seb, created = Result.objects.get_or_create(competition_id=54, number=chip.nr, participant=participant_in_seb[0])
            if result_seb.participant.group == 'M-18':
                result = result_seb
                m18 = True
            if not participant.is_competing:
                hidden_result = True
                result = result_seb

        if not result:
            result, created = Result.objects.get_or_create(competition=chip.competition, number=chip.nr, participant=participant)

        already_exists_result = LapResult.objects.filter(result=result, time__gte=result_time_5back,
                                                         time__lte=result_time_5forw)

        if already_exists_result:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip double scanned.")
        elif result.time:
            Log.objects.create(content_object=chip, action="Chip process", message="Result already set.")
        else:
            if m18:
                m18_final_result = result_seb.lapresult_set.create(index=0, time=result_time)
                # There are no splits for those participants as they are riding public ride with sport numbers.
            elif participant.gender == 'M':
                if chip.url_sync.kind == 'FINISH':
                    split1 = result.lapresult_set.filter(index=2)
                    split2 = result.lapresult_set.filter(index=4)
                    split3 = result.lapresult_set.filter(index=5)

                    if not split1:
                        result.lapresult_set.create(index=2, time=result_time)
                        if result_seb and not hidden_result:
                            result_seb.lapresult_set.create(index=2, time=result_time)
                    elif not split2:
                        result.lapresult_set.create(index=4, time=result_time)
                        if result_seb and not hidden_result:
                            result_seb.lapresult_set.create(index=4, time=result_time)
                    elif not split3:
                        result.lapresult_set.create(index=5, time=result_time)
                        if result_seb and not hidden_result:
                            result_seb.lapresult_set.create(index=5, time=result_time)
                else:
                    split1 = result.lapresult_set.filter(index=1)
                    split2 = result.lapresult_set.filter(index=3)

                    if not split1:
                        result.lapresult_set.create(index=1, time=result_time)
                        if result_seb and not hidden_result:
                            result_seb.lapresult_set.create(index=1, time=result_time)
                    elif not split2:
                        result.lapresult_set.create(index=3, time=result_time)
                        if result_seb and not hidden_result:
                            result_seb.lapresult_set.create(index=3, time=result_time)
            else:
                # WOMEN
                if chip.url_sync.kind == 'FINISH':
                    split1 = result.lapresult_set.filter(index=2)
                    split2 = result.lapresult_set.filter(index=5)

                    if not split1:
                        result.lapresult_set.create(index=2, time=result_time)
                        if result_seb and not hidden_result:
                            result_seb.lapresult_set.create(index=2, time=result_time)
                    elif not split2:
                        result.lapresult_set.create(index=5, time=result_time)
                        if result_seb and not hidden_result:
                            result_seb.lapresult_set.create(index=5, time=result_time)

                else:
                    split1 = result.lapresult_set.filter(index=1)

                    if not split1:
                        result.lapresult_set.create(index=1, time=result_time)
                        if result_seb and not hidden_result:
                            result_seb.lapresult_set.create(index=1, time=result_time)

            # FINAL RESULT CALC:
            if m18:
                final_result = [m18_final_result, ]  # final_result is already set above.
            else:
                final_result = result.lapresult_set.filter(index=5)

            if final_result:
                final_result = final_result[0]
                Log.objects.create(content_object=chip, action="Chip process",
                                   message="DONE. Lets assign avg speed.")
                if not m18 and not hidden_result:
                    if not result.time:
                        result.time = final_result.time
                    result.set_avg_speed()
                    result.save()
                    self.assign_standing_places()

                if result_seb:
                    if not result_seb.time:
                        result_seb.time = final_result.time
                    result_seb.set_all()
                    result_seb.save()

                    recalculate_standing_for_result.delay(54, result_seb.id)

                    # Recalculate standing places in SEB also.
                    from .seb2016 import Seb2016
                    _class = Seb2016(competition_id=54)
                    _class.assign_result_place()

                if not m18: # We will not send to m-18, because results will not be correct.
                    if participant.is_competing and self.competition.competition_date == datetime.date.today() and sendsms:
                        create_result_sms.apply_async(args=[result.id, ], countdown=240)

        chip.is_processed = True
        chip.save()

        print(chip)

    def assign_standing_places(self):
        self.assign_result_place()
        self.reset_cache_results()

    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            return ResultXCODistanceCheckpointTable

    def build_menu(self, lang):
        activate(lang)
        current_date = datetime.date.today()
        child_items = [
            item(_('Start List'), 'competition:participant_list %i' % self.competition.id),
            item(_("Maps"), 'competition:maps %i' % self.competition.id),
        ]
        self.build_flat_pages(self.competition, child_items, lang)

        if self.competition.competition_date <= current_date + datetime.timedelta(days=1):
            child_items.append(item(_("Results"), 'competition:result_distance_list %i' % self.competition.id))

        return item(str(self.competition), 'competition:competition %i' % self.competition.id, url_as_pattern=True, children=child_items, in_menu=self.competition.is_in_menu)

    def build_manager_menu(self):
        return item(str(self.competition), 'manager:competition %i' % self.competition.id,
                    in_menu=self.competition.is_in_menu, access_loggedin=True)

    def setup(self):

        counter = 0
        seb_toyota_pp = Participant.objects.filter(is_participating=True, competition_id__in=(54, 51), distance_id=49)
        for p in seb_toyota_pp:
            ec_pp = Participant.objects.filter(is_participating=True, competition_id=66, distance_id=48, slug=p.slug)
            if not ec_pp:
                Participant.objects.create(competition_id=66, distance_id=48, team_name=p.team_name,
                                           is_participating=p.is_participating, is_competing=False,
                                           first_name=p.first_name, last_name=p.last_name, birthday=p.birthday,
                                           slug=p.slug, gender=p.gender, ssn=p.ssn, phone_number=p.phone_number,
                                           email=p.email, send_email=p.send_email, send_sms=p.send_sms,
                                           country=p.country, city=p.city, bike_brand2=p.bike_brand2, )
                print(p)
                counter += 1

        ec_pp = Participant.objects.filter(is_participating=True, competition_id=66, distance_id=48, is_competing=False)
        for p in ec_pp:
            toy = Participant.objects.filter(is_participating=True, competition_id__in=(54, 51), distance_id=49, slug=p.slug)
            if toy:
                hp = HelperResults.objects.get(participant=toy[0], competition_id=54)
                HelperResults.objects.filter(participant=p, competition_id=66).update(calculated_total=hp.calculated_total)

        from velo.results.models import Result
        import datetime
        # FIX Women results.
        all_results = Result.objects.filter(competition_id__in=[66, 54], number__distance_id=48, participant__gender='F')
        for r in all_results:
            if r.time:
                r.time = (datetime.datetime.combine(datetime.date.today(), r.time) - datetime.timedelta(seconds=15 * 60 + 10)).time()
                r.save()
            for l in r.lapresult_set.all():
                l.time = (datetime.datetime.combine(datetime.date.today(), l.time) - datetime.timedelta(seconds=15 * 60 + 10)).time()
                l.save()

    def assign_result_place(self):
        """
        Assign result place based on result time. Optimized to use raw SQL.
        """
        cursor = connection.cursor()

        # First assign distance place
        cursor.execute("""
        UPDATE
            results_result r
        SET
            result_distance = res2.distance_row_nr,
            result_group = res2.group_row_nr
        FROM
        (
        Select res.id, result_distance, res.competition_id, res.time, p.is_competing, p.last_name,
        row_number() OVER (PARTITION BY nr.distance_id ORDER BY nr.distance_id, res.status, res.time) as distance_row_nr,
        row_number() OVER (PARTITION BY nr.distance_id, p.group ORDER BY nr.distance_id, p.group, res.status, res.time) as group_row_nr
        FROM results_result As res
        INNER JOIN registration_number nr ON res.number_id = nr.id
        INNER JOIN registration_participant p ON res.participant_id = p.id
        WHERE p.is_competing is true and res.time IS NOT NULL and p.group = 'M Elite' and res.competition_id=%s
        ) res2
        WHERE res2.competition_id = %s and res2.time IS NOT NULL and res2.is_competing is true
        AND r.id = res2.id
        """, [self.competition_id, self.competition_id, ])

        cursor.execute("""
        UPDATE
            results_result r
        SET
            result_distance = res2.distance_row_nr,
            result_group = res2.group_row_nr
        FROM
        (
            Select res.id, result_distance, res.competition_id, res.time, p.is_competing, p.last_name,
            row_number() OVER (PARTITION BY nr.distance_id ORDER BY nr.distance_id, res.status, res.time) as distance_row_nr,
            row_number() OVER (PARTITION BY nr.distance_id, p.group ORDER BY nr.distance_id, p.group, res.status, res.time) as group_row_nr
            FROM results_result As res
            INNER JOIN registration_number nr ON res.number_id = nr.id
            INNER JOIN registration_participant p ON res.participant_id = p.id
            WHERE p.is_competing is true and res.time IS NOT NULL and p.group = 'W Elite' and res.competition_id=%s
        ) res2
        WHERE res2.competition_id = %s and res2.time IS NOT NULL and res2.is_competing is true
        AND r.id = res2.id
        """, [self.competition_id, self.competition_id, ])


        # Then unset places to others
        cursor.execute("""
        UPDATE
            results_result r
        SET
            result_distance = NULL,
            result_group = NULL
        FROM
        (
        Select res.id, result_distance, res.competition_id, res.time, p.is_competing
        FROM results_result As res
        INNER JOIN registration_number nr ON res.number_id = nr.id
        INNER JOIN registration_participant p ON res.participant_id = p.id
        ) res2
        WHERE res2.competition_id = %s and (res2.time IS NULL or res2.is_competing is false)
        AND r.id = res2.id
        """, [self.competition_id, ])
