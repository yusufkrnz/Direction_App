from django.test import TestCase
from rest_framework.test import APITestCase
from .models import MindMap, MindMapNode


class MindMapTests(APITestCase):
    def test_create_mindmap_from_speech(self):
        """Mind map can be created from speech text"""
        pass

    def test_get_user_mindmaps(self):
        """User can retrieve their mind maps"""
        pass

    def test_get_mindmap_detail(self):
        """Mind map detail can be fetched"""
        pass

    def test_expand_mindmap_node(self):
        """Mind map node can be expanded"""
        pass

