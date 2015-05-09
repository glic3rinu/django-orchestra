from orchestra.contrib.settings import Setting


PLANS_RATE_METHODS = Setting('PLANS_RATE_METHODS',
    (
        'orchestra.contrib.plans.rating.step_price',
        'orchestra.contrib.plans.rating.match_price',
        'orchestra.contrib.plans.rating.best_price',
    )
)


PLANS_DEFAULT_RATE_METHOD = Setting('PLANS_DEFAULT_RATE_METHOD',
    'orchestra.contrib.plans.rating.step_price',
)
