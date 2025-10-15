from . import users
from . import groups
from . import channels
from . import errors


def setup_routers(dp):
    users.setup(dp)


# handlers/__init__.py
from .users.menuHendlers import router as menu_router
from .users.locations_hendler import router as locations_router
from .users.start import router as start_router
from .users.hamkorlik import router as hamkorlik_router
from .users.echo import router as echo_router
# from .users.admin_panel import router as admin_router  # Agar admin panel bo'lsa

def setup_routers(dp):
    """Routerlarni Dispatcher ga qo'shish"""
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(locations_router)
    dp.include_router(hamkorlik_router)
    dp.include_router(echo_router)
    # dp.include_router(admin_router)  # Agar admin panel bo'lsa
