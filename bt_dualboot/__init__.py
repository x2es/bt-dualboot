# NOTE: re-exported for foreign packages only including tests
#       in order to clean modules dependencies without circular imports
#       submodules of `bt_dualboot.*` should import this from `bt_dualboot.__meta__`
from .__meta__ import APP_NAME, __version__
