from django import template
register = template.Library()


@register.filter
def leading_zeros(value, desired_digits):
  """
  Given an integer, returns a string representation, padded with [desired_digits] zeros.
  """
  num_zeros = int(desired_digits) - len(str(value))
  return ('0'*num_zeros) + str(value)


@register.filter
def tralling_zeros(value, desired_digits):
  """
  Given an integer, returns a string representation, padded with zeros [desired_digits].
  """
  num_zeros = int(desired_digits) - len(str(value))
  return str(value) + ('0'*num_zeros)
  

@register.filter  
def spaces(value):
    return ' '*value
    

@register.filter    
def fit_and_tralling_spaces(value, length):
    value = str(value)[:int(length)]
    num_spaces = int(length) - len(str(value))
    return str(value) + (' '*num_spaces)

    
@register.filter    
def rm_dot(value):
    return int(str(round(float(value),2)).replace('.',''))

