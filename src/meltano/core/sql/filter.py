import collections

from enum import Enum

from .base import MeltanoFilterExpressionType

FilterOption = collections.namedtuple("FilterOption", "label description expression")


FilterOptions = [
    FilterOption(
        label="Less than",
        description="Less than",
        expression=MeltanoFilterExpressionType.LessThan,
    ),
    FilterOption(
        label="Less than or equal",
        description="Less than or equal",
        expression=MeltanoFilterExpressionType.LessOrEqualThan,
    ),
    FilterOption(
        label="Equal to",
        description="Equal to",
        expression=MeltanoFilterExpressionType.EqualTo,
    ),
    FilterOption(
        label="Greater than or equal",
        description="Greater than or equal",
        expression=MeltanoFilterExpressionType.GreaterOrEqualThan,
    ),
    FilterOption(
        label="Greater than",
        description="Greater than",
        expression=MeltanoFilterExpressionType.GreaterThan,
    ),
    FilterOption(
        label="Like",
        description="Custom like expression",
        expression=MeltanoFilterExpressionType.Like,
    ),
    FilterOption(
        label="Is Null",
        description="Is null",
        expression=MeltanoFilterExpressionType.IsNull,
    ),
    FilterOption(
        label="Is Not Null",
        description="Is not null",
        expression=MeltanoFilterExpressionType.IsNotNull,
    ),
]
