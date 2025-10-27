from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.models import Log
from core.decorators import admin_required, check_giris_izni
from core.forms import (
    GorevForm, MesaiForm, IzinForm, AracForm,
    GorevlendirmeForm, MalzemeForm, GorevYeriForm,
    PersonelForm, SifreForm
)


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_protect
def giris(request):
    """
    Login view - handles user authentication
    """
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        kullaniciadi = request.POST.get('kullaniciadi')
        sifre = request.POST.get('sifre')
        
        # Authenticate user
        user = authenticate(request, username=kullaniciadi, password=sifre)
        
        if user is not None:
            # Login successful
            login(request, user)
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=user,
                    islem=f"Kullanıcı giriş yaptı",
                    ip=get_client_ip(request)
                )
            except Exception as e:
                # Log creation failed, but don't prevent login
                pass
            
            messages.success(request, f'Hoş geldiniz, {user.adsoyad}!')
            
            # Redirect to next page or dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            # Login failed
            messages.error(request, 'Kullanıcı adı veya şifre hatalı!')
    
    return render(request, 'auth/login.html')


def cikis(request):
    """
    Logout view - handles user logout
    """
    if request.user.is_authenticated:
        # Create log entry before logout
        try:
            Log.objects.create(
                sofor=request.user,
                islem=f"Kullanıcı çıkış yaptı",
                ip=get_client_ip(request)
            )
        except Exception as e:
            # Log creation failed, but don't prevent logout
            pass
        
        user_name = request.user.adsoyad
        logout(request)
        messages.success(request, f'Güle güle, {user_name}!')
    
    return redirect('giris')


@login_required(login_url='giris')
@check_giris_izni
def dashboard(request):
    """
    Dashboard view - displays statistics, recent tasks, and alerts
    Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
    """
    from core.models import Gorev, Personel, Arac, Mesai
    from django.db.models import Q, Count
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get current date and time
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Calculate statistics (Requirement 12.1)
    total_gorev = Gorev.objects.filter(gizle=False).count()
    total_personel = Personel.objects.filter(is_active=True, girisizni=False).count()
    total_arac = Arac.objects.filter(arsiv=False, gizle=False).count()
    
    # Get recent tasks (last 10) (Requirement 12.2)
    recent_gorevler = Gorev.objects.filter(
        gizle=False
    ).select_related('sofor', 'yurt', 'arac').order_by('-bstarih')[:10]
    
    # Get upcoming inspection/insurance warnings (Requirement 12.3)
    # Check for vehicles with inspection/insurance dates within 30 days
    warning_date = now + timedelta(days=30)
    arac_uyarilar = []
    
    for arac in Arac.objects.filter(arsiv=False, gizle=False):
        warnings = []
        
        # Check muayene (inspection)
        if arac.muayene:
            if arac.muayene < now:
                warnings.append(f"Muayene tarihi geçmiş! ({arac.muayene.strftime('%d.%m.%Y')})")
            elif arac.muayene < warning_date:
                days_left = (arac.muayene.date() - now.date()).days
                warnings.append(f"Muayene tarihi yaklaşıyor ({days_left} gün kaldı)")
        
        # Check sigorta (insurance)
        if arac.sigorta:
            if arac.sigorta < now:
                warnings.append(f"Sigorta tarihi geçmiş! ({arac.sigorta.strftime('%d.%m.%Y')})")
            elif arac.sigorta < warning_date:
                days_left = (arac.sigorta.date() - now.date()).days
                warnings.append(f"Sigorta tarihi yaklaşıyor ({days_left} gün kaldı)")
        
        # Check egzoz (emission test)
        if arac.egzoz:
            if arac.egzoz < now:
                warnings.append(f"Egzoz tarihi geçmiş! ({arac.egzoz.strftime('%d.%m.%Y')})")
            elif arac.egzoz < warning_date:
                days_left = (arac.egzoz.date() - now.date()).days
                warnings.append(f"Egzoz tarihi yaklaşıyor ({days_left} gün kaldı)")
        
        if warnings:
            arac_uyarilar.append({
                'arac': arac,
                'warnings': warnings
            })
    
    # Get today's tasks (Requirement 12.4)
    bugunun_gorevleri = Gorev.objects.filter(
        gizle=False,
        bstarih__gte=today_start,
        bstarih__lte=today_end
    ).select_related('sofor', 'yurt', 'arac').order_by('bstarih')
    
    # Get today's overtime work (Requirement 12.4)
    bugunun_mesaileri = Mesai.objects.filter(
        bstarih__gte=today_start,
        bstarih__lte=today_end
    ).select_related('sofor', 'arac').order_by('bstarih')
    
    # If user is not admin, show only their own tasks and overtime (Requirement 12.5)
    if not request.user.yonetici:
        bugunun_gorevleri = bugunun_gorevleri.filter(sofor=request.user)
        bugunun_mesaileri = bugunun_mesaileri.filter(sofor=request.user)
        recent_gorevler = Gorev.objects.filter(
            gizle=False,
            sofor=request.user
        ).select_related('sofor', 'yurt', 'arac').order_by('-bstarih')[:10]
    
    context = {
        'user': request.user,
        # Statistics
        'total_gorev': total_gorev,
        'total_personel': total_personel,
        'total_arac': total_arac,
        # Recent tasks
        'recent_gorevler': recent_gorevler,
        # Vehicle warnings
        'arac_uyarilar': arac_uyarilar,
        # Today's activities
        'bugunun_gorevleri': bugunun_gorevleri,
        'bugunun_mesaileri': bugunun_mesaileri,
    }
    
    return render(request, 'dashboard.html', context)


# ============================================================================
# GÖREV YÖNETİMİ (TASK MANAGEMENT)
# Requirements: 2.1-2.9, 11.4, 11.7
# ============================================================================

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


@login_required(login_url='giris')
@check_giris_izni
def gorev_taslak_listesi(request):
    """
    Display draft tasks list (tasks not yet completed)
    Requirements: 2.1, 2.6, 2.9
    """
    from core.models import Gorev
    
    # Base query - exclude hidden tasks (soft delete)
    gorevler = Gorev.objects.filter(gizle=False, durum__isnull=True).select_related('sofor', 'yurt', 'arac')
    
    # If not admin, show only user's own tasks (Requirement 1.4)
    if not request.user.yonetici:
        gorevler = gorevler.filter(sofor=request.user)
    
    # Search and filtering (Requirement 2.9)
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    arac_filter = request.GET.get('arac', '')
    yurt_filter = request.GET.get('yurt', '')
    baslangic_tarih = request.GET.get('baslangic_tarih', '')
    bitis_tarih = request.GET.get('bitis_tarih', '')
    
    if search_query:
        gorevler = gorevler.filter(
            Q(varisyeri__icontains=search_query) |
            Q(yetkili__icontains=search_query) |
            Q(aciklama__icontains=search_query) |
            Q(sofor__adsoyad__icontains=search_query)
        )
    
    if personel_filter:
        gorevler = gorevler.filter(sofor_id=personel_filter)
    
    if arac_filter:
        gorevler = gorevler.filter(arac_id=arac_filter)
    
    if yurt_filter:
        gorevler = gorevler.filter(yurt_id=yurt_filter)
    
    if baslangic_tarih:
        gorevler = gorevler.filter(bstarih__gte=baslangic_tarih)
    
    if bitis_tarih:
        gorevler = gorevler.filter(bstarih__lte=bitis_tarih)
    
    # Order by start date (newest first)
    gorevler = gorevler.order_by('-bstarih')
    
    # Pagination (Requirement 11.4)
    paginator = Paginator(gorevler, 25)  # 25 items per page
    page = request.GET.get('page')
    
    try:
        gorevler_page = paginator.page(page)
    except PageNotAnInteger:
        gorevler_page = paginator.page(1)
    except EmptyPage:
        gorevler_page = paginator.page(paginator.num_pages)
    
    # Get filter options for dropdowns
    from core.models import Personel, Arac, GorevYeri
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    araclar = Arac.objects.filter(gizle=False, arsiv=False).order_by('plaka')
    yurtlar = GorevYeri.objects.all().order_by('ad')
    
    context = {
        'gorevler': gorevler_page,
        'personeller': personeller,
        'araclar': araclar,
        'yurtlar': yurtlar,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'arac_filter': arac_filter,
        'yurt_filter': yurt_filter,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
    }
    
    return render(request, 'gorev/taslak.html', context)


@login_required(login_url='giris')
@check_giris_izni
def gorev_nihai_listesi(request):
    """
    Display completed tasks list (final list)
    Requirements: 2.3, 2.6, 2.9
    """
    from core.models import Gorev
    from django.utils import timezone
    
    # Get current month's start and end dates
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Base query - completed tasks in current month
    gorevler = Gorev.objects.filter(
        gizle=False,
        durum=1,
        bstarih__gte=current_month_start
    ).select_related('sofor', 'yurt', 'arac')
    
    # If not admin, show only user's own tasks
    if not request.user.yonetici:
        gorevler = gorevler.filter(sofor=request.user)
    
    # Search and filtering
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    arac_filter = request.GET.get('arac', '')
    yurt_filter = request.GET.get('yurt', '')
    baslangic_tarih = request.GET.get('baslangic_tarih', '')
    bitis_tarih = request.GET.get('bitis_tarih', '')
    
    if search_query:
        gorevler = gorevler.filter(
            Q(varisyeri__icontains=search_query) |
            Q(yetkili__icontains=search_query) |
            Q(aciklama__icontains=search_query) |
            Q(sofor__adsoyad__icontains=search_query)
        )
    
    if personel_filter:
        gorevler = gorevler.filter(sofor_id=personel_filter)
    
    if arac_filter:
        gorevler = gorevler.filter(arac_id=arac_filter)
    
    if yurt_filter:
        gorevler = gorevler.filter(yurt_id=yurt_filter)
    
    if baslangic_tarih:
        gorevler = gorevler.filter(bstarih__gte=baslangic_tarih)
    
    if bitis_tarih:
        gorevler = gorevler.filter(bstarih__lte=bitis_tarih)
    
    # Order by start date (newest first)
    gorevler = gorevler.order_by('-bstarih')
    
    # Pagination
    paginator = Paginator(gorevler, 25)
    page = request.GET.get('page')
    
    try:
        gorevler_page = paginator.page(page)
    except PageNotAnInteger:
        gorevler_page = paginator.page(1)
    except EmptyPage:
        gorevler_page = paginator.page(paginator.num_pages)
    
    # Get filter options
    from core.models import Personel, Arac, GorevYeri
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    araclar = Arac.objects.filter(gizle=False, arsiv=False).order_by('plaka')
    yurtlar = GorevYeri.objects.all().order_by('ad')
    
    context = {
        'gorevler': gorevler_page,
        'personeller': personeller,
        'araclar': araclar,
        'yurtlar': yurtlar,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'arac_filter': arac_filter,
        'yurt_filter': yurt_filter,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
    }
    
    return render(request, 'gorev/nihai.html', context)


@login_required(login_url='giris')
@check_giris_izni
def gecen_ay_gorevler(request):
    """
    Display last month's tasks
    Requirements: 2.4
    """
    from core.models import Gorev
    from django.utils import timezone
    
    # Get last month's start and end dates
    now = timezone.now()
    last_month_end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Base query - tasks from last month
    gorevler = Gorev.objects.filter(
        gizle=False,
        bstarih__gte=last_month_start,
        bstarih__lte=last_month_end
    ).select_related('sofor', 'yurt', 'arac')
    
    # If not admin, show only user's own tasks
    if not request.user.yonetici:
        gorevler = gorevler.filter(sofor=request.user)
    
    # Search and filtering
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    arac_filter = request.GET.get('arac', '')
    yurt_filter = request.GET.get('yurt', '')
    
    if search_query:
        gorevler = gorevler.filter(
            Q(varisyeri__icontains=search_query) |
            Q(yetkili__icontains=search_query) |
            Q(aciklama__icontains=search_query) |
            Q(sofor__adsoyad__icontains=search_query)
        )
    
    if personel_filter:
        gorevler = gorevler.filter(sofor_id=personel_filter)
    
    if arac_filter:
        gorevler = gorevler.filter(arac_id=arac_filter)
    
    if yurt_filter:
        gorevler = gorevler.filter(yurt_id=yurt_filter)
    
    # Order by start date (newest first)
    gorevler = gorevler.order_by('-bstarih')
    
    # Pagination
    paginator = Paginator(gorevler, 25)
    page = request.GET.get('page')
    
    try:
        gorevler_page = paginator.page(page)
    except PageNotAnInteger:
        gorevler_page = paginator.page(1)
    except EmptyPage:
        gorevler_page = paginator.page(paginator.num_pages)
    
    # Get filter options
    from core.models import Personel, Arac, GorevYeri
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    araclar = Arac.objects.filter(gizle=False, arsiv=False).order_by('plaka')
    yurtlar = GorevYeri.objects.all().order_by('ad')
    
    context = {
        'gorevler': gorevler_page,
        'personeller': personeller,
        'araclar': araclar,
        'yurtlar': yurtlar,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'arac_filter': arac_filter,
        'yurt_filter': yurt_filter,
        'last_month_start': last_month_start,
        'last_month_end': last_month_end,
    }
    
    return render(request, 'gorev/gecen_ay.html', context)


@login_required(login_url='giris')
@check_giris_izni
def eski_gorevler(request):
    """
    Display archived tasks (older than last month)
    Requirements: 2.5
    """
    from core.models import Gorev
    from django.utils import timezone
    
    # Get date for 2 months ago
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (current_month_start - relativedelta(months=1))
    
    # Base query - tasks older than last month (before last month's start date)
    gorevler = Gorev.objects.filter(
        gizle=False,
        bstarih__lt=last_month_start
    ).select_related('sofor', 'yurt', 'arac')
    
    # If not admin, show only user's own tasks
    if not request.user.yonetici:
        gorevler = gorevler.filter(sofor=request.user)
    
    # Search and filtering
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    arac_filter = request.GET.get('arac', '')
    yurt_filter = request.GET.get('yurt', '')
    baslangic_tarih = request.GET.get('baslangic_tarih', '')
    bitis_tarih = request.GET.get('bitis_tarih', '')
    
    if search_query:
        gorevler = gorevler.filter(
            Q(varisyeri__icontains=search_query) |
            Q(yetkili__icontains=search_query) |
            Q(aciklama__icontains=search_query) |
            Q(sofor__adsoyad__icontains=search_query)
        )
    
    if personel_filter:
        gorevler = gorevler.filter(sofor_id=personel_filter)
    
    if arac_filter:
        gorevler = gorevler.filter(arac_id=arac_filter)
    
    if yurt_filter:
        gorevler = gorevler.filter(yurt_id=yurt_filter)
    
    if baslangic_tarih:
        gorevler = gorevler.filter(bstarih__gte=baslangic_tarih)
    
    if bitis_tarih:
        gorevler = gorevler.filter(bstarih__lte=bitis_tarih)
    
    # Order by start date (newest first)
    gorevler = gorevler.order_by('-bstarih')
    
    # Pagination
    paginator = Paginator(gorevler, 25)
    page = request.GET.get('page')
    
    try:
        gorevler_page = paginator.page(page)
    except PageNotAnInteger:
        gorevler_page = paginator.page(1)
    except EmptyPage:
        gorevler_page = paginator.page(paginator.num_pages)
    
    # Get filter options
    from core.models import Personel, Arac, GorevYeri
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    araclar = Arac.objects.filter(gizle=False, arsiv=False).order_by('plaka')
    yurtlar = GorevYeri.objects.all().order_by('ad')
    
    context = {
        'gorevler': gorevler_page,
        'personeller': personeller,
        'araclar': araclar,
        'yurtlar': yurtlar,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'arac_filter': arac_filter,
        'yurt_filter': yurt_filter,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
    }
    
    return render(request, 'gorev/eski.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorev_ekle(request):
    """
    Add new task
    Requirements: 2.1, 2.2
    """
    from core.models import Gorev, Personel, Arac, GorevYeri
    from django import forms
    
    class GorevForm(forms.ModelForm):
        class Meta:
            model = Gorev
            fields = ['sofor', 'yurt', 'varisyeri', 'arac', 'bstarih', 'bttarih', 'yetkili', 'ilolur', 'aciklama']
            widgets = {
                'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'bttarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'aciklama': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                'sofor': forms.Select(attrs={'class': 'form-select'}),
                'yurt': forms.Select(attrs={'class': 'form-select'}),
                'arac': forms.Select(attrs={'class': 'form-select'}),
                'varisyeri': forms.TextInput(attrs={'class': 'form-control'}),
                'yetkili': forms.TextInput(attrs={'class': 'form-control'}),
                'ilolur': forms.TextInput(attrs={'class': 'form-control'}),
            }
            labels = {
                'sofor': 'Personel',
                'yurt': 'Görev Yeri',
                'varisyeri': 'Varış Yeri',
                'arac': 'Araç',
                'bstarih': 'Başlangıç Tarihi',
                'bttarih': 'Bitiş Tarihi',
                'yetkili': 'Yetkili',
                'ilolur': 'İl Olur',
                'aciklama': 'Açıklama',
            }
        
        def clean(self):
            cleaned_data = super().clean()
            bstarih = cleaned_data.get('bstarih')
            bttarih = cleaned_data.get('bttarih')
            
            # Validate that end date is after start date
            if bstarih and bttarih and bttarih < bstarih:
                raise forms.ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = GorevForm(request.POST)
        if form.is_valid():
            gorev = form.save(commit=False)
            gorev.gizle = False
            gorev.durum = None  # Draft status
            gorev.aktarildi = 0
            gorev.save()
            
            # Create log entry (Requirement 2.7)
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Yeni görev eklendi: {gorev.sofor.adsoyad} - {gorev.varisyeri}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Görev başarıyla eklendi!')
            return redirect('gorev_taslak')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = GorevForm()
    
    context = {
        'form': form,
        'title': 'Yeni Görev Ekle',
    }
    
    return render(request, 'gorev/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorev_duzenle(request, id):
    """
    Edit existing task
    Requirements: 2.7
    """
    from core.models import Gorev
    from django import forms
    from django.shortcuts import get_object_or_404
    
    gorev = get_object_or_404(Gorev, id=id, gizle=False)
    
    class GorevForm(forms.ModelForm):
        class Meta:
            model = Gorev
            fields = ['sofor', 'yurt', 'varisyeri', 'arac', 'bstarih', 'bttarih', 'yetkili', 'ilolur', 'aciklama', 'durum']
            widgets = {
                'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'bttarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'aciklama': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                'sofor': forms.Select(attrs={'class': 'form-select'}),
                'yurt': forms.Select(attrs={'class': 'form-select'}),
                'arac': forms.Select(attrs={'class': 'form-select'}),
                'varisyeri': forms.TextInput(attrs={'class': 'form-control'}),
                'yetkili': forms.TextInput(attrs={'class': 'form-control'}),
                'ilolur': forms.TextInput(attrs={'class': 'form-control'}),
                'durum': forms.Select(attrs={'class': 'form-select'}, choices=[(None, 'Taslak'), (1, 'Tamamlandı')]),
            }
            labels = {
                'sofor': 'Personel',
                'yurt': 'Görev Yeri',
                'varisyeri': 'Varış Yeri',
                'arac': 'Araç',
                'bstarih': 'Başlangıç Tarihi',
                'bttarih': 'Bitiş Tarihi',
                'yetkili': 'Yetkili',
                'ilolur': 'İl Olur',
                'aciklama': 'Açıklama',
                'durum': 'Durum',
            }
        
        def clean(self):
            cleaned_data = super().clean()
            bstarih = cleaned_data.get('bstarih')
            bttarih = cleaned_data.get('bttarih')
            
            if bstarih and bttarih and bttarih < bstarih:
                raise forms.ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = GorevForm(request.POST, instance=gorev)
        if form.is_valid():
            form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Görev düzenlendi: {gorev.sofor.adsoyad} - {gorev.varisyeri}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Görev başarıyla güncellendi!')
            return redirect('gorev_taslak')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        # Format datetime for HTML5 input
        initial_data = {
            'bstarih': gorev.bstarih.strftime('%Y-%m-%dT%H:%M') if gorev.bstarih else '',
            'bttarih': gorev.bttarih.strftime('%Y-%m-%dT%H:%M') if gorev.bttarih else '',
        }
        form = GorevForm(instance=gorev, initial=initial_data)
    
    context = {
        'form': form,
        'gorev': gorev,
        'title': 'Görev Düzenle',
    }
    
    return render(request, 'gorev/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorev_sil(request, id):
    """
    Soft delete task (set gizle=True)
    Requirements: 2.8
    """
    from core.models import Gorev
    from django.shortcuts import get_object_or_404
    
    gorev = get_object_or_404(Gorev, id=id)
    
    if request.method == 'POST':
        # Soft delete - set gizle=True instead of actual deletion
        gorev.gizle = True
        gorev.save()
        
        # Create log entry
        try:
            Log.objects.create(
                sofor=request.user,
                islem=f"Görev silindi: {gorev.sofor.adsoyad} - {gorev.varisyeri}",
                ip=get_client_ip(request)
            )
        except Exception:
            pass
        
        messages.success(request, 'Görev başarıyla silindi!')
        return redirect('gorev_taslak')
    
    context = {
        'gorev': gorev,
    }
    
    return render(request, 'gorev/sil_onay.html', context)


# ============================================================================
# MESAİ VE İZİN YÖNETİMİ (OVERTIME AND LEAVE MANAGEMENT)
# Requirements: 3.1-3.8
# ============================================================================

from django import forms
from core.models import Mesai, Izin, Personel, Arac


@login_required(login_url='giris')
@check_giris_izni
def mesai_listesi(request):
    """
    Display overtime (mesai) list
    Requirements: 3.1, 3.6
    """
    # Base query
    mesailer = Mesai.objects.select_related('sofor', 'arac')
    
    # If not admin, show only user's own records
    if not request.user.yonetici:
        mesailer = mesailer.filter(sofor=request.user)
    
    # Search and filtering (Requirement 3.6)
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    baslangic_tarih = request.GET.get('baslangic_tarih', '')
    bitis_tarih = request.GET.get('bitis_tarih', '')
    
    if search_query:
        mesailer = mesailer.filter(
            Q(sofor__adsoyad__icontains=search_query) |
            Q(gorev__icontains=search_query)
        )
    
    if personel_filter:
        mesailer = mesailer.filter(sofor_id=personel_filter)
    
    if baslangic_tarih:
        mesailer = mesailer.filter(bstarih__gte=baslangic_tarih)
    
    if bitis_tarih:
        mesailer = mesailer.filter(bstarih__lte=bitis_tarih)
    
    # Order by start date (newest first)
    mesailer = mesailer.order_by('-bstarih')
    
    # Pagination
    paginator = Paginator(mesailer, 25)
    page = request.GET.get('page')
    
    try:
        mesailer_page = paginator.page(page)
    except PageNotAnInteger:
        mesailer_page = paginator.page(1)
    except EmptyPage:
        mesailer_page = paginator.page(paginator.num_pages)
    
    # Get filter options
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    
    context = {
        'mesailer': mesailer_page,
        'personeller': personeller,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
    }
    
    return render(request, 'mesai/liste.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def mesai_ekle(request):
    """
    Add new overtime record
    Requirements: 3.1, 3.2, 3.3
    """
    class MesaiForm(forms.ModelForm):
        class Meta:
            model = Mesai
            fields = ['sofor', 'bstarih', 'bttarih', 'arac', 'gorev', 'pazargunu']
            widgets = {
                'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'bttarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'sofor': forms.Select(attrs={'class': 'form-select'}),
                'arac': forms.Select(attrs={'class': 'form-select'}),
                'gorev': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
                'pazargunu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }
            labels = {
                'sofor': 'Personel',
                'bstarih': 'Başlangıç Tarihi',
                'bttarih': 'Bitiş Tarihi',
                'arac': 'Araç',
                'gorev': 'Görev Açıklaması',
                'pazargunu': 'Pazar Günü',
            }
        
        def clean(self):
            cleaned_data = super().clean()
            bstarih = cleaned_data.get('bstarih')
            bttarih = cleaned_data.get('bttarih')
            
            if bstarih and bttarih and bttarih < bstarih:
                raise forms.ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = MesaiForm(request.POST)
        if form.is_valid():
            mesai = form.save(commit=False)
            
            # Calculate overtime duration (Requirement 3.2)
            if mesai.bstarih and mesai.bttarih:
                duration = mesai.bttarih - mesai.bstarih
                hours = duration.total_seconds() / 3600
                mesai.mesai = f"{hours:.2f}"
            
            # Check if it's Sunday (Requirement 3.3)
            if mesai.bstarih and mesai.bstarih.weekday() == 6:
                mesai.pazargunu = True
            
            mesai.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Yeni mesai kaydı eklendi: {mesai.sofor.adsoyad}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Mesai kaydı başarıyla eklendi!')
            return redirect('mesai_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = MesaiForm()
    
    context = {
        'form': form,
        'title': 'Yeni Mesai Ekle',
    }
    
    return render(request, 'mesai/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
def izin_listesi(request):
    """
    Display leave (izin) list
    Requirements: 3.4, 3.6
    """
    # Base query
    izinler = Izin.objects.select_related('sofor')
    
    # If not admin, show only user's own records
    if not request.user.yonetici:
        izinler = izinler.filter(sofor=request.user)
    
    # Search and filtering (Requirement 3.6)
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    izin_turu = request.GET.get('izin_turu', '')
    baslangic_tarih = request.GET.get('baslangic_tarih', '')
    bitis_tarih = request.GET.get('bitis_tarih', '')
    
    if search_query:
        izinler = izinler.filter(
            Q(sofor__adsoyad__icontains=search_query) |
            Q(aciklama__icontains=search_query)
        )
    
    if personel_filter:
        izinler = izinler.filter(sofor_id=personel_filter)
    
    if izin_turu:
        izinler = izinler.filter(izin=izin_turu)
    
    if baslangic_tarih:
        izinler = izinler.filter(bstarih__gte=baslangic_tarih)
    
    if bitis_tarih:
        izinler = izinler.filter(bstarih__lte=bitis_tarih)
    
    # Order by start date (newest first)
    izinler = izinler.order_by('-bstarih')
    
    # Pagination
    paginator = Paginator(izinler, 25)
    page = request.GET.get('page')
    
    try:
        izinler_page = paginator.page(page)
    except PageNotAnInteger:
        izinler_page = paginator.page(1)
    except EmptyPage:
        izinler_page = paginator.page(paginator.num_pages)
    
    # Get filter options
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    
    context = {
        'izinler': izinler_page,
        'personeller': personeller,
        'izin_turleri': Izin.IZIN_TURLERI,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'izin_turu': izin_turu,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
    }
    
    return render(request, 'izin/liste.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def izin_ekle(request):
    """
    Add new leave record
    Requirements: 3.4, 3.5
    """
    class IzinForm(forms.ModelForm):
        class Meta:
            model = Izin
            fields = ['sofor', 'izin', 'bstarih', 'bttarih', 'gun', 'saat', 'aciklama']
            widgets = {
                'bstarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'bttarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'sofor': forms.Select(attrs={'class': 'form-select'}),
                'izin': forms.Select(attrs={'class': 'form-select'}),
                'gun': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
                'saat': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
                'aciklama': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }
            labels = {
                'sofor': 'Personel',
                'izin': 'İzin Türü',
                'bstarih': 'Başlangıç Tarihi',
                'bttarih': 'Bitiş Tarihi',
                'gun': 'Gün Sayısı',
                'saat': 'Saat',
                'aciklama': 'Açıklama',
            }
        
        def clean(self):
            cleaned_data = super().clean()
            bstarih = cleaned_data.get('bstarih')
            bttarih = cleaned_data.get('bttarih')
            
            if bstarih and bttarih and bttarih < bstarih:
                raise forms.ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = IzinForm(request.POST)
        if form.is_valid():
            izin = form.save(commit=False)
            izin.save()
            
            # Update remaining leave days (Requirement 3.5)
            personel = izin.sofor
            if izin.gun and personel.kalanizin is not None:
                personel.kalanizin -= izin.gun
                personel.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Yeni izin kaydı eklendi: {izin.sofor.adsoyad} - {izin.get_izin_display()}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'İzin kaydı başarıyla eklendi!')
            return redirect('izin_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = IzinForm()
    
    context = {
        'form': form,
        'title': 'Yeni İzin Ekle',
    }
    
    return render(request, 'izin/form.html', context)


# ============================================================================
# ARAÇ YÖNETİMİ (VEHICLE MANAGEMENT) - Task 11
# ============================================================================

@login_required(login_url='giris')
@check_giris_izni
def arac_listesi(request):
    """
    Display active vehicles list with filtering and warnings
    
    Requirements: 4.1, 4.2, 4.3, 4.9, 11.4
    """
    from core.utils import kontrol_muayene_tarihi
    
    # Get all active vehicles (not archived, not hidden)
    araclar = Arac.objects.filter(arsiv=False, gizle=False).order_by('plaka')
    
    # Get filter parameters
    kategori_filter = request.GET.get('kategori', '')
    arama = request.GET.get('arama', '')
    
    # Apply filters
    if kategori_filter:
        araclar = araclar.filter(kategori=kategori_filter)
    
    if arama:
        araclar = araclar.filter(
            models.Q(plaka__icontains=arama) |
            models.Q(marka__icontains=arama) |
            models.Q(zimmet__icontains=arama)
        )
    
    # Add warnings to each vehicle
    araclar_with_warnings = []
    for arac in araclar:
        warnings = kontrol_muayene_tarihi(arac)
        araclar_with_warnings.append({
            'arac': arac,
            'warnings': warnings
        })
    
    # Get category choices for filter dropdown
    kategoriler = Arac.KATEGORI_CHOICES
    
    context = {
        'araclar': araclar_with_warnings,
        'kategoriler': kategoriler,
        'kategori_filter': kategori_filter,
        'arama': arama,
        'title': 'Araç Listesi',
    }
    
    return render(request, 'arac/liste.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def arac_ekle(request):
    """
    Add new vehicle
    
    Requirements: 4.2, 4.3
    """
    from django import forms
    
    class AracForm(forms.ModelForm):
        class Meta:
            model = Arac
            fields = ['plaka', 'kategori', 'marka', 'zimmet', 'yolcusayisi', 
                     'muayene', 'sigorta', 'egzoz', 'takip']
            widgets = {
                'plaka': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '34 ABC 123'}),
                'kategori': forms.Select(attrs={'class': 'form-select'}),
                'marka': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ford Transit'}),
                'zimmet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Personel Adı'}),
                'yolcusayisi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '15'}),
                'muayene': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'sigorta': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'egzoz': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'takip': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }
            labels = {
                'plaka': 'Plaka',
                'kategori': 'Kategori',
                'marka': 'Marka/Model',
                'zimmet': 'Zimmetli Personel',
                'yolcusayisi': 'Yolcu Sayısı',
                'muayene': 'Muayene Tarihi',
                'sigorta': 'Sigorta Tarihi',
                'egzoz': 'Egzoz Muayene Tarihi',
                'takip': 'Takip Edilsin mi?',
            }
    
    if request.method == 'POST':
        form = AracForm(request.POST)
        if form.is_valid():
            arac = form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Yeni araç eklendi: {arac.plaka}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, f'Araç başarıyla eklendi: {arac.plaka}')
            return redirect('arac_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = AracForm()
    
    context = {
        'form': form,
        'title': 'Yeni Araç Ekle',
    }
    
    return render(request, 'arac/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def arac_duzenle(request, id):
    """
    Edit existing vehicle
    
    Requirements: 4.2, 4.3, 4.7
    """
    from django import forms
    from django.shortcuts import get_object_or_404
    
    arac = get_object_or_404(Arac, id=id)
    
    class AracForm(forms.ModelForm):
        class Meta:
            model = Arac
            fields = ['plaka', 'kategori', 'marka', 'zimmet', 'yolcusayisi', 
                     'muayene', 'sigorta', 'egzoz', 'takip', 'gizle']
            widgets = {
                'plaka': forms.TextInput(attrs={'class': 'form-control'}),
                'kategori': forms.Select(attrs={'class': 'form-select'}),
                'marka': forms.TextInput(attrs={'class': 'form-control'}),
                'zimmet': forms.TextInput(attrs={'class': 'form-control'}),
                'yolcusayisi': forms.TextInput(attrs={'class': 'form-control'}),
                'muayene': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'sigorta': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'egzoz': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'takip': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'gizle': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }
            labels = {
                'plaka': 'Plaka',
                'kategori': 'Kategori',
                'marka': 'Marka/Model',
                'zimmet': 'Zimmetli Personel',
                'yolcusayisi': 'Yolcu Sayısı',
                'muayene': 'Muayene Tarihi',
                'sigorta': 'Sigorta Tarihi',
                'egzoz': 'Egzoz Muayene Tarihi',
                'takip': 'Takip Edilsin mi?',
                'gizle': 'Gizle (Görev formlarında görünmesin)',
            }
    
    if request.method == 'POST':
        form = AracForm(request.POST, instance=arac)
        if form.is_valid():
            arac = form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Araç güncellendi: {arac.plaka}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, f'Araç başarıyla güncellendi: {arac.plaka}')
            return redirect('arac_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        # Pre-fill date fields in correct format
        initial_data = {}
        if arac.muayene:
            initial_data['muayene'] = arac.muayene.strftime('%Y-%m-%d')
        if arac.sigorta:
            initial_data['sigorta'] = arac.sigorta.strftime('%Y-%m-%d')
        if arac.egzoz:
            initial_data['egzoz'] = arac.egzoz.strftime('%Y-%m-%d')
        
        form = AracForm(instance=arac, initial=initial_data)
    
    context = {
        'form': form,
        'arac': arac,
        'title': f'Araç Düzenle: {arac.plaka}',
    }
    
    return render(request, 'arac/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def arac_arsivle(request, id):
    """
    Archive vehicle (set arsiv=True)
    
    Requirements: 4.5, 4.8
    """
    from django.shortcuts import get_object_or_404
    
    arac = get_object_or_404(Arac, id=id)
    arac.arsiv = True
    arac.save()
    
    # Create log entry
    try:
        Log.objects.create(
            sofor=request.user,
            islem=f"Araç arşivlendi: {arac.plaka}",
            ip=get_client_ip(request)
        )
    except Exception:
        pass
    
    messages.success(request, f'Araç arşivlendi: {arac.plaka}')
    return redirect('arac_listesi')


@login_required(login_url='giris')
@check_giris_izni
def arac_arsiv(request):
    """
    Display archived vehicles
    
    Requirements: 4.5, 4.8
    """
    # Get all archived vehicles
    araclar = Arac.objects.filter(arsiv=True).order_by('-id')
    
    # Get filter parameters
    kategori_filter = request.GET.get('kategori', '')
    arama = request.GET.get('arama', '')
    
    # Apply filters
    if kategori_filter:
        araclar = araclar.filter(kategori=kategori_filter)
    
    if arama:
        araclar = araclar.filter(
            models.Q(plaka__icontains=arama) |
            models.Q(marka__icontains=arama) |
            models.Q(zimmet__icontains=arama)
        )
    
    # Get category choices for filter dropdown
    kategoriler = Arac.KATEGORI_CHOICES
    
    context = {
        'araclar': araclar,
        'kategoriler': kategoriler,
        'kategori_filter': kategori_filter,
        'arama': arama,
        'title': 'Arşivlenmiş Araçlar',
    }
    
    return render(request, 'arac/arsiv.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def arac_arsivden_cikar(request, id):
    """
    Restore vehicle from archive (set arsiv=False)
    
    Requirements: 4.5, 4.8
    """
    from django.shortcuts import get_object_or_404
    
    arac = get_object_or_404(Arac, id=id)
    arac.arsiv = False
    arac.save()
    
    # Create log entry
    try:
        Log.objects.create(
            sofor=request.user,
            islem=f"Araç arşivden çıkarıldı: {arac.plaka}",
            ip=get_client_ip(request)
        )
    except Exception:
        pass
    
    messages.success(request, f'Araç arşivden çıkarıldı: {arac.plaka}')
    return redirect('arac_arsiv')



# ============================================================================
# GÖREVLENDIRME YÖNETİMİ (ASSIGNMENT MANAGEMENT) - Task 12
# Requirements: 6.1-6.5
# ============================================================================

from core.models import Gorevlendirme


@login_required(login_url='giris')
@check_giris_izni
def gorevlendirme_listesi(request):
    """
    Display assignments list
    Requirements: 6.1
    """
    # Base query
    gorevlendirmeler = Gorevlendirme.objects.select_related('sofor', 'arac')
    
    # If not admin, show only user's own records
    if not request.user.yonetici:
        gorevlendirmeler = gorevlendirmeler.filter(sofor=request.user)
    
    # Search and filtering
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    baslangic_tarih = request.GET.get('baslangic_tarih', '')
    bitis_tarih = request.GET.get('bitis_tarih', '')
    
    if search_query:
        gorevlendirmeler = gorevlendirmeler.filter(
            Q(sofor__adsoyad__icontains=search_query) |
            Q(gorev__icontains=search_query)
        )
    
    if personel_filter:
        gorevlendirmeler = gorevlendirmeler.filter(sofor_id=personel_filter)
    
    if baslangic_tarih:
        gorevlendirmeler = gorevlendirmeler.filter(bstarih__gte=baslangic_tarih)
    
    if bitis_tarih:
        gorevlendirmeler = gorevlendirmeler.filter(bstarih__lte=bitis_tarih)
    
    # Order by start date (newest first)
    gorevlendirmeler = gorevlendirmeler.order_by('-bstarih')
    
    # Pagination
    paginator = Paginator(gorevlendirmeler, 25)
    page = request.GET.get('page')
    
    try:
        gorevlendirmeler_page = paginator.page(page)
    except PageNotAnInteger:
        gorevlendirmeler_page = paginator.page(1)
    except EmptyPage:
        gorevlendirmeler_page = paginator.page(paginator.num_pages)
    
    # Get filter options
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    
    context = {
        'gorevlendirmeler': gorevlendirmeler_page,
        'personeller': personeller,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
    }
    
    return render(request, 'gorevlendirme/liste.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorevlendirme_ekle(request):
    """
    Add new assignment
    Requirements: 6.2
    """
    class GorevlendirmeForm(forms.ModelForm):
        class Meta:
            model = Gorevlendirme
            fields = ['sofor', 'bstarih', 'bttarih', 'arac', 'gorev']
            widgets = {
                'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'bttarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'sofor': forms.Select(attrs={'class': 'form-select'}),
                'arac': forms.Select(attrs={'class': 'form-select'}),
                'gorev': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }
            labels = {
                'sofor': 'Personel',
                'bstarih': 'Başlangıç Tarihi',
                'bttarih': 'Bitiş Tarihi',
                'arac': 'Araç',
                'gorev': 'Görev Açıklaması',
            }
        
        def clean(self):
            cleaned_data = super().clean()
            bstarih = cleaned_data.get('bstarih')
            bttarih = cleaned_data.get('bttarih')
            
            if bstarih and bttarih and bttarih < bstarih:
                raise forms.ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = GorevlendirmeForm(request.POST)
        if form.is_valid():
            gorevlendirme = form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Yeni görevlendirme eklendi: {gorevlendirme.sofor.adsoyad}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Görevlendirme başarıyla eklendi!')
            return redirect('gorevlendirme_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = GorevlendirmeForm()
    
    context = {
        'form': form,
        'title': 'Yeni Görevlendirme Ekle',
    }
    
    return render(request, 'gorevlendirme/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorevlendirme_duzenle(request, id):
    """
    Edit existing assignment
    Requirements: 6.3
    """
    from django.shortcuts import get_object_or_404
    
    gorevlendirme = get_object_or_404(Gorevlendirme, id=id)
    
    class GorevlendirmeForm(forms.ModelForm):
        class Meta:
            model = Gorevlendirme
            fields = ['sofor', 'bstarih', 'bttarih', 'arac', 'gorev']
            widgets = {
                'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'bttarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'sofor': forms.Select(attrs={'class': 'form-select'}),
                'arac': forms.Select(attrs={'class': 'form-select'}),
                'gorev': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }
            labels = {
                'sofor': 'Personel',
                'bstarih': 'Başlangıç Tarihi',
                'bttarih': 'Bitiş Tarihi',
                'arac': 'Araç',
                'gorev': 'Görev Açıklaması',
            }
        
        def clean(self):
            cleaned_data = super().clean()
            bstarih = cleaned_data.get('bstarih')
            bttarih = cleaned_data.get('bttarih')
            
            if bstarih and bttarih and bttarih < bstarih:
                raise forms.ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = GorevlendirmeForm(request.POST, instance=gorevlendirme)
        if form.is_valid():
            form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Görevlendirme güncellendi: {gorevlendirme.sofor.adsoyad}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Görevlendirme başarıyla güncellendi!')
            return redirect('gorevlendirme_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        # Format datetime for HTML5 input
        initial_data = {
            'bstarih': gorevlendirme.bstarih.strftime('%Y-%m-%dT%H:%M') if gorevlendirme.bstarih else '',
            'bttarih': gorevlendirme.bttarih.strftime('%Y-%m-%dT%H:%M') if gorevlendirme.bttarih else '',
        }
        form = GorevlendirmeForm(instance=gorevlendirme, initial=initial_data)
    
    context = {
        'form': form,
        'gorevlendirme': gorevlendirme,
        'title': 'Görevlendirme Düzenle',
    }
    
    return render(request, 'gorevlendirme/form.html', context)



@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorevlendirme_sil(request, id):
    """
    Delete assignment
    Requirements: 6.4
    """
    from django.shortcuts import get_object_or_404
    
    gorevlendirme = get_object_or_404(Gorevlendirme, id=id)
    
    if request.method == 'POST':
        personel_adi = gorevlendirme.sofor.adsoyad
        gorevlendirme.delete()
        
        # Create log entry
        try:
            Log.objects.create(
                sofor=request.user,
                islem=f"Görevlendirme silindi: {personel_adi}",
                ip=get_client_ip(request)
            )
        except Exception:
            pass
        
        messages.success(request, 'Görevlendirme başarıyla silindi!')
        return redirect('gorevlendirme_listesi')
    
    context = {
        'gorevlendirme': gorevlendirme,
    }
    
    return render(request, 'gorevlendirme/sil_onay.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def personele_gorevlendirme_ekle(request, personel_id):
    """
    Add assignment directly to a specific personnel
    Requirements: 6.5
    """
    from django.shortcuts import get_object_or_404
    
    personel = get_object_or_404(Personel, id=personel_id)
    
    class GorevlendirmeForm(forms.ModelForm):
        class Meta:
            model = Gorevlendirme
            fields = ['bstarih', 'bttarih', 'arac', 'gorev']
            widgets = {
                'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'bttarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'arac': forms.Select(attrs={'class': 'form-select'}),
                'gorev': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }
            labels = {
                'bstarih': 'Başlangıç Tarihi',
                'bttarih': 'Bitiş Tarihi',
                'arac': 'Araç',
                'gorev': 'Görev Açıklaması',
            }
        
        def clean(self):
            cleaned_data = super().clean()
            bstarih = cleaned_data.get('bstarih')
            bttarih = cleaned_data.get('bttarih')
            
            if bstarih and bttarih and bttarih < bstarih:
                raise forms.ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = GorevlendirmeForm(request.POST)
        if form.is_valid():
            gorevlendirme = form.save(commit=False)
            gorevlendirme.sofor = personel
            gorevlendirme.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Görevlendirme eklendi: {personel.adsoyad}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, f'{personel.adsoyad} için görevlendirme eklendi!')
            return redirect('gorevlendirme_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = GorevlendirmeForm()
    
    context = {
        'form': form,
        'personel': personel,
        'title': f'{personel.adsoyad} için Görevlendirme Ekle',
    }
    
    return render(request, 'gorevlendirme/form.html', context)


# ============================================================================
# MALZEME YÖNETİMİ (MATERIAL MANAGEMENT) - Task 12
# Requirements: 7.1-7.4
# ============================================================================

from core.models import Malzeme


@login_required(login_url='giris')
@check_giris_izni
def malzeme_listesi(request):
    """
    Display materials list
    Requirements: 7.1
    """
    # Base query
    malzemeler = Malzeme.objects.select_related('sofor')
    
    # If not admin, show only user's own records
    if not request.user.yonetici:
        malzemeler = malzemeler.filter(sofor=request.user)
    
    # Search and filtering
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    baslangic_tarih = request.GET.get('baslangic_tarih', '')
    bitis_tarih = request.GET.get('bitis_tarih', '')
    
    if search_query:
        malzemeler = malzemeler.filter(
            Q(sofor__adsoyad__icontains=search_query) |
            Q(aciklama__icontains=search_query)
        )
    
    if personel_filter:
        malzemeler = malzemeler.filter(sofor_id=personel_filter)
    
    if baslangic_tarih:
        malzemeler = malzemeler.filter(bstarih__gte=baslangic_tarih)
    
    if bitis_tarih:
        malzemeler = malzemeler.filter(bstarih__lte=bitis_tarih)
    
    # Order by date (newest first)
    malzemeler = malzemeler.order_by('-bstarih')
    
    # Pagination
    paginator = Paginator(malzemeler, 25)
    page = request.GET.get('page')
    
    try:
        malzemeler_page = paginator.page(page)
    except PageNotAnInteger:
        malzemeler_page = paginator.page(1)
    except EmptyPage:
        malzemeler_page = paginator.page(paginator.num_pages)
    
    # Get filter options
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    
    context = {
        'malzemeler': malzemeler_page,
        'personeller': personeller,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
    }
    
    return render(request, 'malzeme/liste.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def malzeme_ekle(request):
    """
    Add new material record
    Requirements: 7.2
    """
    class MalzemeForm(forms.ModelForm):
        class Meta:
            model = Malzeme
            fields = ['sofor', 'bstarih', 'aciklama']
            widgets = {
                'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'sofor': forms.Select(attrs={'class': 'form-select'}),
                'aciklama': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }
            labels = {
                'sofor': 'Teslim Alan Personel',
                'bstarih': 'Teslim Tarihi',
                'aciklama': 'Malzeme Detayları',
            }
    
    if request.method == 'POST':
        form = MalzemeForm(request.POST)
        if form.is_valid():
            malzeme = form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Yeni malzeme kaydı eklendi: {malzeme.sofor.adsoyad}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Malzeme kaydı başarıyla eklendi!')
            return redirect('malzeme_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = MalzemeForm()
    
    context = {
        'form': form,
        'title': 'Yeni Malzeme Kaydı Ekle',
    }
    
    return render(request, 'malzeme/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def malzeme_duzenle(request, id):
    """
    Edit existing material record
    Requirements: 7.3
    """
    from django.shortcuts import get_object_or_404
    
    malzeme = get_object_or_404(Malzeme, id=id)
    
    class MalzemeForm(forms.ModelForm):
        class Meta:
            model = Malzeme
            fields = ['sofor', 'bstarih', 'aciklama']
            widgets = {
                'bstarih': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                'sofor': forms.Select(attrs={'class': 'form-select'}),
                'aciklama': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }
            labels = {
                'sofor': 'Teslim Alan Personel',
                'bstarih': 'Teslim Tarihi',
                'aciklama': 'Malzeme Detayları',
            }
    
    if request.method == 'POST':
        form = MalzemeForm(request.POST, instance=malzeme)
        if form.is_valid():
            form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Malzeme kaydı güncellendi: {malzeme.sofor.adsoyad}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Malzeme kaydı başarıyla güncellendi!')
            return redirect('malzeme_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        # Format datetime for HTML5 input
        initial_data = {
            'bstarih': malzeme.bstarih.strftime('%Y-%m-%dT%H:%M') if malzeme.bstarih else '',
        }
        form = MalzemeForm(instance=malzeme, initial=initial_data)
    
    context = {
        'form': form,
        'malzeme': malzeme,
        'title': 'Malzeme Kaydı Düzenle',
    }
    
    return render(request, 'malzeme/form.html', context)



@login_required(login_url='giris')
@check_giris_izni
@admin_required
def malzeme_sil(request, id):
    """
    Delete material record
    Requirements: 7.4
    """
    from django.shortcuts import get_object_or_404
    
    malzeme = get_object_or_404(Malzeme, id=id)
    
    if request.method == 'POST':
        personel_adi = malzeme.sofor.adsoyad
        malzeme.delete()
        
        # Create log entry
        try:
            Log.objects.create(
                sofor=request.user,
                islem=f"Malzeme kaydı silindi: {personel_adi}",
                ip=get_client_ip(request)
            )
        except Exception:
            pass
        
        messages.success(request, 'Malzeme kaydı başarıyla silindi!')
        return redirect('malzeme_listesi')
    
    context = {
        'malzeme': malzeme,
    }
    
    return render(request, 'malzeme/sil_onay.html', context)


# ============================================================================
# GÖREV YERİ YÖNETİMİ (TASK LOCATION MANAGEMENT) - Task 12
# Requirements: 5.1-5.6
# ============================================================================

from core.models import GorevYeri
from django.db.models import Count


@login_required(login_url='giris')
@check_giris_izni
def gorev_yeri_listesi(request):
    """
    Display task locations list with task count
    Requirements: 5.1, 5.6
    """
    # Get all task locations with task count
    gorev_yerleri = GorevYeri.objects.annotate(
        gorev_sayisi=Count('gorev', filter=Q(gorev__gizle=False))
    ).order_by('ad')
    
    # Search filtering
    search_query = request.GET.get('q', '')
    
    if search_query:
        gorev_yerleri = gorev_yerleri.filter(ad__icontains=search_query)
    
    # Pagination
    paginator = Paginator(gorev_yerleri, 25)
    page = request.GET.get('page')
    
    try:
        gorev_yerleri_page = paginator.page(page)
    except PageNotAnInteger:
        gorev_yerleri_page = paginator.page(1)
    except EmptyPage:
        gorev_yerleri_page = paginator.page(paginator.num_pages)
    
    context = {
        'gorev_yerleri': gorev_yerleri_page,
        'search_query': search_query,
    }
    
    return render(request, 'gorev_yeri/liste.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorev_yeri_ekle(request):
    """
    Add new task location
    Requirements: 5.2
    """
    class GorevYeriForm(forms.ModelForm):
        class Meta:
            model = GorevYeri
            fields = ['ad']
            widgets = {
                'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Görev yeri adı'}),
            }
            labels = {
                'ad': 'Görev Yeri Adı',
            }
    
    if request.method == 'POST':
        form = GorevYeriForm(request.POST)
        if form.is_valid():
            gorev_yeri = form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Yeni görev yeri eklendi: {gorev_yeri.ad}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, f'Görev yeri başarıyla eklendi: {gorev_yeri.ad}')
            return redirect('gorev_yeri_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = GorevYeriForm()
    
    context = {
        'form': form,
        'title': 'Yeni Görev Yeri Ekle',
    }
    
    return render(request, 'gorev_yeri/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorev_yeri_duzenle(request, id):
    """
    Edit existing task location
    Requirements: 5.3
    """
    from django.shortcuts import get_object_or_404
    
    gorev_yeri = get_object_or_404(GorevYeri, id=id)
    
    class GorevYeriForm(forms.ModelForm):
        class Meta:
            model = GorevYeri
            fields = ['ad']
            widgets = {
                'ad': forms.TextInput(attrs={'class': 'form-control'}),
            }
            labels = {
                'ad': 'Görev Yeri Adı',
            }
    
    if request.method == 'POST':
        form = GorevYeriForm(request.POST, instance=gorev_yeri)
        if form.is_valid():
            form.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Görev yeri güncellendi: {gorev_yeri.ad}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, f'Görev yeri başarıyla güncellendi: {gorev_yeri.ad}')
            return redirect('gorev_yeri_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = GorevYeriForm(instance=gorev_yeri)
    
    context = {
        'form': form,
        'gorev_yeri': gorev_yeri,
        'title': f'Görev Yeri Düzenle: {gorev_yeri.ad}',
    }
    
    return render(request, 'gorev_yeri/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def gorev_yeri_sil(request, id):
    """
    Delete task location (with related tasks check)
    Requirements: 5.4
    """
    from django.shortcuts import get_object_or_404
    
    gorev_yeri = get_object_or_404(GorevYeri, id=id)
    
    # Check if there are related tasks
    related_gorevler = Gorev.objects.filter(yurt=gorev_yeri, gizle=False).count()
    
    if request.method == 'POST':
        if related_gorevler > 0:
            messages.error(request, f'Bu görev yeri silinemez! {related_gorevler} adet görev kaydı ile ilişkili.')
            return redirect('gorev_yeri_listesi')
        
        gorev_yeri_adi = gorev_yeri.ad
        gorev_yeri.delete()
        
        # Create log entry
        try:
            Log.objects.create(
                sofor=request.user,
                islem=f"Görev yeri silindi: {gorev_yeri_adi}",
                ip=get_client_ip(request)
            )
        except Exception:
            pass
        
        messages.success(request, f'Görev yeri başarıyla silindi: {gorev_yeri_adi}')
        return redirect('gorev_yeri_listesi')
    
    context = {
        'gorev_yeri': gorev_yeri,
        'related_gorevler': related_gorevler,
    }
    
    return render(request, 'gorev_yeri/sil_onay.html', context)


@login_required(login_url='giris')
@check_giris_izni
def gorev_yeri_detay(request, id):
    """
    Display task location details with all related tasks
    Requirements: 5.6
    """
    from django.shortcuts import get_object_or_404
    
    gorev_yeri = get_object_or_404(GorevYeri, id=id)
    
    # Get all tasks for this location
    gorevler = Gorev.objects.filter(
        yurt=gorev_yeri,
        gizle=False
    ).select_related('sofor', 'arac').order_by('-bstarih')
    
    # Pagination
    paginator = Paginator(gorevler, 25)
    page = request.GET.get('page')
    
    try:
        gorevler_page = paginator.page(page)
    except PageNotAnInteger:
        gorevler_page = paginator.page(1)
    except EmptyPage:
        gorevler_page = paginator.page(paginator.num_pages)
    
    context = {
        'gorev_yeri': gorev_yeri,
        'gorevler': gorevler_page,
    }
    
    return render(request, 'gorev_yeri/detay.html', context)


# ============================================================================
# PERSONEL YÖNETİMİ (PERSONNEL MANAGEMENT)
# Requirements: 8.1-8.7
# ============================================================================

@login_required(login_url='giris')
@check_giris_izni
@admin_required
def personel_listesi(request):
    """
    Display personnel list
    Requirements: 8.1
    """
    # Base query - all active personnel
    personeller = Personel.objects.all()
    
    # Search and filtering
    search_query = request.GET.get('q', '')
    durum_filter = request.GET.get('durum', '')
    
    if search_query:
        personeller = personeller.filter(
            Q(adsoyad__icontains=search_query) |
            Q(kullaniciadi__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if durum_filter == 'aktif':
        personeller = personeller.filter(is_active=True, girisizni=False)
    elif durum_filter == 'pasif':
        personeller = personeller.filter(Q(is_active=False) | Q(girisizni=True))
    elif durum_filter == 'yonetici':
        personeller = personeller.filter(yonetici=True)
    
    # Order by name
    personeller = personeller.order_by('adsoyad')
    
    # Pagination
    paginator = Paginator(personeller, 25)
    page = request.GET.get('page')
    
    try:
        personeller_page = paginator.page(page)
    except PageNotAnInteger:
        personeller_page = paginator.page(1)
    except EmptyPage:
        personeller_page = paginator.page(paginator.num_pages)
    
    context = {
        'personeller': personeller_page,
        'search_query': search_query,
        'durum_filter': durum_filter,
    }
    
    return render(request, 'personel/liste.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def personel_ekle(request):
    """
    Add new personnel
    Requirements: 8.2
    """
    class PersonelForm(forms.ModelForm):
        sifre = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
            label='Şifre',
            required=True
        )
        sifre_tekrar = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
            label='Şifre Tekrar',
            required=True
        )
        
        class Meta:
            model = Personel
            fields = ['adsoyad', 'kullaniciadi', 'email', 'yonetici', 'gg', 'girisizni', 'is_active', 'kalanizin']
            widgets = {
                'adsoyad': forms.TextInput(attrs={'class': 'form-control'}),
                'kullaniciadi': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
                'yonetici': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'gg': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'girisizni': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'kalanizin': forms.NumberInput(attrs={'class': 'form-control'}),
            }
            labels = {
                'adsoyad': 'Ad Soyad',
                'kullaniciadi': 'Kullanıcı Adı',
                'email': 'E-posta',
                'yonetici': 'Yönetici',
                'gg': 'Gizli Kullanıcı',
                'girisizni': 'Giriş İzni Yok',
                'is_active': 'Aktif',
                'kalanizin': 'Kalan İzin (Gün)',
            }
        
        def clean(self):
            cleaned_data = super().clean()
            sifre = cleaned_data.get('sifre')
            sifre_tekrar = cleaned_data.get('sifre_tekrar')
            
            # Validate password match
            if sifre and sifre_tekrar and sifre != sifre_tekrar:
                raise forms.ValidationError('Şifreler eşleşmiyor!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = PersonelForm(request.POST)
        if form.is_valid():
            personel = form.save(commit=False)
            # Set password with MD5 hashing (Requirement 8.4)
            personel.set_password(form.cleaned_data['sifre'])
            # Set is_staff if yonetici (Requirement 8.5)
            if personel.yonetici:
                personel.is_staff = True
            personel.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Yeni personel eklendi: {personel.adsoyad} ({personel.kullaniciadi})",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Personel başarıyla eklendi!')
            return redirect('personel_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = PersonelForm()
    
    context = {
        'form': form,
        'title': 'Yeni Personel Ekle',
    }
    
    return render(request, 'personel/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def personel_duzenle(request, id):
    """
    Edit existing personnel
    Requirements: 8.3
    """
    from django.shortcuts import get_object_or_404
    
    personel = get_object_or_404(Personel, id=id)
    
    class PersonelForm(forms.ModelForm):
        class Meta:
            model = Personel
            fields = ['adsoyad', 'kullaniciadi', 'email', 'yonetici', 'gg', 'girisizni', 'is_active', 'kalanizin']
            widgets = {
                'adsoyad': forms.TextInput(attrs={'class': 'form-control'}),
                'kullaniciadi': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
                'yonetici': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'gg': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'girisizni': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'kalanizin': forms.NumberInput(attrs={'class': 'form-control'}),
            }
            labels = {
                'adsoyad': 'Ad Soyad',
                'kullaniciadi': 'Kullanıcı Adı',
                'email': 'E-posta',
                'yonetici': 'Yönetici',
                'gg': 'Gizli Kullanıcı',
                'girisizni': 'Giriş İzni Yok',
                'is_active': 'Aktif',
                'kalanizin': 'Kalan İzin (Gün)',
            }
    
    if request.method == 'POST':
        form = PersonelForm(request.POST, instance=personel)
        if form.is_valid():
            personel = form.save(commit=False)
            # Update is_staff based on yonetici (Requirement 8.5)
            if personel.yonetici:
                personel.is_staff = True
            else:
                personel.is_staff = False
            personel.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Personel bilgileri güncellendi: {personel.adsoyad} ({personel.kullaniciadi})",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Personel bilgileri başarıyla güncellendi!')
            return redirect('personel_listesi')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = PersonelForm(instance=personel)
    
    context = {
        'form': form,
        'personel': personel,
        'title': 'Personel Düzenle',
    }
    
    return render(request, 'personel/form.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def personel_sil(request, id):
    """
    Delete personnel (with related records check)
    Requirements: 8.6
    """
    from django.shortcuts import get_object_or_404
    
    personel = get_object_or_404(Personel, id=id)
    
    # Check for related records (Requirement 8.6)
    gorev_count = Gorev.objects.filter(sofor=personel).count()
    mesai_count = Mesai.objects.filter(sofor=personel).count()
    izin_count = Izin.objects.filter(sofor=personel).count()
    
    has_related_records = gorev_count > 0 or mesai_count > 0 or izin_count > 0
    
    if request.method == 'POST':
        if has_related_records:
            # Don't delete, just deactivate
            personel.is_active = False
            personel.girisizni = True
            personel.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Personel devre dışı bırakıldı: {personel.adsoyad} ({personel.kullaniciadi})",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.warning(request, 'Personel ilişkili kayıtları olduğu için silinemedi, ancak devre dışı bırakıldı.')
        else:
            # Safe to delete
            personel_name = personel.adsoyad
            personel_username = personel.kullaniciadi
            personel.delete()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Personel silindi: {personel_name} ({personel_username})",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            messages.success(request, 'Personel başarıyla silindi!')
        
        return redirect('personel_listesi')
    
    context = {
        'personel': personel,
        'gorev_count': gorev_count,
        'mesai_count': mesai_count,
        'izin_count': izin_count,
        'has_related_records': has_related_records,
    }
    
    return render(request, 'personel/sil_onay.html', context)


@login_required(login_url='giris')
@check_giris_izni
def sifre_degistir(request):
    """
    Change user password
    Requirements: 8.4
    """
    class SifreForm(forms.Form):
        eski_sifre = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
            label='Eski Şifre',
            required=True
        )
        yeni_sifre = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
            label='Yeni Şifre',
            required=True,
            min_length=6,
            help_text='En az 6 karakter olmalıdır.'
        )
        yeni_sifre_tekrar = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
            label='Yeni Şifre Tekrar',
            required=True
        )
        
        def __init__(self, user, *args, **kwargs):
            self.user = user
            super().__init__(*args, **kwargs)
        
        def clean_eski_sifre(self):
            eski_sifre = self.cleaned_data.get('eski_sifre')
            if not self.user.check_password(eski_sifre):
                raise forms.ValidationError('Eski şifre hatalı!')
            return eski_sifre
        
        def clean(self):
            cleaned_data = super().clean()
            yeni_sifre = cleaned_data.get('yeni_sifre')
            yeni_sifre_tekrar = cleaned_data.get('yeni_sifre_tekrar')
            
            # Validate password match
            if yeni_sifre and yeni_sifre_tekrar and yeni_sifre != yeni_sifre_tekrar:
                raise forms.ValidationError('Yeni şifreler eşleşmiyor!')
            
            return cleaned_data
    
    if request.method == 'POST':
        form = SifreForm(request.user, request.POST)
        if form.is_valid():
            # Change password with MD5 hashing (Requirement 8.4)
            request.user.set_password(form.cleaned_data['yeni_sifre'])
            request.user.save()
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Şifre değiştirildi",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            # Re-login user with new password
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Şifreniz başarıyla değiştirildi!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = SifreForm(request.user)
    
    context = {
        'form': form,
        'title': 'Şifre Değiştir',
    }
    
    return render(request, 'personel/sifre_degistir.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def personel_detay(request, id):
    """
    Display personnel details with related records
    Requirements: 8.1
    """
    from django.shortcuts import get_object_or_404
    
    personel = get_object_or_404(Personel, id=id)
    
    # Get related records
    gorevler = Gorev.objects.filter(sofor=personel, gizle=False).order_by('-bstarih')[:10]
    mesailer = Mesai.objects.filter(sofor=personel).order_by('-bstarih')[:10]
    izinler = Izin.objects.filter(sofor=personel).order_by('-bstarih')[:10]
    
    # Calculate statistics
    toplam_gorev = Gorev.objects.filter(sofor=personel, gizle=False).count()
    toplam_mesai = Mesai.objects.filter(sofor=personel).count()
    toplam_izin = Izin.objects.filter(sofor=personel).count()
    
    context = {
        'personel': personel,
        'gorevler': gorevler,
        'mesailer': mesailer,
        'izinler': izinler,
        'toplam_gorev': toplam_gorev,
        'toplam_mesai': toplam_mesai,
        'toplam_izin': toplam_izin,
    }
    
    return render(request, 'personel/detay.html', context)


# ============================================================================
# LOG VE SİSTEM BİLGİLERİ (LOG AND SYSTEM INFORMATION)
# Requirements: 9.1, 9.3, 9.4, 9.5
# ============================================================================

@login_required(login_url='giris')
@check_giris_izni
@admin_required
def log_kayitlari(request):
    """
    Display system log records
    Requirements: 9.1, 9.5
    """
    from core.models import Log, Personel
    from django.core.paginator import Paginator
    
    # Base query - all logs ordered by newest first
    loglar = Log.objects.select_related('sofor').order_by('-tarih')
    
    # Search and filtering (Requirement 9.5)
    search_query = request.GET.get('q', '')
    personel_filter = request.GET.get('personel', '')
    baslangic_tarih = request.GET.get('baslangic_tarih', '')
    bitis_tarih = request.GET.get('bitis_tarih', '')
    
    if search_query:
        loglar = loglar.filter(
            Q(islem__icontains=search_query) |
            Q(sofor__adsoyad__icontains=search_query) |
            Q(ip__icontains=search_query)
        )
    
    if personel_filter:
        loglar = loglar.filter(sofor_id=personel_filter)
    
    if baslangic_tarih:
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        try:
            start_date = timezone.make_aware(parse_datetime(baslangic_tarih + ' 00:00:00'))
            loglar = loglar.filter(tarih__gte=start_date)
        except:
            pass
    
    if bitis_tarih:
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        try:
            end_date = timezone.make_aware(parse_datetime(bitis_tarih + ' 23:59:59'))
            loglar = loglar.filter(tarih__lte=end_date)
        except:
            pass
    
    # Pagination
    paginator = Paginator(loglar, 50)  # 50 logs per page
    page = request.GET.get('page')
    
    try:
        loglar_page = paginator.page(page)
    except PageNotAnInteger:
        loglar_page = paginator.page(1)
    except EmptyPage:
        loglar_page = paginator.page(paginator.num_pages)
    
    # Get filter options
    personeller = Personel.objects.filter(is_active=True).order_by('adsoyad')
    
    context = {
        'loglar': loglar_page,
        'personeller': personeller,
        'search_query': search_query,
        'personel_filter': personel_filter,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
    }
    
    return render(request, 'sistem/log_kayitlari.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def sistem_bilgileri(request):
    """
    Display system information and statistics
    Requirements: 9.3
    """
    import django
    import sys
    import os
    from django.conf import settings
    from core.models import Personel, Arac, Gorev, Mesai, Izin, GorevYeri, Gorevlendirme, Malzeme, Log
    
    # Django and Python version info
    django_version = django.get_version()
    python_version = sys.version
    
    # Database information
    db_path = settings.DATABASES['default']['NAME']
    db_size = 0
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # Convert to MB
    
    # Record counts
    record_counts = {
        'Personel': Personel.objects.count(),
        'Araç': Arac.objects.count(),
        'Görev': Gorev.objects.count(),
        'Mesai': Mesai.objects.count(),
        'İzin': Izin.objects.count(),
        'Görev Yeri': GorevYeri.objects.count(),
        'Görevlendirme': Gorevlendirme.objects.count(),
        'Malzeme': Malzeme.objects.count(),
        'Log': Log.objects.count(),
    }
    
    # Active records
    active_counts = {
        'Aktif Personel': Personel.objects.filter(is_active=True, girisizni=False).count(),
        'Aktif Araç': Arac.objects.filter(arsiv=False, gizle=False).count(),
        'Aktif Görev': Gorev.objects.filter(gizle=False, durum__isnull=True).count(),
    }
    
    # Recent activity (last 24 hours)
    from django.utils import timezone
    from datetime import timedelta
    last_24h = timezone.now() - timedelta(hours=24)
    recent_activity = {
        'Son 24 Saat Log': Log.objects.filter(tarih__gte=last_24h).count(),
        'Son 24 Saat Görev': Gorev.objects.filter(bstarih__gte=last_24h, gizle=False).count(),
    }
    
    context = {
        'django_version': django_version,
        'python_version': python_version,
        'db_path': db_path,
        'db_size': f'{db_size:.2f} MB',
        'record_counts': record_counts,
        'active_counts': active_counts,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'sistem/sistem_bilgileri.html', context)


@login_required(login_url='giris')
@check_giris_izni
@admin_required
def yedek_al(request):
    """
    Create and download database backup
    Requirements: 9.4
    """
    import os
    import shutil
    from django.conf import settings
    from django.http import FileResponse, HttpResponse
    from datetime import datetime
    
    if request.method == 'POST':
        try:
            # Get database path
            db_path = settings.DATABASES['default']['NAME']
            
            if not os.path.exists(db_path):
                messages.error(request, 'Veritabanı dosyası bulunamadı!')
                return redirect('yedek_al')
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'gorev_takip_yedek_{timestamp}.sqlite3'
            
            # Create temporary backup file
            backup_path = os.path.join(settings.BASE_DIR, backup_filename)
            shutil.copy2(db_path, backup_path)
            
            # Create log entry
            try:
                Log.objects.create(
                    sofor=request.user,
                    islem=f"Veritabanı yedeği alındı: {backup_filename}",
                    ip=get_client_ip(request)
                )
            except Exception:
                pass
            
            # Send file as download
            response = FileResponse(open(backup_path, 'rb'), as_attachment=True, filename=backup_filename)
            
            # Schedule file deletion after sending (cleanup)
            # Note: In production, consider using a background task for cleanup
            try:
                os.remove(backup_path)
            except:
                pass
            
            messages.success(request, f'Yedek başarıyla oluşturuldu: {backup_filename}')
            return response
            
        except Exception as e:
            messages.error(request, f'Yedek alınırken hata oluştu: {str(e)}')
            return redirect('yedek_al')
    
    # GET request - show backup page
    from django.conf import settings
    import os
    
    db_path = settings.DATABASES['default']['NAME']
    db_size = 0
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # Convert to MB
    
    context = {
        'db_path': db_path,
        'db_size': f'{db_size:.2f} MB',
    }
    
    return render(request, 'sistem/yedek_al.html', context)
