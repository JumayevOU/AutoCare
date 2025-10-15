# migrate.py
import asyncio
import sys
import os

# Root papkaga qo'shish
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, batch_insert_autoservices, batch_insert_carwashes
from data.locations import Autoservice, CarWash

async def migrate_data():
    """Ma'lumotlarni database ga ko'chiradi"""
    print("🚀 Database migratsiyasi boshlandi...")
    
    # Database ni ishga tushirish
    await init_db()
    print("✅ Database jadvallari yaratildi")
    
    # Avtoservislarni ko'chirish
    autoservice_data = []
    for service in Autoservice:
        autoservice_data.append({
            "id": service["id"],
            "name": service["name"],
            "lat": service["lat"],
            "lon": service["lon"],
            "address": service["address"],
            "phone": service["phone"],
            "services": service["services"],
            "working_days": service["working_days"],
            "working_hours": service["working_hours"],
            "is_24_7": service["is_24_7"]
        })
    
    success = await batch_insert_autoservices(autoservice_data)
    if success:
        print(f"✅ {len(autoservice_data)} ta avtoservis database ga qo'shildi")
    else:
        print("❌ Avtoservislarni qo'shishda xatolik")
    
    # Avtomoykalarni ko'chirish
    carwash_data = []
    for carwash in CarWash:
        carwash_data.append({
            "id": carwash["id"],
            "name": carwash["name"],
            "lat": carwash["lat"],
            "lon": carwash["lon"],
            "address": carwash["address"],
            "phone": carwash["phone"],
            "services": carwash["services"],
            "working_days": carwash["working_days"],
            "working_hours": carwash["working_hours"],
            "is_24_7": carwash["is_24_7"]
        })
    
    success = await batch_insert_carwashes(carwash_data)
    if success:
        print(f"✅ {len(carwash_data)} ta avtomoyka database ga qo'shildi")
    else:
        print("❌ Avtomoykalarni qo'shishda xatolik")
    
    print("🎉 Migratsiya muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    asyncio.run(migrate_data())
