# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from django.conf import settings

from appconf import AppConf


class EmailQueueConf(AppConf):
    # The email backend to use. For possible shortcuts see django.core.mail.
    # The default is to use the SMTP backend.
    # Third-party backends can be specified by providing a Python path
    # to a module that defines an EmailBackend class.
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    # Per minute maximum number of messages to be sent
    THROTTLE = 30

    # Sleep time between queue checkup
    SLEEP_TIME = 15

    class Meta:
        prefix = 'email_queue'
