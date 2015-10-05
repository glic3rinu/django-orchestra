#import re


#class CronTab(object):
#    pass


#class ParseException(Exception):
#    """Raised by crontab_parser when the input can't be parsed."""


## https://github.com/celery/celery/blob/master/celery/schedules.py
#class CrontabParser(object):
#    """Parser for crontab expressions. Any expression of the form 'groups'
#    (see BNF grammar below) is accepted and expanded to a set of numbers.
#    These numbers represent the units of time that the crontab needs to
#    run on::
#        digit   :: '0'..'9'
#        dow     :: 'a'..'z'
#        number  :: digit+ | dow+
#        steps   :: number
#        range   :: number ( '-' number ) ?
#        numspec :: '*' | range
#        expr    :: numspec ( '/' steps ) ?
#        groups  :: expr ( ',' expr ) *
#    The parser is a general purpose one, useful for parsing hours, minutes and
#    day_of_week expressions.  Example usage::
#        >>> minutes = crontab_parser(60).parse('*/15')
#        [0, 15, 30, 45]
#        >>> hours = crontab_parser(24).parse('*/4')
#        [0, 4, 8, 12, 16, 20]
#        >>> day_of_week = crontab_parser(7).parse('*')
#        [0, 1, 2, 3, 4, 5, 6]
#    It can also parse day_of_month and month_of_year expressions if initialized
#    with an minimum of 1.  Example usage::
#        >>> days_of_month = crontab_parser(31, 1).parse('*/3')
#        [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31]
#        >>> months_of_year = crontab_parser(12, 1).parse('*/2')
#        [1, 3, 5, 7, 9, 11]
#        >>> months_of_year = crontab_parser(12, 1).parse('2-12/2')
#        [2, 4, 6, 8, 10, 12]
#    The maximum possible expanded value returned is found by the formula::
#        max_ + min_ - 1
#    """
#    ParseException = ParseException

#    _range = r'(\w+?)-(\w+)'
#    _steps = r'/(\w+)?'
#    _star = r'\*'

#    def __init__(self, max_=60, min_=0):
#        self.max_ = max_
#        self.min_ = min_
#        self.pats = (
#            (re.compile(self._range + self._steps), self._range_steps),
#            (re.compile(self._range), self._expand_range),
#            (re.compile(self._star + self._steps), self._star_steps),
#            (re.compile('^' + self._star + '$'), self._expand_star),
#        )

#    def parse(self, spec):
#        acc = set()
#        for part in spec.split(','):
#            if not part:
#                raise self.ParseException('empty part')
#            acc |= set(self._parse_part(part))
#        return acc

#    def _parse_part(self, part):
#        for regex, handler in self.pats:
#            m = regex.match(part)
#            if m:
#                return handler(m.groups())
#        return self._expand_range((part, ))

#    def _expand_range(self, toks):
#        fr = self._expand_number(toks[0])
#        if len(toks) > 1:
#            to = self._expand_number(toks[1])
#            if to < fr:  # Wrap around max_ if necessary
#                return (list(range(fr, self.min_ + self.max_)) +
#                        list(range(self.min_, to + 1)))
#            return list(range(fr, to + 1))
#        return [fr]

#    def _range_steps(self, toks):
#        if len(toks) != 3 or not toks[2]:
#            raise self.ParseException('empty filter')
#        return self._expand_range(toks[:2])[::int(toks[2])]

#    def _star_steps(self, toks):
#        if not toks or not toks[0]:
#            raise self.ParseException('empty filter')
#        return self._expand_star()[::int(toks[0])]

#    def _expand_star(self, *args):
#        return list(range(self.min_, self.max_ + self.min_))

#    def _expand_number(self, s):
#        if isinstance(s, str) and s[0] == '-':
#            raise self.ParseException('negative numbers not supported')
#        try:
#            i = int(s)
#        except ValueError:
#            try:
#                i = weekday(s)
#            except KeyError:
#                raise ValueError('Invalid weekday literal {0!r}.'.format(s))

#        max_val = self.min_ + self.max_ - 1
#        if i > max_val:
#            raise ValueError(
#                'Invalid end range: {0} > {1}.'.format(i, max_val))
#        if i < self.min_:
#            raise ValueError(
#                'Invalid beginning range: {0} < {1}.'.format(i, self.min_))

#        return i
