from django.utils import timezone


def tashkent_now():
    return timezone.localtime(timezone.now())


def tashkent_now_str():
    return timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
