from celery.task import task
from django.core.cache import cache
from django import template
from django.utils.hashcompat import md5_constructor as md5
import random
import settings


@task(name="daemon_execution", max_retries=10)  
def execute(daemon_instance_id, object_id, template_file, method, extra_context={}, lock=True):
    """ 
        Execute django templates using provided method.
        If lock=True we ensure that a template is executed on at a time per server, 
            avoiding concurrency problems with scripts that are performing write operations. Based on:
            http://ask.github.com/celery/cookbook/tasks.html#ensuring-a-task-is-only-executed-one-at-a-time
    """ 
    # extra_context might contain {'var_name': function_call(instance), 'var_name': 'content'}
    if template_file:
        if lock:
            # The cache key consists of the task name, MD5 digest of the script file name and daemon instance id
            template_md5 = md5(template_file).hexdigest()
            lock_id = "%s-lock-%s-%s" % (execute.name, template_md5, daemon_instance_id)

            # cache.add fails if the key already exists
            acquire_lock = lambda: cache.add(lock_id, "true", settings.DAEMONS_LOCK_EXPIRE)
            release_lock = lambda: cache.delete(lock_id)

        if not lock or acquire_lock():
            from models import DaemonInstance
            
            daemon_instance = DaemonInstance.objects.get(pk=daemon_instance_id)
            obj_model = daemon_instance.daemon.content_type.model_class()

            context = {'object': obj_model.objects.get(pk=object_id),
                       'objects': obj_model.objects.all() }
                       
            for key, value in extra_context.iteritems():
                # if it's a function, call it
                if hasattr(value, '__call__'):
                    context[key] = value(obj)
                else: context[key] = value

            f = open(template_file, 'r+')
            script = template.loader.get_template_from_string(f.read()).render(template.Context(context))
            f.close()
        
            try: 
                result = method.execute(daemon_instance, script)
            finally: 
                if lock: release_lock()
            
            return result
            
        # retry the task within an exponential scale and preventing more colisions adding randomness
        base = (execute.request.retries+1) ** 2
        variation = base/2 * random.random()
        execute.retry(args=[daemon_instance_id, object_id, template_file, method],
                      kwargs={'extra_context':extra_context},
                      countdown=(base + variation))
                      
    return
