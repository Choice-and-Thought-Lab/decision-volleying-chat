from ._builtin import Page, WaitPage
from .models import Constants, MovieSelection
from .forms import MovieForm, MovieResultForm
from django.forms import modelformset_factory
import time

MovieFormset = modelformset_factory(
    MovieSelection, form=MovieForm, fields=('isChecked',), extra=0)
RemainingMovie = modelformset_factory(
    MovieSelection, form=MovieResultForm, fields=('embeddedVideo',), extra=0)


class Consent(Page):
    pass


class Introduction(Page):
    def before_next_page(self):
        # user has 60 minutes to complete as many pages as possible
        if self.player.id_in_group == 1:
            self.player.isSelecting = True
        else:
            self.player.isSelecting = False


class ParticipantInfo(Page):
    template_name = 'volleying/ParticipantInfo.html'
    form_model = 'player'
    form_fields = ['first_name']

    def error_message(self, values):
        if len(values["first_name"]) == 0:
            return 'Please enter your name'


class ChatWaitPage(WaitPage):
    template_name = 'volleying/WaitForChat.html'

    def after_all_players_arrive(self):
        self.is_displayed = True


class Chat(Page):
    def get_timeout_seconds(self):
        return 90


class Instructions(Page):
    def get_timeout_seconds(self):
        return 8


def sort_movies(movie):
    return movie.key

class Volley(Page):
    form_model = 'group'
    template_name = 'volleying/Volley.html'

    def vars_for_template(self):
        remaining_movies = self.player.group.get_remaining_movies()
        
        question_formset = MovieFormset(queryset=MovieSelection.objects.filter(group__exact=self.player.group).filter(isRemaining__exact=True))
        for (form, model) in zip(question_formset, remaining_movies):
            form.setLabel(model.description)
        
        return {
            'movie_formset': question_formset
        }

    def before_next_page(self):
        if self.player.role() == "player1":
            self.group.numberVolleys += 1
            self.player.isSelecting = False
            self.player.get_others_in_group()[0].isSelecting = True
            self.group.volley = self.group.volley + \
                "[" + " ".join(self.group.get_remaining_movie_names()) + "] "

            all_movies = MovieSelection.objects.filter(
                group__exact=self.player.group)
            remaining_movies = all_movies.filter(isRemaining__exact=True)

            submitted_data = self.form.data

            movies_by_id = {mov.pk: mov for mov in remaining_movies}

            for i in range(len(remaining_movies)):
                input_prefix = 'form-%d-' % (len(remaining_movies) - i - 1)
                input_prefix1 = 'form-%d-' % i
                mov_id1 = int(submitted_data[input_prefix1 + 'id'])
                isChecked = submitted_data.get(input_prefix + 'isChecked')

                mov = movies_by_id[mov_id1]

                if isChecked:
                    mov.isChecked = True
                    mov.isRemaining = True
                else:
                    mov.isChecked = False
                    mov.isRemaining = False

                mov.save()

            if self.timeout_happened:
                self.player.get_partner().timed_out = True
                self.player.timed_out = True

        self.group.has_selected = True

    def get_timeout_seconds(self):
        return 300

    def error_message(self, values):
        remaining_movies = self.player.group.get_remaining_movies()
        submitted_data = self.form.data
        num_checked = 0

        for i in range(len(remaining_movies)):
            input_prefix = 'form-%d-' % i
            isChecked = submitted_data.get(input_prefix + 'isChecked')

            if isChecked:
                num_checked += 1

        if (num_checked != 1) and self.player.role() == "player1":
            return 'You must select only one movie trailer'
        else:
            pass

class TrailerSelectWaitPage(WaitPage):
    template_name = 'volleying/WaitPage.html'

    def after_all_players_arrive(self):
        self.is_displayed = True


class TrailerIntro(Page):
    timeout_seconds = 5

    def vars_for_template(self):
        self.player.madeFinalDecision = not self.player.isSelecting
        self.player.selectedMovie = self.player.group.last_movie_name()
        return {
            "finalMovie": self.player.selectedMovie
        }

    def before_next_page(self):
        self.player.selectedMovie = self.player.group.last_movie_name()


class Results(Page):
    def get_timeout_seconds(self):
        return 60*2.5 

    def is_displayed(self):
        return not self.player.timed_out

    def vars_for_template(self):
        remaining_movies = self.player.group.get_remaining_movies()
        question_formset = RemainingMovie(queryset=MovieSelection.objects.filter(
            group__exact=self.player.group).filter(isRemaining__exact=True))

        for (form, model) in zip(question_formset, remaining_movies):
            form.generateVideoHtml(model.embeddedVideo)

        return {
            'movie_formset': question_formset
        }


class FollowUpQuestions(Page):
    form_model = 'player'
    form_fields = ['own_satisfaction_a', 'own_satisfaction_b', 'partner_satisfaction_a', 'partner_satisfaction_b', 'satisfied_process', 'satisfied_treated', 'willing_to', 'comment']

    def is_displayed(self):
        return not self.player.timed_out

    def before_next_page(self):
        if self.timeout_happened:
            self.player.timed_out = True


class ManipulationChecks(Page):
    form_fields = ['manip_question']


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'race', 'gender']

    def is_displayed(self):
        return not self.player.timed_out

    def before_next_page(self):
        if self.timeout_happened:
            self.player.timed_out = True


class Conclusion(Page):
    pass


page_sequence = [
    Consent,
    Introduction,
    ParticipantInfo,
    ChatWaitPage,
    Instructions,
    Volley,
    TrailerSelectWaitPage,
    TrailerIntro,
    Results,
    FollowUpQuestions,
    Demographics,
    Conclusion
]
