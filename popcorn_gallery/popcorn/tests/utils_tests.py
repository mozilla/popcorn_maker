import mock
import datetime

from django.db import models
from django.test import TestCase

from dateutil.relativedelta import relativedelta
from nose.tools import eq_, ok_
from ..utils import update_views_count, get_order_fields, update_vote_score


class _ModelMock(mock.MagicMock):
    def _get_child_mock(self, **kwargs):
        name = kwargs.get('name', '')
        if name == 'pk':
            return self.id
        if name in ['views_count', 'votes_count']:
            return 0
        return super(_ModelMock, self)._get_child_mock(**kwargs)


class MockItemModel(models.Model):
    views_count = models.IntegerField(default=0)
    votes_count = models.IntegerField(default=0)


class UpdateViewsCounterTest(TestCase):

    def setUp(self):
        self.item = _ModelMock(spec=MockItemModel())

    @mock.patch('django.core.cache.cache.set', return_value=True)
    @mock.patch('django.core.cache.cache.get', return_value=False)
    def test_count_not_in_cache(self, cache_get, cache_set):
        self.item.modified = datetime.datetime.utcnow() - relativedelta(minutes=1)
        count = update_views_count(self.item)
        eq_(count, 1)
        eq_(self.item.save.called, False)

    @mock.patch('django.core.cache.cache.set', return_value=True)
    @mock.patch('django.core.cache.cache.get', return_value=1)
    def test_count_in_cache(self, cache_get, cache_set):
        self.item.modified = datetime.datetime.utcnow() - relativedelta(minutes=1)
        count = update_views_count(self.item)
        eq_(count, 2)
        eq_(self.item.save.called, False)

    @mock.patch('django.core.cache.cache.set', return_value=True)
    @mock.patch('django.core.cache.cache.get', return_value=1)
    def test_count_saved(self, cache_get, cache_set):
        self.item.modified = datetime.datetime.utcnow() - relativedelta(minutes=11)
        count = update_views_count(self.item)
        eq_(count, 2)
        eq_(self.item.save.called, True)


class OrderFieldsTest(TestCase):

    def test_order_default(self):
        order = get_order_fields({})
        eq_(order, ['-is_featured','-created'])

    def test_order_override(self):
        order = {'order': 'default'}
        new_default = {'default': ['test']}
        order = get_order_fields(order, **new_default)
        eq_(order, ['test'])

    def test_order_invalid(self):
        order = {'order': 'something-malicious'}
        order = get_order_fields(order)
        eq_(order, ['-is_featured','-created'])

    def test_order_requested(self):
        order = {'order': 'created'}
        order = get_order_fields(order)
        eq_(order, ['-created'])


mock_votes = mock.patch('voting.models.Vote.objects.get_score',
                        return_value={'num_votes': 1,
                                      'score': 1})


class UpdateVoteScore(TestCase):

    def setUp(self):
        self.item = _ModelMock(spec=MockItemModel())

    @mock_votes
    def test_no_update_vote(self, mocked_vote):
        self.item.modified = datetime.datetime.utcnow() - relativedelta(minutes=1)
        votes = update_vote_score(self.item)
        eq_(votes['num_votes'], 1)
        eq_(votes['score'], 1)
        eq_(self.item.save.called, False)

    @mock_votes
    def test_update_vote(self, mocked_vote):
        self.item.modified = datetime.datetime.utcnow() - relativedelta(minutes=11)
        votes = update_vote_score(self.item)
        eq_(votes['num_votes'], 1)
        eq_(votes['score'], 1)
        eq_(self.item.save.called, True)

    @mock_votes
    def test_vote_no_change(self, mocked_vote):
        self.item.modified = datetime.datetime.utcnow() - relativedelta(minutes=11)
        self.item.votes_count = 1
        votes = update_vote_score(self.item)
        eq_(votes['num_votes'], 1)
        eq_(votes['score'], 1)
        eq_(self.item.save.called, False)
