-- Keep aggregate and component sectors separate. Compare identical endpoints.
WITH endpoints AS (
 SELECT sector,
        MAX(CASE WHEN year = 1970 THEN consumption_ktoe END) AS first_ktoe,
        MAX(CASE WHEN year = 2024 THEN consumption_ktoe END) AS last_ktoe
 FROM energy
 WHERE fuel = 'Total'
 GROUP BY sector
)
SELECT sector, first_ktoe, last_ktoe,
       ROUND(100.0 * (last_ktoe - first_ktoe) / NULLIF(first_ktoe, 0), 2) AS change_pct
FROM endpoints
ORDER BY change_pct;
