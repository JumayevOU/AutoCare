from . import start
from . import menuHendlers
from . import locations_hendler
from . import hamkorlik
from . import echo

def setup(dp):
    dp.include_router(start.router)
    dp.include_router(menuHendlers.router)
    dp.include_router(locations_hendler.router)
    dp.include_router(hamkorlik.router)
    dp.include_router(echo.router)

from .users import menuHendlers, locations_hendler
from .admin_panel import router as admin_router

def setup_routers():
    routers = [
        menuHendlers.router,
        locations_hendler.router,
        admin_router  
    ]
    return routers
