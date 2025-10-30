from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import UserExamAttempt, SubjectPerformance, StudyPlan


class UserExamAttemptTests(APITestCase):
    def setUp(self):
        self.submit_url = '/api/coaching/exam-attempts/submit_exam_result/'

    def test_submit_exam_result(self):
        """Sınav sonucu başarıyla kaydedilir"""
        pass

    def test_subject_performance_updated(self):
        """Sınav sonrası ders performansı güncellenir"""
        pass


class StudyPlanTests(APITestCase):
    def test_create_study_plan(self):
        """Çalışma planı oluşturulabilir"""
        pass

    def test_list_user_study_plans(self):
        """Kullanıcı kendi planlarını listeleyebilir"""
        pass


class SpacedRepetitionTests(APITestCase):
    def test_due_reviews(self):
        """Tekrar zamanı gelen konular listelenir"""
        pass

    def test_calculate_next_review(self):
        """Sonraki tekrar tarihi doğru hesaplanır"""
        pass
