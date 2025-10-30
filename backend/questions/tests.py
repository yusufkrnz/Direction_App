from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Question


class QuestionTests(APITestCase):
    def test_upload_image(self):
        """Image can be uploaded for question"""
        pass

    def test_create_question(self):
        """Question can be created"""
        pass

    def test_get_my_questions(self):
        """User can retrieve their questions"""
        pass
