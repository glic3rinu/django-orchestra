from orchestra.contrib.settings import Setting


PLANS_RATE_METHODS = Setting('PLANS_RATE_METHODS',
    (
        'orchestra.contrib.plans.ratings.step_price',
        'orchestra.contrib.plans.ratings.match_price',
        'orchestra.contrib.plans.ratings.best_price',
    )
)


PLANS_DEFAULT_RATE_METHOD = Setting('PLANS_DEFAULT_RATE_METHOD',
    'orchestra.contrib.plans.ratings.step_price',
)
