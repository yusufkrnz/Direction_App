from django.test import TestCase
from rest_framework.test import APITestCase
from .models import ExamCategory, Subject, Topic, Question


class ExamCategoryTests(APITestCase):
    def test_list_categories(self):
        """Sınav kategorileri listelenir"""
        pass

    def test_category_subjects(self):
        """Kategoriye ait dersler listelenir"""
        pass


class TopicTests(APITestCase):
    def test_topic_tree_structure(self):
        """Konu ağacı doğru şekilde oluşturulur"""
        pass

    def test_get_children(self):
        """Alt konular doğru getirilir"""
        pass

    def test_is_leaf(self):
        """Yaprak düğüm kontrolü çalışır"""
        pass


class QuestionTests(APITestCase):
    def test_random_questions(self):
        """Rastgele sorular getirilir"""
        pass

    def test_filter_by_difficulty(self):
        """Zorluk seviyesine göre filtreleme çalışır"""
        pass
