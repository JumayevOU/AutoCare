from . import users
from . import groups
from . import channels
from . import errors


def setup_routers(dp):
    users.setup(dp)


from .users.menuHendlers import router as menu_router
from .users.locations_hendler import router as locations_router
from .users.start import router as start_router
from .users.hamkorlik import router as hamkorlik_router
from .users.echo import router as echo_router
from .admin_panel import router as admin_router

def setup_routers():
    routers = [
        start_router,
        menu_router,
        locations_router,
        hamkorlik_router,
        echo_router,
        admin_router  
    ]
    return routers
