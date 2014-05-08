from django.db import models


class Root(models.Model):
    name = models.CharField(max_length=256, default='randomname')


class Related(models.Model):
    root = models.ForeignKey(Root)


class TwoRelated(models.Model):
    related = models.ForeignKey(Related)


class ThreeRelated(models.Model):
    twolated = models.ForeignKey(TwoRelated)


class FourRelated(models.Model):
    threerelated = models.ForeignKey(ThreeRelated)
