=====
Usage
=====

To use Django email queue in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_email_queue.apps.DjangoEmailQueueConfig',
        ...
    )

Add Django email queue's URL patterns:

.. code-block:: python

    from django_email_queue import urls as django_email_queue_urls


    urlpatterns = [
        ...
        url(r'^', include(django_email_queue_urls)),
        ...
    ]
