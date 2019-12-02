from django.forms import CheckboxInput
from random import randint
from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
)
from otree.db.models import Model, ForeignKey

class Constants(BaseConstants):
    name_in_url = 'volleying'
    players_per_group = 2
    num_rounds = 1


class Subsession(BaseSubsession):
    def creating_session(self):
        for group_id, group in enumerate(self.get_groups()):
            group.eliminateNegative = True
            group.volleyLots = group_id % 2 == 1
            group.goal = group_id % 4 < 2
            print(group.goal)
            group.chat = str(group_id) + 'chat1'
            group.chat2 = str(group_id) + 'chat2'
            group.generate_movie_options()

class Group(BaseGroup):

    def generate_movie_options(self):
        for name, movie in self.movies().items():
            movieObj = self.movieselection_set.create(group=self, key=name, name=movie["title"], description=movie["description"], embeddedVideo=movie["videoId"], isRemaining=True, isChecked=False)
            movieObj.save()

    def movies(self):
        return {'intouchables': {"videoId": "34WIbmXkewU", "description": "<strong> The Intouchables </strong>(Foreign) – two very different men bond and develop a very close relationship", "title":  "The Intouchables"},
                'starfish': {"videoId": "U5XnW3c8P-Y", "description": "<strong> Starfish </strong>(Science Fiction) – a young woman struggles with the death of her best friend", "title": "Starfish"}, 
                'versailles': {"videoId": "LQW9Ks0GZUQ", "description": "<strong>The Queen of Versailles </strong>(Documentary) – the economic crisis threatens the fortune of a billionaire family", "title": "The Queen of Versailles"},
                'hush': {"videoId": "Q_P8WCbhC6s", "description": "<strong>Hush </strong>(Horror) – a deaf writer living in the woods fights for her life when a killer appears in her window", "title": "Hush"},
                'father': {"videoId": "_bfqsNh6U7c", "description": "<strong> Like Father </strong> (Rom-com) – a woman left at the altar takes her estranged father on her honeymoon", "title": "Like Father"},
                'tomboy': {"videoId": "Jb-Oys-IcWE", "description": "<strong> Tomboy </strong> (Drama) - a 10-year old girl experiments with with her gender identity over the summer", "title": "Tomboy"},
                'phoenix': {"videoId": "1-q8C_c-nlM", "description": "<strong>Dark Phoenix </strong>(Science Fiction/Action) – the X-Men embark on a risky mission in space", "title": "Dark Phoenix"},
                'shazam': {"videoId": "Y5I4TA0yhr4", "description": "<strong>Shazam! </strong>(Superhero) - a 14-year-old transforms into an adult superhero with one magic word", "title": "Shazam!"},
                'dumbo': {"videoId": "7NiYVoqBt-8", "description": "<strong>Dumbo </strong>(Fantasy) - a man and his two children take care of a newborn elephant that can fly", "title": "Dumbo"},
                'survivalist': {"videoId": "KNADbtHsIU8", "description": "<strong>The Survivalist </strong>(Thriller) - a survivalist hides in the forest protecting his crop from intruders", "title": "The Survivalist"},
                'carol': {"videoId": "679wr31SXWk", "description": "<strong>Carol </strong>(Romance) - two women develop a fast bond that becomes a love with complicated consequences", "title": "Carol"},
                'wild': {"videoId": "tn2-GSqPyl0", "description": "<strong> Wild </strong>(Adventure) - a woman's solo undertakes a hike as a way to recover from a recent personal tragedy", "title": "Wild"}}
    
    eliminateNegative = models.BooleanField(initial=True) 

    goal = models.BooleanField()
    chat = models.StringField()
    chat2 = models.StringField()
    volleyLots = models.BooleanField()
    has_selected = models.BooleanField(initial=False)

    def get_movies(self):
        return MovieSelection.objects.filter(group__exact=self)

    def get_remaining_movies(self):
        return self.get_movies().filter(isRemaining=True)

    def get_eliminated_movies(self):
        return self.get_movies().filter(isRemaining=False)

    def get_eliminated_movie_descriptions(self):
        return map(lambda mov: mov.description, self.get_eliminated_movies())

    def get_remaining_movie_names(self):
        return map(lambda mov: mov.name, self.get_remaining_movies())

    def volleying(self):
        return not len(self.get_remaining_movies()) == 1

    def last_movie(self):
        return "" if len(self.get_remaining_movies()) == 0 else list(self.get_remaining_movies())[0]

    def last_movie_name(self):
        return "" if len(self.get_remaining_movies()) == 0 else self.get_remaining_movies()[0].name

    def last_movie_key(self):
        return "" if len(self.get_remaining_movies()) == 0 else self.get_remaining_movies()[0].key

    numberVolleys = models.IntegerField(initial=0)

    volley = models.LongStringField(initial="")

class MovieSelection(Model):
    group = ForeignKey(Group) 
    key = models.StringField()
    name = models.StringField()
    description = models.StringField()
    isRemaining = models.BooleanField()
    isChecked = models.BooleanField(initial=False, widget=CheckboxInput)
    embeddedVideo = models.StringField()

class Player(BasePlayer):

    def role(self):
        if self.id_in_group == 1:
            return 'player1'
        else:
            return 'player2'

    def get_partner(self):
        return self.get_others_in_group()[0]

    def get_partner_name(self):
        return self.get_others_in_group()[0].first_name

    def get_code(self):
        code = ""
        if not self.timed_out:
            code = "movies" + str(randint(1000, 9999))
        else:
            code =  "timeout" + str(randint(1000, 9999))
        self.mturkCompletitionCode = code
        return code


    selectedMovie = models.StringField(initial="")

    isSelecting = models.BooleanField()

    first_name = models.StringField(
        label="What is your first name?",
        initial=""
    )

    mturkId = models.StringField(
        label="What is your mturk ID?",
        initial=""
    )

    mturkCode = models.StringField()

    mturkCompletitionCode = models.StringField(initial="")

    timed_out = models.BooleanField(initial=False)

    madeFinalDecision = models.BooleanField()

    manip_question = models.StringField(
        label="In this study, what were you instructed to do?",
        widget=widgets.RadioSelect,
        choices=["Choose the movie that I personally would enjoy the most", "Choose the movie that I think my partner would enjoy the most"]
    )

    satisfied_trailer = models.IntegerField(
        label="How satisfied are you with the choice you came to with your partner?",
        choices=[[1, "1 (Very Unsatisfied)"], [2, "2"], [3, "3"], [4, "4"], [5, "5"], [6, "6"], [7, "7 (Very Satisfied)"]],
        widget=widgets.RadioSelect,
    )

    satisfied_process = models.IntegerField(
        label="How satisfied are you with the process by which you and your partner chose the movie trailer?",
        choices=[[1, "1 (Very Unsatisfied)"], [2, "2"], [3, "3"], [4, "4"], [5, "5"], [6, "6"], [7, "7 (Very Satisfied)"]],
        widget=widgets.RadioSelect,
    )

    satisfied_treated = models.IntegerField(
        label="How satisfied are you with how you were treated by your partner?",
        choices=[[1, "1 (Very Unsatisfied)"], [2, "2"], [3, "3"], [4, "4"], [5, "5"], [6, "6"], [7, "7 (Very Satisfied)"]],
        widget=widgets.RadioSelect,
    )

    willing_to = models.IntegerField(
        label="How willing would you be to make a decision with this partner again in the future?",
        choices=[[1, "1 (Very Unsatisfied)"], [2, "2"], [3, "3"], [4, "4"], [5, "5"], [6, "6"], [7, "7 (Very Satisfied)"]],
        widget=widgets.RadioSelect,
    )


    partner_experience = models.LongStringField(
        label="Explain how your experience with your partner was:",
    )

    strategy = models.LongStringField(
        label="Explain what your strategy was in selecting a movie trailer:",
    )

    rate_trailer = models.IntegerField(
        label="Please rate how much you liked the trailer",
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        widget=widgets.RadioSelect,
    )

    likely_watch = models.IntegerField(
        label="how likely are you to watch the movie?",
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        widget=widgets.RadioSelect,
    )

    # Demographic questions
    gender = models.IntegerField(
        label="What is your gender?",
        choices=[
            [1, 'Male'],
            [2, 'Female'],
            [3, 'Other']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    age = models.IntegerField(
        label="how old are you?",
        min=18,
        max=130, 
        blank=True
    )
    race = models.IntegerField(
        label="What is your race?",
        choices=[
            [1, 'White'],
            [2, 'Black, African-American'],
            [3, 'American Indian or Alaska Native'],
            [4, 'Asian or Asian-American'],
            [5, 'Pacific Islander'],
            [6, 'Some other race']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    education = models.IntegerField(
        label="Please indicate the highest level of education completed.",
        choices=[
            [1, 'Grammar school'],
            [2, 'High school or equivalent'],
            [3, 'Vocational/technical school (2 year)'],
            [4, 'Some college'],
            [5, 'College graduate (4 year)'],
            [6, 'Master\'s degree (MS, etc.)'],
            [7, 'Doctoral degree (PhD, etc.)'],
            [8, 'Professional degree (MD, JD, etc.)'],
            [9, 'Other']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    comment = models.LongStringField(
        label="Do you have any comments for the researchers? (Optional)", blank=True)
 