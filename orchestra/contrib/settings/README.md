```python
>>> from orchestra.contrib.settings import Setting, parser
>>> Setting.settings['TASKS_BACKEND'].value
'thread'
>>> Setting.settings['TASKS_BACKEND'].default
'thread'
>>> Setting.settings['TASKS_BACKEND'].validate_value('rata')
Traceback (most recent call last):
  File "<console>", line 1, in <module>
  File "/home/orchestra/django-orchestra/orchestra/contrib/settings/__init__.py", line 99, in validate_value
    raise ValidationError("'%s' not in '%s'" % (value, ', '.join(choices)))
django.core.exceptions.ValidationError: ["'rata' not in 'thread, process, celery'"]
>>> parser.apply({'TASKS_BACKEND': 'process'})
...
>>> parser.apply({'TASKS_BACKEND': parser.Remove()})
...
```

