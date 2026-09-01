-- Marketplace performance metrics
-- Example SQL that could be run against a warehouse table named marketplace_panel.

WITH property_week AS (
    SELECT
        property_id,
        week,
        treated,
        adoption_week,
        baseline_visibility,
        impressions,
        clicks,
        bookings,
        revenue,
        CASE WHEN impressions > 0 THEN 1.0 * clicks / impressions END AS ctr,
        CASE WHEN clicks > 0 THEN 1.0 * bookings / clicks END AS booking_conversion
    FROM marketplace_panel
),

property_level AS (
    SELECT
        property_id,
        MAX(treated) AS ever_treated,
        MIN(CASE WHEN treated = 1 THEN week END) AS first_treated_week,
        AVG(baseline_visibility) AS baseline_visibility,
        SUM(impressions) AS impressions,
        SUM(clicks) AS clicks,
        SUM(bookings) AS bookings,
        SUM(revenue) AS revenue
    FROM property_week
    GROUP BY property_id
)

SELECT
    ever_treated,
    COUNT(*) AS properties,
    AVG(baseline_visibility) AS avg_baseline_visibility,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(bookings) AS bookings,
    SUM(revenue) AS revenue,
    1.0 * SUM(clicks) / NULLIF(SUM(impressions), 0) AS ctr,
    1.0 * SUM(bookings) / NULLIF(SUM(clicks), 0) AS booking_conversion
FROM property_level
GROUP BY ever_treated
ORDER BY ever_treated;
