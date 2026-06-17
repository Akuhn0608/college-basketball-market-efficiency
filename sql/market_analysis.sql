-- 1. Overall market overview using a JOIN
SELECT
    COUNT(*) AS games_analyzed,
    ROUND(AVG(mp.market_vig) * 100, 2) AS average_vig_pct,
    ROUND(AVG(g.visitor_win) * 100, 2) AS visitor_win_rate_pct,
    ROUND(AVG(g.home_win) * 100, 2) AS home_win_rate_pct
FROM games AS g
JOIN market_prices AS mp
    ON g.game_id = mp.game_id;


-- 2. Favorite and underdog performance using CASE WHEN
WITH team_market_observations AS (
    SELECT
        g.game_id,
        'visitor' AS team_location,
        mp.visitor_market_role AS market_role,
        mp.visitor_no_vig_prob AS market_probability,
        g.visitor_win AS actual_win
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id

    UNION ALL

    SELECT
        g.game_id,
        'home' AS team_location,
        mp.home_market_role AS market_role,
        mp.home_no_vig_prob AS market_probability,
        g.home_win AS actual_win
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id
)

SELECT
    team_location,
    market_role,
    COUNT(*) AS team_games,
    ROUND(AVG(market_probability) * 100, 2) AS avg_market_probability_pct,
    ROUND(AVG(actual_win) * 100, 2) AS actual_win_rate_pct,
    ROUND(
        (AVG(actual_win) - AVG(market_probability)) * 100,
        2
    ) AS pricing_error_pp,
    CASE
        WHEN AVG(actual_win) > AVG(market_probability)
            THEN 'outperformed market expectation'
        WHEN AVG(actual_win) < AVG(market_probability)
            THEN 'underperformed market expectation'
        ELSE 'matched market expectation'
    END AS performance_summary
FROM team_market_observations
GROUP BY
    team_location,
    market_role
ORDER BY
    team_location,
    market_role;


-- 3. Team-level market performance using multiple JOINs
WITH team_observations AS (
    SELECT
        g.game_id,
        g.game_date,
        g.visitor_team_id AS team_id,
        g.visitor_win AS win,
        mp.visitor_no_vig_prob AS market_probability
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id

    UNION ALL

    SELECT
        g.game_id,
        g.game_date,
        g.home_team_id AS team_id,
        g.home_win AS win,
        mp.home_no_vig_prob AS market_probability
    FROM games AS g
    JOIN market_prices AS mp
        ON g.game_id = mp.game_id
)

SELECT
    t.team_name,
    COUNT(*) AS games,
    SUM(o.win) AS actual_wins,
    ROUND(SUM(o.market_probability), 2) AS expected_wins,
    ROUND(
        SUM(o.win) - SUM(o.market_probability),
        2
    ) AS wins_above_expectation
FROM team_observations AS o
JOIN teams AS t
    ON o.team_id = t.team_id
GROUP BY
    t.team_id,
    t.team_name
HAVING COUNT(*) >= 20
ORDER BY
    wins_above_expectation DESC
LIMIT 15;


-- 4. Louisville rolling market adjustment using window functions
SELECT
    game_date,
    opponent,
    louisville_win,
    ROUND(louisville_no_vig_prob * 100, 2) AS market_probability_pct,

    SUM(louisville_win) OVER (
        ORDER BY game_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_actual_wins,

    ROUND(
        SUM(louisville_no_vig_prob) OVER (
            ORDER BY game_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS cumulative_expected_wins,

    ROUND(
        AVG(louisville_pricing_error) OVER (
            ORDER BY game_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) * 100,
        2
    ) AS rolling_5_game_pricing_error_pp

FROM louisville_case_study
ORDER BY game_date;