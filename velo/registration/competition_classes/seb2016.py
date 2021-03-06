import csv
from difflib import get_close_matches
import datetime

from django.db.models import Sum
from slugify import slugify

from velo.core.models import Log, Distance
from velo.registration.competition_classes.base_seb import SEBCompetitionBase
from velo.registration.models import Application, ChangedName, Number, Participant, UCICategory
from django import forms
from django.utils.translation import ugettext_lazy as _
from velo.registration.tables import ParticipantTableWithPoints, ParticipantTableWithPassage, ParticipantTable
from velo.results.helper import time_to_seconds, seconds_to_time
from velo.results.models import SebStandings, HelperResults, ChipScan, Result
from velo.results.tables import ResultDistanceCheckpointTable, ResultXCODistanceCheckpointSEBTable


class Seb2016(SEBCompetitionBase):
    competition_index = None

    SPORTA_DISTANCE_ID = 49
    TAUTAS_DISTANCE_ID = 50
    VESELIBAS_DISTANCE_ID = 51
    BERNU_DISTANCE_ID = 52

    STAGES_COUNT = 7

    @property
    def passages(self):
        return {
            # Passage, participant count, reserve
            self.SPORTA_DISTANCE_ID: [
                (1, 50, 0),
                (2, 50, 0),
                (3, 100, 0),
                (4, 100, 0),
                (5, 100, 0),
                (6, 100, 0)],
            self.TAUTAS_DISTANCE_ID: [
                (1,  50,  0),
                (2,  50,  0),
                (3,  100, 0),
                (4,  100, 0),
                (5,  200, 0),
                (6,  200, 0),
                (7,  200, 0),
                (8,  200, 0),
                (9,  200, 0),
                (10, 200, 0),
                (11, 200, 0),
                (12, 200, 0),
                (13, 200, 0),
                (14, 200, 0),
                (15, 200, 0),
                ],
        }


    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M Elite', 'M 19-34 CFA', 'W', 'M-35', 'M-40', 'M-45', 'M-50'),
            self.TAUTAS_DISTANCE_ID: ('M-16', 'T M-18', 'T M', 'T M-35', 'T M-40', 'T M-45', 'T M-50', 'T M-55', 'T M-60', 'T M-65', 'W-16', 'T W-18', 'T W', 'T W-35', 'T W-45'),
            self.VESELIBAS_DISTANCE_ID: ('M-14', 'W-14', ),
            self.BERNU_DISTANCE_ID: ('B 06-05 Z', 'B 06-05 M', 'B 07', 'B 08', 'B 09', 'B 10', 'B 11', 'B 12-', )
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 400, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 700, 'end': 3200, 'group': ''}, ],
            self.VESELIBAS_DISTANCE_ID: [{'start': 5000, 'end': 5200, 'group': ''}, ],
            self.BERNU_DISTANCE_ID: [{'start': 1, 'end': 150, 'group': group} for group in self.groups.get(self.BERNU_DISTANCE_ID)],
        }

    def result_select_extra(self, distance_id):
        if self.competition_index == 3:
            return {
                'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
                'l2': 'SELECT time FROM results_lapresult l2 WHERE l2.result_id = results_result.id and l2.index=2',
                'l3': 'SELECT time FROM results_lapresult l3 WHERE l3.result_id = results_result.id and l3.index=3',
                'l4': 'SELECT time FROM results_lapresult l4 WHERE l4.result_id = results_result.id and l4.index=4',
            }
        else:
            return {
                'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
            }

    def get_startlist_table_class(self, distance=None):
        if distance.id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            are_passages_assigned = HelperResults.objects.filter(competition=self.competition).exclude(passage_assigned=None).count()
            if are_passages_assigned:
                return ParticipantTableWithPassage
            else:
                return ParticipantTableWithPoints
        else:
            return ParticipantTable

    def _update_year(self, year):
        return year + 2

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if participant and (self._update_year(1995) >= year >= self._update_year(1980)) and UCICategory.objects.filter(category="CYCLING FOR ALL", slug=participant.slug):
                    return 'M 19-34 CFA'
                elif year in (self._update_year(1997), self._update_year(1996)):
                    return 'M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'M Elite'
                elif self._update_year(1979) >= year >= self._update_year(1975):
                    return 'M-35'
                elif self._update_year(1974) >= year >= self._update_year(1970):
                    return 'M-40'
                elif self._update_year(1969) >= year >= self._update_year(1965):
                    return 'M-45'
                elif year <= self._update_year(1964):
                    return 'M-50'
            else:
                return 'W'  # ok
        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'T M'
                elif self._update_year(1979) >= year >= self._update_year(1975):
                    return 'T M-35'
                elif self._update_year(1974) >= year >= self._update_year(1970):
                    return 'T M-40'
                elif self._update_year(1969) >= year >= self._update_year(1965):
                    return 'T M-45'
                elif self._update_year(1964) >= year >= self._update_year(1960):
                    return 'T M-50'
                elif self._update_year(1959) >= year >= self._update_year(1955):
                    return 'T M-55'
                elif self._update_year(1954) >= year >= self._update_year(1950):
                    return 'T M-60'
                elif year <= self._update_year(1949):
                    return 'T M-65'
            else:
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'W-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T W-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'T W'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'T W-35'
                elif year <= self._update_year(1969):
                    return 'T W-45'
        elif distance_id == self.BERNU_DISTANCE_ID:
            # bernu sacensibas
            if year >= 2012:
                return 'B 12-'
            elif year == 2011:
                return 'B 11'
            elif year == 2010:
                return 'B 10'
            elif year == 2009:
                return 'B 09'
            elif year == 2008:
                return 'B 08'
            elif year == 2007:
                return 'B 07'
            elif year in (2006, 2005):
                if gender == 'M':
                    return 'B 06-05 Z'
                else:
                    return 'B 06-05 M'

        elif distance_id == self.VESELIBAS_DISTANCE_ID:
            if year in (self._update_year(2000), self._update_year(2001), self._update_year(2002)):
                if gender == 'M':
                    return 'M-14'
                else:
                    return 'W-14'
            else:
                return ''

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning.')


    def payment_additional_checkboxes(self, application_id=None, application=None):
        if not application:
            application = Application.objects.get(id=application_id)

        if application.participant_set.filter(distance_id=self.SPORTA_DISTANCE_ID):
            distance = Distance.objects.get(id=self.SPORTA_DISTANCE_ID)
            return ('sport_approval', forms.BooleanField(label=_("I am informed that participation in %s requires LRF licence. More info - http://lrf.lv") % distance, required=True)),

        return ()

    def create_helper_results(self, participants):
        if self.competition.level != 2:
            raise Exception('We allow creating helper results only for stages.')


        # participants = participants.filter(distance_id__in=(self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID))

        current_competition = self.competition.parent
        prev_competition = current_competition.get_previous_sibling()

        # used for matching similar participants (grammar errors)
        prev_slugs = [obj.participant_slug for obj in SebStandings.objects.filter(competition=prev_competition)]

        def get_prev_standings(participant):
            standings = SebStandings.objects.filter(competition=prev_competition, participant_slug=participant.slug).order_by('-distance_total')

            if not standings:
                # 1. check if participant have changed name
                try:
                    changed = ChangedName.objects.get(new_slug=participant.slug)
                    standings = SebStandings.objects.filter(competition=prev_competition, participant_slug=changed.slug).order_by('-distance_total')
                except:
                    pass
            return standings

        def get_current_standing(participant):
            standings = SebStandings.objects.filter(competition=current_competition, participant_slug=participant.slug).order_by('-distance_total')

            if not standings:
                return None

            standings = standings.aggregate(distance_points1=Sum('distance_points1'),
                                            distance_points2=Sum('distance_points2'),
                                            distance_points3=Sum('distance_points3'),
                                            distance_points4=Sum('distance_points4'),
                                            distance_points5=Sum('distance_points5'),
                                            distance_points6=Sum('distance_points6'),
                                            distance_points7=Sum('distance_points7'))
            return standings

        for participant in participants:
            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant)

            current = helper.calculated_total

            if participant.distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
                continue

            # Calculate stage points only if last stage have finished + 2 days.
            if self.competition_index > 1:
                if self.competition.get_previous_sibling().competition_date  + datetime.timedelta(days=2) > datetime.date.today():
                    continue

            if helper.is_manual:
                continue # We do not want to overwrite manually created records

            current_standing = get_current_standing(participant)

            if self.competition_index == 1 or (self.competition_index == 2 and (not current_standing or current_standing.get('distance_points1') == 0)):
                standings = get_prev_standings(participant)
                try:
                    standing = standings[0]
                except:
                    standing = None

                helper.matches_slug = ''
                if standing:

                    # If participant have participated in all stages, but changed distances, we restore points
                    divide_by = 5.0
                    if standing.stages_participated < 5 and standings.count() > 1:
                        if standing.stages_participated + standings[1].stages_participated >= 5:
                            divide_by = float(standing.stages_participated)

                    helper.calculated_total = (standing.distance_total or 0.0) / divide_by

                    # If last year participant was riding in Tautas and this year he is riding in Sport distance, then he must be after those who where riding sport distance.
                    # To sort participants correctly we have to give less points to them but still keep order based on last years results.
                    # If we divide by 10, then we will get them at the end of list.
                    # If participant from Mammadaba now participates in tauta distance, then their points are reduced.
                    if (standing.distance.kind == 'T' and participant.distance.kind == 'S') or (standing.distance.kind == 'M' and participant.distance.kind == 'T'):
                        helper.calculated_total /= 10.0

                    if self.competition_index == 2:
                        helper.calculated_total /= 1.15

                    helper.result_used = standing
                else:
                    helper.calculated_total = 0.0
                    matches = get_close_matches(participant.slug, prev_slugs)
                    if matches:
                        helper.matches_slug = matches[0]
            elif current_standing:
                skipped_count = 0
                total_points_array = []

                stages = range(1, self.competition_index)
                for stage in stages:
                    points = current_standing.get('distance_points%i' % stage)

                    if points > 1000:
                        points /= 2  # There shouldn't be such a case, but still, if so, then we divide points by 2

                    if points > 0:
                        total_points_array.append(points)
                    else:
                        skipped_count += 1

                if len(total_points_array):
                    avg = float(sum(total_points_array)) / float(len(total_points_array))
                    if skipped_count in (1, 2):
                        total_points_array.append(avg / 1.15)

                    if skipped_count in (2, 3, 4):
                        total_points_array.append(avg / 1.25)

                    total_points_array = sorted(total_points_array, reverse=True)
                    if skipped_count > 2:
                        helper.calculated_total = sum(total_points_array[0:5]) / (len(total_points_array) + (skipped_count - 2))
                    else:
                        count = float(len(total_points_array))
                        if count > 5:
                            count = 5.0
                        helper.calculated_total = float(sum(total_points_array[0:5])) / count
                else:
                    helper.calculated_total = 0.0

                standings = SebStandings.objects.filter(competition=current_competition,
                                                       participant_slug=participant.slug).order_by('-distance_total')
                if standings.count() == 1:
                    standings = standings[0]
                    if standings.distance.kind == 'T' and participant.distance.kind == 'S' and helper.calculated_total > 0:
                        helper.calculated_total /= 10.0

            elif not participant.primary_number:
                matches = get_close_matches(participant.slug, prev_slugs)
                if matches:
                    helper.matches_slug = matches[0]

            if helper.calculated_total is None:
                helper.calculated_total = 0.0

            helper.calculated_total = round(helper.calculated_total, 2)

            helper.save()

    def get_group_for_number_search(self, distance_id, gender, birthday, group=None):
        if group is None:
            group = super(Seb2016, self).get_group_for_number_search(distance_id, gender, birthday)
        groups = self.groups.get(self.BERNU_DISTANCE_ID)

        if groups[0][:7] != groups[1][:7]:
            raise Exception("First two groups should be gender deperated. Update script otherwise.")

        if group in groups[:2]:
            return groups[0][:7]

        return group

    def recalculate_team_result(self, team_id=None, team=None):
        """
        3. stage should have zeros.
        """
        standing = super(Seb2016, self).recalculate_team_result(team_id, team)

        # Override point calculation.
        if standing.team.distance_id == self.SPORTA_DISTANCE_ID:
            if standing.points3:
                standing.points3 = 0

            # 3.stage is not taken because it is UCI category
            point_list = [standing.points1, standing.points2, standing.points4, standing.points5, standing.points6, standing.points7]
            point_list = filter(None, point_list)  # remove None from list
            setattr(standing, 'points_total', sum(point_list))

            standing.save()

        return standing

    def process_chip_result(self, chip_id, sendsms=True, recalc=False):
        """
        Function processes chip result and recalculates all standings
        """

        chip = ChipScan.objects.get(id=chip_id)

        if chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None

        if chip.nr.number < 500 and self.competition_index == 3:
            # We are not processing any numbers that are less than 500 in 3rd stage, as they are calculated in XCO competition.
            return False

        if chip.url_sync.kind == 'FINISH':
            return super(Seb2016, self).process_chip_result(chip_id, sendsms, recalc)
        else:
            result_time, seconds = self.calculate_time(chip)

            # Do not process if finished in 10 minutes.
            if seconds < 10 * 60: # 10 minutes
                Log.objects.create(content_object=chip, action="Chip process", message="Chip result less than 10 minutes. Ignoring.")
                return None

            participant = self.process_chip_create_participant(chip)

            if not participant:
                Log.objects.create(content_object=chip, action="Chip error", message="Participant not found")
                return False

            result, created = Result.objects.get_or_create(competition=chip.competition, participant=participant[0], number=chip.nr, )
            lap, created = result.lapresult_set.get_or_create(index=chip.url_sync.index)
            if lap.time:
                Log.objects.create(content_object=chip, action="Chip process", message="Lap time already set.")
                return None

            lap.time = result_time
            lap.save()

        print(chip)

    def get_result_table_class(self, distance, group=None):
        if self.competition_index == 3 and distance.id == self.SPORTA_DISTANCE_ID and not group:
            return ResultXCODistanceCheckpointSEBTable

        if distance.id != self.BERNU_DISTANCE_ID and not group:
            return ResultDistanceCheckpointTable

        return super(Seb2016, self).get_result_table_class(distance, group)

    def setup(self):
        uci = UCICategory.objects.filter(category="CYCLING FOR ALL", birthday__gte="1982-01-01", birthday__lt="1998-01-01")
        for u in uci:
            Participant.objects.filter(competition=self.competition, distance_id=49, is_participating=True, slug=u.slug, gender="M").update(group='M 19-34 CFA')

    def calculate_points_distance(self, result, top_result=None):
        """
        Overriding point calculation, because of 3rd
        """

        if self.competition_index == 3:
            if result.participant.distance_id == self.SPORTA_DISTANCE_ID and result.participant.group == 'M-18':
                # M-18 group was riding with TAUTA distance, so we need to recalculate points based on different top_result.
                try:
                    top_result = Result.objects.filter(competition=result.competition, number__distance_id=self.TAUTAS_DISTANCE_ID).exclude(time=None).order_by('time')[0]
                    tauta_time = time_to_seconds(self.competition.distanceadmin_set.get(distance_id=self.TAUTAS_DISTANCE_ID).zero)
                    sport_time = time_to_seconds(self.competition.distanceadmin_set.get(distance_id=self.SPORTA_DISTANCE_ID).zero)
                    top_result.time = seconds_to_time(time_to_seconds(top_result.time) + (tauta_time - sport_time))
                except IndexError:
                    return 1000

            elif result.participant.distance_id == self.SPORTA_DISTANCE_ID:
                # As the distance for women was shorter then men, but points should be calculated, we take proportion and calculate based on that.
                try:
                    top_result = Result.objects.filter(competition=result.competition, number__distance=result.number.distance).exclude(time=None).exclude(participant__group="W").order_by('time')[0]
                except IndexError:
                    return 1000

                if result.participant.group == 'W':
                    proportion = 80.0 / 103.0  # W distance was 80 km, but all M distance was 103 km
                    time = time_to_seconds(top_result.time) * proportion
                    top_result = Result(time=seconds_to_time(time))

        return super().calculate_points_distance(result, top_result)

    def import_children_csv(self, filename):
        with open(filename, 'r') as csvfile:
            results = csv.reader(csvfile)
            next(results)  # header line
            for row in results:
                print(row)
                if int(row[5]) != self.competition_index:
                    print("Not processing.")
                    continue

                if not row[1] or not row[2] or not row[3]:
                    print("Don't have all required data. Skipping.")
                    continue

                slug = slugify("%s-%s-%s" % (row[1], row[2], row[3]))
                participant = Participant.objects.filter(slug=slug, competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=self.BERNU_DISTANCE_ID)
                if participant:
                    participant = participant[0]
                else:
                    data = {
                        'competition_id': self.competition_id,
                        'distance_id': self.BERNU_DISTANCE_ID,
                        'team_name': row[4],
                        'is_participating': True,
                        'first_name': row[1],
                        'last_name': row[2],
                        'birthday': datetime.date(int(row[3]), 1, 1),
                        'is_only_year': True,
                        'gender': '',
                    }

                    if row[13] in ('F', 'M'):
                        data.update({'gender': row[13]})

                    participant = Participant.objects.create(**data)

                number_group = self.get_group_for_number_search(self.BERNU_DISTANCE_ID, 'M', datetime.date(int(row[3]), 1, 1))

                number = Number.objects.filter(competition=self.competition.parent, distance_id=self.BERNU_DISTANCE_ID, number=int(row[0][1:]), group=number_group).order_by('-id')
                number.update(participant_slug=participant.slug)
                if number:
                    participant.primary_number = number.get()
                    participant.save()

                if row[8]:
                    time = row[7]
                    status = ''
                    if time == 'NFL':
                        time = None
                        status = 'NFL'

                    result, created = Result.objects.get_or_create(competition=self.competition, participant=participant, number=number.get(),
                                                                   result_group=row[8] if row[8] else None, points_group=row[9] if row[9] else 0,
                                                                   status=status, time=time)
                    self.recalculate_standing_for_result(result)
                else:
                    print('didnt participate')
        self.assign_standing_places()
