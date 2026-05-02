def get_nearby(api, lat: float, lng: float, radius_km: int = 20):
 
    print(f"[get_nearby] lat={lat}, lng={lng}, radius={radius_km} km")

    data, code = api._get("/menu/nearby/", {
        "lat":    lat,
        "lng":    lng,
        "radius": radius_km,   
    })

    print(f"[get_nearby] status={code}")
    print(f"[get_nearby] response={data}")

    if code == 404 and "No home cooks with location" in str(data.get("error", "")):
        print("[get_nearby] ⚠️  HomeCook records exist but have NULL latitude/longitude in DB.")
        print("[get_nearby]    Run this in Django shell to check:")
        print("[get_nearby]    from homecook.models import HomeCook")
        print("[get_nearby]    print(HomeCook.objects.values('name','latitude','longitude'))")

    return data, code