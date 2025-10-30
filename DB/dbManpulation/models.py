from django.db import models


class Stable(models.Model):
    stableid = models.CharField(db_column='stableId', primary_key=True, max_length=15)
    stablename = models.CharField(db_column='stableName', max_length=30, blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    colors = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stable'

    def __str__(self):
        # what shows in admin dropdowns
        return f"{self.stableid} - {self.stablename or 'Unnamed Stable'}"


class Horse(models.Model):
    horseid = models.CharField(db_column='horseId', primary_key=True, max_length=15)
    horsename = models.CharField(db_column='horseName', max_length=30)  # increased from 15 for safety
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    registration = models.IntegerField()
    stableid = models.ForeignKey(Stable, models.DO_NOTHING, db_column='stableId')

    class Meta:
        managed = False
        db_table = 'horse'

    def __str__(self):
        return f"{self.horseid} - {self.horsename}"


class Owner(models.Model):
    ownerid = models.CharField(db_column='ownerId', primary_key=True, max_length=15)
    lname = models.CharField(max_length=15, blank=True, null=True)
    fname = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'owner'

    def __str__(self):
        # "Saeed Ahmed" style
        first = self.fname or ""
        last = self.lname or ""
        return f"{first} {last}".strip() or self.ownerid


class Owns(models.Model):
    # NOTE: Real DB has composite PK (ownerId, horseId). Django can't do that natively.
    # We will treat (ownerid, horseid) as unique together and let Django think ownerid is the PK.
    ownerid = models.ForeignKey(Owner, models.DO_NOTHING, db_column='ownerId', primary_key=True)
    horseid = models.ForeignKey(Horse, models.DO_NOTHING, db_column='horseId')

    class Meta:
        managed = False
        db_table = 'owns'
        unique_together = (('ownerid', 'horseid'),)

    def __str__(self):
        return f"{self.ownerid} owns {self.horseid}"


class Track(models.Model):
    trackname = models.CharField(db_column='trackName', primary_key=True, max_length=30)
    location = models.CharField(max_length=30, blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'track'

    def __str__(self):
        return self.trackname


class Race(models.Model):
    raceid = models.CharField(db_column='raceId', primary_key=True, max_length=15)
    racename = models.CharField(db_column='raceName', max_length=30, blank=True, null=True)
    trackname = models.ForeignKey(Track, models.DO_NOTHING, db_column='trackName', blank=True, null=True)
    racedate = models.DateField(db_column='raceDate', blank=True, null=True)
    racetime = models.TimeField(db_column='raceTime', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'race'

    def __str__(self):
        return f"{self.raceid} - {self.racename}"


class Raceresults(models.Model):
    # Same composite-PK issue as Owns: real PK is (raceId, horseId).
    raceid = models.ForeignKey(Race, models.DO_NOTHING, db_column='raceId', primary_key=True)
    horseid = models.ForeignKey(Horse, models.DO_NOTHING, db_column='horseId')
    results = models.CharField(max_length=15, blank=True, null=True)
    prize = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raceresults'
        unique_together = (('raceid', 'horseid'),)

    def __str__(self):
        return f"{self.raceid} - {self.horseid} : {self.results}"


class Trainer(models.Model):
    trainerid = models.CharField(db_column='trainerId', primary_key=True, max_length=15)
    lname = models.CharField(max_length=30, blank=True, null=True)
    fname = models.CharField(max_length=30, blank=True, null=True)
    stableid = models.ForeignKey(Stable, models.DO_NOTHING, db_column='stableId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trainer'

    def __str__(self):
        first = self.fname or ""
        last = self.lname or ""
        return f"{first} {last}".strip() or self.trainerid
