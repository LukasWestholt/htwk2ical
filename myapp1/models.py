from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta
import urllib.parse
import hashlib
import random

from config import latest_valid_date, start_date, start_week, FULL_DOMAIN


MAX_LENGTH_WORKGROUP = 5


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fetched_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class GroupCache(models.Model):
    key = models.CharField(max_length=200)
    value = models.JSONField()


class Group(models.Model):
    name = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=200, default="")
    sg_url = models.CharField(max_length=200, default="")

    def is_studium_generale(self):
        return self.title == ""

    def __str__(self):
        return self.name


class Module(models.Model):
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    workgroups = ArrayField(models.CharField(max_length=MAX_LENGTH_WORKGROUP), default=list)

    class Meta:
        unique_together = ('name', 'group')
        ordering = ['name']

    def add_workgroup(self, txt):
        if len(txt) <= MAX_LENGTH_WORKGROUP:
            self.workgroups.append(txt)
        else:
            raise ValueError("workgroup name to big")

    def __str__(self):
        return self.name


class Appointment(models.Model):
    # data = models.JSONField(unique=True)
    """weeks = models.CharField(max_length=200, validators=[int_list_validator(
        message="Enter only digits separated by commas.",
    )])"""
    weeks = ArrayField(models.IntegerField())
    weekday = models.IntegerField()
    start = models.IntegerField()
    end = models.IntegerField()
    location = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)
    lecturer = models.CharField(max_length=200, null=True, blank=True)
    notes = models.CharField(max_length=200, null=True, blank=True)
    workgroups = ArrayField(models.CharField(max_length=5))

    modules = models.ManyToManyField(Module)

    def __str__(self):
        return str(
            [self.weeks, self.weekday, self.start, self.end, self.location, self.type, self.lecturer, self.notes]
        )


class ModuleAlias(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    custom_name = models.CharField(max_length=200)

    class Meta:
        unique_together = ('module', 'custom_name')


class ModuleWorkgroup(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    workgroup = models.CharField(max_length=MAX_LENGTH_WORKGROUP)

    class Meta:
        unique_together = ('module', 'workgroup')


# Generates a new secret by creating an MD5-hash of the current UNIX-time (ms
# since 01.01.1970) with a random number appended. By checking whether the
# generated secret exists we make sure it stays unique.
def generate_secret():
    secret = str(hashlib.md5(
        str((datetime.now()-datetime(1970, 1, 1)).total_seconds() + random.randint(1, 99)).encode('utf-8')
    ).hexdigest())[:8]
    if len(Calendar.objects.filter(secret=secret)) != 0:
        print("secret generator failed.")
        return generate_secret()
    return secret


class Calendar(TimeStampMixin):
    secret = models.CharField(max_length=8, default=generate_secret, unique=True)
    modules = models.ManyToManyField(Module)
    groups = models.ManyToManyField(Group)
    aliases = models.ManyToManyField(ModuleAlias)
    workgroups = models.ManyToManyField(ModuleWorkgroup)
    #password = models.

    def events(self):
        secret = self.secret
        time_format = "%Y%m%dT%H%M%S"

        # don't fetch events for outdated calendars
        if self.created_at < latest_valid_date:
            now = timezone.localtime(timezone.now())
            event_end = (now + timedelta(hours=2))
            return [{
                "summary":     "Kalender aktualisieren",
                "description": "Dein Kalender ist nicht mehr gültig. "
                               "Bitte besuche " + FULL_DOMAIN + ", um einen neuen zu erstellen.",
                "start":       now,
                "end":         event_end,
                "uid":         secret + "_" + now.strftime(time_format) + "-" + event_end.strftime(time_format) +
                               "_deprecated"
            }]

        events = []

        for module in self.modules.all():

            name = module.name
            for x in self.aliases.all():
                if x.module.id == module.id:
                    name = x.custom_name

            fitting_workgroup = False
            for x in self.workgroups.all():
                if x.module.id == module.id:
                    fitting_workgroup = x.workgroup

            # TODO
            # re.search(r"\s*SCHWARZ.*Gr.\s*([" + "".join([str(y) if y != prof_schwarz_group else "" for y in range(1, 4)]) + r"]).*", desc)

            for ap in module.appointment_set.all():
                if fitting_workgroup and len(ap.workgroups) != 0:
                    if fitting_workgroup not in ap.workgroups:
                        continue

                location = ap.location if ap.location else ""
                summary = name + (" (" + ap.type + ")" if ap.type else "")
                description = [x for x in [ap.lecturer, ap.notes] if x]
                for week in ap.weeks:
                    day_start = timezone.localtime(start_date) + timedelta(weeks=(week - start_week), days=ap.weekday)
                    event_start = day_start + timedelta(seconds=ap.start)
                    event_end = day_start + timedelta(seconds=ap.end or 60*60*24)
                    assert(event_end > event_start)
                    events.append(
                        {
                            "location":    location,
                            "summary":     summary,
                            "description": ", ".join(description),
                            "start":       event_start,
                            "end":         event_end,
                            "uid":         secret + "_" + event_start.strftime(time_format) + "-" +
                                           event_end.strftime(time_format) + "_" + summary + "_" +
                                           urllib.parse.quote(name.encode('utf8'))
                        }
                    )
        return events
