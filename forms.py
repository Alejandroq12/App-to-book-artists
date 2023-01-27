import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Optional, AnyOf, URL, Regexp

genresList = [
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]

statesList = [
            ('AL', 'Alabama'),
            ('AK', 'Alaska'),
            ('AZ', 'Arizona'),
            ('AR', 'Arkansas'),
            ('CA', 'California'),
            ('CO', 'Colorado'),
            ('CT', 'Connecticut'),
            ('DE', 'Delaware'),
            ('DC', 'District of Columbia'),
            ('FL', 'Florida'),
            ('GA', 'Georgia'),
            ('HI', 'Hawaii'),
            ('ID', 'Idaho'),
            ('IL', 'Illinois'),
            ('IN', 'Indiana'),
            ('IA', 'Iowa'),
            ('KS', 'Kansas'),
            ('KY', 'Kentucky'),
            ('LA', 'Louisiana'),
            ('ME', 'Maine'),
            ('MT', 'Montana'),
            ('NE', 'Nebraska'),
            ('NV', 'Nevada'),
            ('NH', 'New Hampshire'),
            ('NJ', 'New Jersey'),
            ('NM', 'New Mexico'),
            ('NY', 'New York'),
            ('NC', 'North Carolina'),
            ('ND', 'North Dakota'),
            ('OH', 'Ohio'),
            ('OK', 'Oklahoma'),
            ('OR', 'Oregon'),
            ('MD', 'Maryland'),
            ('MA', 'Massachusetts'),
            ('MI', 'Michigan'),
            ('MN', 'Minnesota'),
            ('MS', 'Mississippi'),
            ('MO', 'Missouri'),
            ('PA', 'Pennsylvania'),
            ('RI', 'Rhode Island'),
            ('SC', 'South Carolina'),
            ('SD', 'South Dakota'),
            ('TN', 'Tennessee'),
            ('TX', 'Texas'),
            ('UT', 'Utah'),
            ('VT', 'Vermont'),
            ('VA', 'Virginia'),
            ('WA', 'Washington'),
            ('WV', 'West Virginia'),
            ('WY', 'Wisconsin'),
        ]

class ShowForm(Form):
    artist_id = SelectField(
        'artist_id',
        validators=[DataRequired()],
        choices=[]
    )
    venue_id = SelectField(
        'venue_id',
        validators=[DataRequired()],
        choices=[]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.datetime.now()
    )


class VenueForm(Form):
    csrf = False

    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    city = StringField(
        'city',
        validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[DataRequired()],
        choices=statesList
    )
    address = StringField(
        'address',
        validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[DataRequired(), Regexp(r'\w{3}-\w{3}-\w{4}')]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL()]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired()],
        choices=genresList
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), URL()]
    )
    website = StringField(
        'website',
        validators=[Optional(), URL()]
    )
    seeking_talent = BooleanField('seeking_talent')
    seeking_description = StringField(
        'seeking_description'
    )


class ArtistForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    city = StringField(
        'city',
        validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[DataRequired()],
        choices=statesList
    )
    phone = StringField(
        'phone',
        validators=[Optional(), Regexp(r'\w{3}-\w{3}-\w{4}')]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL()]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired()],
        choices=genresList
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), URL()]
    )
    seeking_venue = BooleanField('seeking_venue')
    seeking_description = StringField(
        'seeking_description'
    )