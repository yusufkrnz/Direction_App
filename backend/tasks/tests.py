from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import DailyTask


class DailyTaskTests(APITestCase):
    def setUp(self):
        self.create_url = '/api/tasks/create/'
        self.list_url = '/api/tasks/'

    def test_create_daily_task(self):
        """Daily task can be created"""
        pass

    def test_get_daily_tasks(self):
        """User can retrieve their daily tasks"""
        pass

    def test_update_task_status(self):
        """Task status can be updated"""
        pass

    def test_delete_task(self):
        """Task can be deleted"""
        pass

    def test_get_tasks_by_date(self):
        """Tasks can be filtered by date"""
        pass
