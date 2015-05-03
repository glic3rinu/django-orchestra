import os


# Rename module to handler.py
class CronHandler(object):
    def __init__(self, filename):
        self.content = None
        self.filename = filename
    
    def read(self):
        comments = []
        self.content = []
        with open(self.filename, 'r') as handler:
            for line in handler.readlines():
                line = line.strip()
                if line.startswith('#'):
                    comments.append(line)
                else:
                    schedule = line.split()[:5]
                    command = ' '.join(line.split()[5:]).strip()
                    self.content.append((schedule, command, comments))
                    comments = []
    
    def save(self, backup=True):
        if self.content is None:
            raise Exception("First read() the cron file!")
        if backup:
            os.rename(self.filename, self.filename + '.backup')
        with open(self.filename, 'w') as handler:
            handler.write('\n'.join(self.content))
            handler.truncate()
        self.reload()
    
    def reload(self):
        pass
        # TODO
    
    def remove(self, command):
        if self.content is None:
            raise Exception("First read() the cron file!")
        new_content = []
        for c_schedule, c_command, c_comments in self.content:
            if command != c_command:
                new_content.append((c_schedule, c_command, c_comments))
        self.content = new_content
    
    def add_or_update(self, schedule, command, comments=None):
        """ if content contains an equal command, its schedule is updated """
        if self.content is None:
            raise Exception("First read() the cron file!")
        new_content = []
        replaced = False
        for c_schedule, c_command, c_comments in self.content:
            if command == c_command:
                replaced = True
                new_content.append((schedule, command, comments or c_comments))
            else:
                new_content.append((c_schedule, c_command, c_comments))
        if not replaced:
            new_content.append((schedule, command, comments or []))
        self.content = new_content
