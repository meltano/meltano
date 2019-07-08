import collections

from enum import Enum

FilterOption = collections.namedtuple('FilterOption', 'label description operation')


class FilterOptionType(str, Enum):
    LESS_THAN = "LESS_THAN"
    LESS_THAN_OR_EQUAL_TO = "LESS_THAN_OR_EQUAL_TO"
    EQUAL_TO = "EQUAL_TO"
    NOT_EQUAL_TO = "NOT_EQUAL_TO"
    GREATER_THAN_OR_EQUAL_TO = "GREATER_THAN_OR_EQUAL_TO"
    GREATER_THAN = "GREATER_THAN"
    LIKE = "LIKE"


FilterOptions = [
    FilterOption(
      label = "< Less than",
      description = "Less than",
      operation = FilterOptionType.LESS_THAN,
    ),
    FilterOption(
      label = "<= Less than or equal",
      description = "Less than or equal",
      operation = FilterOptionType.LESS_THAN_OR_EQUAL_TO,
    ),
    FilterOption(
      label = "= Equal to",
      description = "Equal to",
      operation = FilterOptionType.EQUAL_TO,
    ),
    FilterOption(
      label = "!= Not equal to",
      description = "Not equal to",
      operation = FilterOptionType.NOT_EQUAL_TO,
    ),
    FilterOption(
      label = ">= Greater than or equal",
      description = "Greater than or equal",
      operation = FilterOptionType.GREATER_THAN_OR_EQUAL_TO,
    ),
    FilterOption(
      label = "> Greater than",
      description = "Greater than",
      operation = FilterOptionType.GREATER_THAN,
    ),
    FilterOption(
      label = "Like",
      description = "Custom like expression",
      operation = FilterOptionType.LIKE,
    ),
]
