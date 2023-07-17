## Spanner Slow query 
spanner 활용 시 slow query 찾기용 쿼리 

```
SELECT  
  execution_count,
  avg_latency_seconds,
  avg_cpu_seconds,
  execution_count * avg_cpu_seconds AS total_cpu,
  interval_end,
  request_tag,
  text
FROM
  spanner_sys.QUERY_STATS_TOP_HOUR
WHERE
  interval_end = (
  SELECT
    MAX(interval_end)
  FROM
    spanner_sys.QUERY_STATS_TOP_HOUR)
ORDER BY
  avg_cpu_seconds DESC
LIMIT
  100;
```
