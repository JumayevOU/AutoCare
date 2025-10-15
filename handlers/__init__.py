from . import users
from . import groups
from . import channels
from . import errors


def setup_routers(dp):
    users.setup(dp)
