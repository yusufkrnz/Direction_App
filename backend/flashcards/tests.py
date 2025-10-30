from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Flashcard, FlashcardDeck, FlashcardProgress


class FlashcardTests(APITestCase):
    def test_create_flashcard(self):
        """Flashcard oluşturulabilir"""
        pass

    def test_random_flashcards(self):
        """Rastgele flashcard'lar getirilir"""
        pass


class FlashcardDeckTests(APITestCase):
    def test_create_deck(self):
        """Deste oluşturulabilir"""
        pass

    def test_add_flashcard_to_deck(self):
        """Desteye flashcard eklenebilir"""
        pass

    def test_remove_flashcard_from_deck(self):
        """Desteden flashcard kaldırılabilir"""
        pass


class FlashcardProgressTests(APITestCase):
    def test_start_learning(self):
        """Yeni flashcard öğrenmeye başlanır"""
        pass

    def test_spaced_repetition_algorithm(self):
        """Spaced repetition algoritması çalışır"""
        pass

    def test_due_for_review(self):
        """Tekrar zamanı gelen kartlar listelenir"""
        pass
