"""Geospatial helpers — nearby-driver search using PostGIS ST_DWithin."""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def nearby_drivers(db: AsyncSession, lat: float, lng: float,
                         radius_m: int = 3000, vehicle_type: str | None = None):
    sql = text(
        """
        SELECT
            id AS driver_id,
            vehicle_type,
            rating,
            ST_Y(location::geometry) AS latitude,
            ST_X(location::geometry) AS longitude,
            ST_Distance(location, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) AS distance_m
        FROM drivers
        WHERE is_online = TRUE
          AND location IS NOT NULL
          AND (:vtype IS NULL OR vehicle_type = :vtype)
          AND ST_DWithin(location, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius)
        ORDER BY distance_m ASC
        LIMIT 20
        """
    )
    rows = await db.execute(sql, {"lat": lat, "lng": lng, "radius": radius_m, "vtype": vehicle_type})
    return [dict(r._mapping) for r in rows]


def make_point_sql(lng: float, lat: float) -> str:
    """SQL literal for a PostGIS geography point."""
    return f"ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326)::geography"
