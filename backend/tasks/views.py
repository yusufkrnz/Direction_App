from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import DailyTask
from .serializers import DailyTaskSerializer
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import firebase_admin
from firebase_admin import firestore
from django.conf import settings

# Firebase Firestore client
db = firestore.client()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_daily_tasks(request):
    """Günlük görevleri getir - Sadece bugün oluşturulan görevler"""
    try:        # Kullanıcının UID'sini al
        user_uid = request.user.firebase_uid        
        # Bugünün tarihini al (Türkiye saati)
        today = timezone.now().date()        
        # Firebase'den görevleri al
        try:
            user_ref = db.collection('users').document(user_uid)
            tasks_ref = user_ref.collection('tasks')
            firestore_tasks = tasks_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
            
            tasks_data = []
            for task_doc in firestore_tasks:
                task_data = task_doc.to_dict()
                
                # Sadece bugün oluşturulan görevleri filtrele
                created_at = task_data.get('created_at')
                if created_at:
                    # ISO string'i datetime'a çevir
                    if isinstance(created_at, str):
                        from datetime import datetime
                        try:
                            created_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            created_date = created_datetime.date()
                        except:
                            # Eğer parse edilemezse bugün kabul et
                            created_date = today
                    else:
                        created_date = created_at.date()
                    
                    # Sadece bugün oluşturulan görevleri ekle
                    if created_date == today:
                        tasks_data.append(task_data)} görev alındı")
            
            # İstatistikleri hesapla
            total_tasks = len(tasks_data)
            completed_tasks = len([task for task in tasks_data if task.get('is_completed', False)])
            pending_tasks = total_tasks - completed_tasks
            
            return Response({
                'success': True,
                'data': {
                    'tasks': tasks_data,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'pending_tasks': pending_tasks
                }
            })
            
        except Exception as firebase_error:            # Fallback: Django'dan al            
            # Sadece bugün oluşturulan görevleri getir
            tasks = DailyTask.objects.filter(
                user_uid=user_uid,
                created_at__date=today
            ).order_by('-created_at')
            
            # Serialize et
            serializer = DailyTaskSerializer(tasks, many=True)
            
            # İstatistikleri hesapla
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(is_completed=True).count()
            pending_tasks = total_tasks - completed_tasks
            
            return Response({
                'success': True,
                'data': {
                    'tasks': serializer.data,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'pending_tasks': pending_tasks
                }
            })
        
    except Exception as e:        return Response({
            'success': False,
            'message': f'Görevler getirilirken hata oluştu: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task_detail(request, task_id):
    """Belirli bir görevin detaylarını getir"""
    try:        # Kullanıcının UID'sini al
        user_uid = request.user.firebase_uid        
        # Firebase'den görevi getir
        try:
            user_ref = db.collection('users').document(user_uid)
            task_ref = user_ref.collection('tasks').document(str(task_id))
            task_doc = task_ref.get()
            
            if not task_doc.exists:
                return Response({
                    'success': False,
                    'message': 'Görev bulunamadı'
                }, status=status.HTTP_404_NOT_FOUND)
            
            task_data = task_doc.to_dict()            
            return Response({
                'success': True,
                'data': task_data
            })
            
        except Exception as firebase_error:            # Fallback: Django'dan getir            
            # Görevi getir
            task = DailyTask.objects.get(id=task_id, user_uid=user_uid)
            
            # Serialize et
            serializer = DailyTaskSerializer(task)
            
            return Response({
                'success': True,
                'data': serializer.data
            })
        
    except ObjectDoesNotExist:
        return Response({
            'success': False,
            'message': 'Görev bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:        return Response({
            'success': False,
            'message': f'Görev detayı getirilirken hata oluştu: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_daily_task(request):
    """Yeni görev oluştur"""
    try:}")        
        # Kullanıcının UID'sini al
        user_uid = request.user.firebase_uid
        
        if not user_uid:
            return Response({
                'success': False,
                'message': 'Kullanıcı UID bulunamadı'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Request data'sını al
        data = request.data.copy()
        data['user_uid'] = user_uid        
        # Serialize et ve validate et
        serializer = DailyTaskSerializer(data=data)
        if serializer.is_valid():
            # Django database'e kaydet
            task = serializer.save()            
            # Firebase Firestore'a kaydet
            try:
                task_data = serializer.data
                task_data['id'] = task.id
                task_data['created_at'] = task.created_at.isoformat()
                task_data['updated_at'] = task.updated_at.isoformat()
                
                # Firestore'a kaydet
                user_ref = db.collection('users').document(user_uid)
                tasks_ref = user_ref.collection('tasks')
                firestore_task = tasks_ref.document(str(task.id))
                firestore_task.set(task_data)                
            except Exception as firebase_error:                # Firebase hatası olsa bile Django kaydı başarılı olduğu için devam et
            
            return Response({
                'success': True,
                'message': 'Görev başarıyla oluşturuldu',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:            return Response({
                'success': False,
                'message': 'Geçersiz veri',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:        return Response({
            'success': False,
            'message': f'Görev oluşturulurken hata oluştu: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_daily_task(request, task_id):
    """Görevi güncelle"""
    try:        # Kullanıcının UID'sini al
        user_uid = request.user.firebase_uid        
        # Firebase'den görevi güncelle
        try:
            user_ref = db.collection('users').document(user_uid)
            task_ref = user_ref.collection('tasks').document(str(task_id))
            task_doc = task_ref.get()
            
            if not task_doc.exists:
                return Response({
                    'success': False,
                    'message': 'Görev bulunamadı'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Mevcut veriyi al
            current_data = task_doc.to_dict()
            
            # Yeni veriyi hazırla
            update_data = request.data.copy()
            
            # Eğer görev tamamlandıysa completed_at'i set et
            if update_data.get('is_completed') and not current_data.get('is_completed', False):
                update_data['completed_at'] = timezone.now().isoformat()
            elif not update_data.get('is_completed') and current_data.get('is_completed', False):
                update_data['completed_at'] = None
            
            # updated_at'i güncelle
            update_data['updated_at'] = timezone.now().isoformat()
            
            # Firebase'i güncelle
            task_ref.update(update_data)            
            # Güncellenmiş veriyi döndür
            updated_doc = task_ref.get()
            updated_data = updated_doc.to_dict()
            
            return Response({
                'success': True,
                'message': 'Görev başarıyla güncellendi',
                'data': updated_data
            })
            
        except Exception as firebase_error:            # Fallback: Django'dan güncelle            
            # Görevi getir
            task = DailyTask.objects.get(id=task_id, user_uid=user_uid)
            
            # Request data'sını al
            data = request.data.copy()
            
            # Eğer görev tamamlandıysa completed_at'i set et
            if data.get('is_completed') and not task.is_completed:
                data['completed_at'] = timezone.now()
            elif not data.get('is_completed') and task.is_completed:
                data['completed_at'] = None
            
            # Serialize et ve update et
            serializer = DailyTaskSerializer(task, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Görev başarıyla güncellendi',
                    'data': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Geçersiz veri',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
    except ObjectDoesNotExist:
        return Response({
            'success': False,
            'message': 'Görev bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:        return Response({
            'success': False,
            'message': f'Görev güncellenirken hata oluştu: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks_by_date(request):
    """Belirli bir tarih için görevleri getir"""
    try:        # Kullanıcının UID'sini al
        user_uid = request.user.firebase_uid
        
        # Tarih parametresini al
        date_str = request.GET.get('date')
        if not date_str:
            return Response({
                'success': False,
                'message': 'Tarih parametresi gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Tarihi parse et
            from datetime import datetime
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Geçersiz tarih formatı. YYYY-MM-DD formatında olmalı'
            }, status=status.HTTP_400_BAD_REQUEST)        
        # Firebase'den görevleri al
        try:
            user_ref = db.collection('users').document(user_uid)
            tasks_ref = user_ref.collection('tasks')
            firestore_tasks = tasks_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
            
            tasks_data = []
            for task_doc in firestore_tasks:
                task_data = task_doc.to_dict()
                
                # Sadece hedef tarihte oluşturulan görevleri filtrele
                created_at = task_data.get('created_at')
                if created_at:
                    # ISO string'i datetime'a çevir
                    if isinstance(created_at, str):
                        try:
                            created_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            created_date = created_datetime.date()
                        except:
                            # Eğer parse edilemezse atla
                            continue
                    else:
                        created_date = created_at.date()
                    
                    # Sadece hedef tarihte oluşturulan görevleri ekle
                    if created_date == target_date:
                        tasks_data.append(task_data)} görev alındı")
            
            # İstatistikleri hesapla
            total_tasks = len(tasks_data)
            completed_tasks = len([task for task in tasks_data if task.get('is_completed', False)])
            pending_tasks = total_tasks - completed_tasks
            
            return Response({
                'success': True,
                'data': {
                    'tasks': tasks_data,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'pending_tasks': pending_tasks,
                    'date': target_date.isoformat()
                }
            })
            
        except Exception as firebase_error:            # Fallback: Django'dan al            
            # Sadece hedef tarihte oluşturulan görevleri getir
            tasks = DailyTask.objects.filter(
                user_uid=user_uid,
                created_at__date=target_date
            ).order_by('-created_at')
            
            # Serialize et
            serializer = DailyTaskSerializer(tasks, many=True)
            
            # İstatistikleri hesapla
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(is_completed=True).count()
            pending_tasks = total_tasks - completed_tasks
            
            return Response({
                'success': True,
                'data': {
                    'tasks': serializer.data,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'pending_tasks': pending_tasks,
                    'date': target_date.isoformat()
                }
            })
        
    except Exception as e:        return Response({
            'success': False,
            'message': f'Görevler getirilirken hata oluştu: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_daily_task(request, task_id):
    """Görevi sil"""
    try:        # Kullanıcının UID'sini al
        user_uid = request.user.firebase_uid        
        # Firebase'den görevi sil
        try:
            user_ref = db.collection('users').document(user_uid)
            task_ref = user_ref.collection('tasks').document(str(task_id))
            task_doc = task_ref.get()
            
            if not task_doc.exists:
                return Response({
                    'success': False,
                    'message': 'Görev bulunamadı'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Firebase'den sil
            task_ref.delete()            
            return Response({
                'success': True,
                'message': 'Görev başarıyla silindi'
            })
            
        except Exception as firebase_error:            # Fallback: Django'dan sil            
            # Görevi getir ve sil
            task = DailyTask.objects.get(id=task_id, user_uid=user_uid)
            task.delete()
            
            return Response({
                'success': True,
                'message': 'Görev başarıyla silindi'
            })
            
    except ObjectDoesNotExist:
        return Response({
            'success': False,
            'message': 'Görev bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:        return Response({
            'success': False,
            'message': f'Görev silinirken hata oluştu: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
