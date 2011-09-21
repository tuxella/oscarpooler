from django.db import models
import sys
from hashlib import md5
import datetime

# Create your models here.

base_hexa = "0123456789abcdef"
base_62 = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def baseconvert(number, fromdigits, todigits):
    x=long(0)
    for digit in str(number):
       x = x*len(fromdigits) + fromdigits.index(digit)
    res=""
    while x>0:
        digit = x % len(todigits)
        res = todigits[digit] + res
        x /= len(todigits)
    return res

class Journey(models.Model):
    title = models.CharField(max_length=200)
    from_addr = models.CharField(max_length=1000, blank = True)
    to_addr = models.CharField(max_length=1000, blank = True)
    meeting_addr = models.CharField(max_length=1000, blank = True)
    date = models.CharField(max_length=1000, blank = True)
    url_token = models.CharField(max_length=16, blank = True, unique = True)
    url_admin_token = models.CharField(max_length=32, blank = True)

    URL_HASH_LEN = 10

    def _generate_hash(self):
            journey_str = "%s%s%s%s%s%s" % (self.title,
                                            self.from_addr,
                                            self.to_addr,
                                            self.meeting_addr,
                                            self.date,
                                            datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            hasher = md5()
            hasher.update(journey_str)
            journey_hash = baseconvert(hasher.hexdigest(),
                                       base_hexa,
                                       base_62)
            return {"url_token":journey_hash[:self.URL_HASH_LEN],
                    "admin_url_token":journey_hash}

    def save(self, force_insert=False, force_update=False):
        if "" == self.url_token:
            tokens = self._generate_hash()
            # This works because the hash includes the datetime
            while 0 < len(Journey.objects.filter(url_token = tokens["url_token"])):
                tokens = self._generate_hash()
            self.url_token = tokens["url_token"]
            self.url_admin_token = tokens["admin_url_token"]
        super(Journey, self).save(force_insert, force_update)

    def available_seats(self):
        vehicles = Vehicle.objects.filter(journey = self.id)
        peoples = People.objects.filter(journey = self.id)
        people_count = 0
        seats_count = 0
        for p in peoples:
            people_count = people_count + p.count
        for v in vehicles:
            seats_count = seats_count + v.seats
        return seats_count - people_count

class People(models.Model):
    name = models.CharField(max_length=200)
    count = models.IntegerField(blank = True, null = True)
    journey = models.ForeignKey(Journey)

    def save(self, force_insert=False, force_update=False):
        if  self.count is None:
            self.count = 1
        super(People, self).save(force_insert, force_update)


class Vehicle(models.Model):
    name = models.CharField(max_length=200)
    seats = models.IntegerField()
    journey = models.ForeignKey(Journey)
    people = models.ForeignKey(People, blank = True, null = True)
