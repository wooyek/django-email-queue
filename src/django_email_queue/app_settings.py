# coding=utf-8

DJANGO_EMAIL_QUEUE_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DJANGO_EMAIL_QUEUE_EMAIL_BACKEND.__doc__ = """
The email backend to use. For possible shortcuts see django.core.mail.
The default is to use the SMTP backend.
Third-party backends can be specified by providing a Python path
to a module that defines an EmailBackend class.
"""

DJANGO_EMAIL_QUEUE_EAGER = False
DJANGO_EMAIL_QUEUE_EAGER.__doc__ = """
Don't queue messages store them and send them immediately
Set this to True if you are going to use
`djcelery_email.backends.CeleryEmailBackend` as EMAIL_QUEUE_EMAIL_BACKEND.
"""

# THROTTLE = 30
# THROTTLE.__doc__ ="""Per minute maximum number of messages to be sent"""

DJANGO_EMAIL_QUEUE_SLEEP_TIME = 15
DJANGO_EMAIL_QUEUE_SLEEP_TIME.__doc__ = """Sleep time between queue checkup"""
