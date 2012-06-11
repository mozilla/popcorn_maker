from django.test import TestCase

from nose.tools import ok_, eq_
from ..models import Tutorial


class TutorialTest(TestCase):

    def tearDown(self):
        Tutorial.objects.all().delete()


    def test_tutorial_creation(self):
        data = {
            'title': 'How to do X with popcornjs',
            'body': 'This is amazing!',
            }
        tutorial = Tutorial.objects.create(**data)
        ok_(tutorial.id)
        ok_(tutorial.slug)
        ok_(tutorial.created)
        ok_(tutorial.modified)
        eq_(tutorial.status, Tutorial.HIDDEN)
