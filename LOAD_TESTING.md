# API Load Testing Guide

## Running Load Tests

### Start the Application
```bash
# Development server
python manage.py runserver

# Or Docker
docker-compose up -d
```

### Run Basic Load Test
```bash
# Start Locust (test 10 users, 2 new users per second)
locust -f locustfile.py --host=http://localhost:8000 -u 10 -r 2

# Open browser and navigate to: http://localhost:8089
```

### Test Scenarios

#### Scenario 1: Global Load Test
- Simulates both employees and managers
- Expected: 50-100 requests/sec at peak
- Target response time: <200ms for 95th percentile

```bash
locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 5
```

#### Scenario 2: Heavy Report Generation
- Focus on report endpoints with caching
- Validates cache effectiveness
- Expected: <100ms average response time

```bash
locust -f locustfile.py --host=http://localhost:8000 -u 20 -r 1 \
  --weight AttendanceUser:1 --weight ManagerUser:3
```

#### Scenario 3: Concurrent Attendance Marking
- Peak load during sign-in time
- Tests rate limiting
- Expected: 429 responses after limit reached

```bash
locust -f locustfile.py --host=http://localhost:8000 -u 50 -r 10
```

## Performance Metrics to Monitor

### Response Time
- Average: <150ms
- 95th percentile: <300ms
- 99th percentile: <500ms

### Throughput
- Minimum: 50 requests/sec
- Target: 100+ requests/sec
- Peak capacity: 200+ requests/sec

### Error Rate
- Target: <0.1%
- Rate limit errors (429): Expected under load
- 5xx errors: Should be 0

### Resource Usage
- CPU: <80% under normal load
- Memory: <70% of available
- Database connections: <80 of max pool

## Analyzing Results

### Using Dashboard
1. Access Locust web UI at `http://localhost:8089`
2. Monitor real-time metrics:
   - Requests/sec
   - Response times
   - Number of failures
   - User count

### CSV Export
```bash
# Run test and export results
locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 5 \
  --run-time 5m --csv=load_test_results
```

### Analyzing Prometheus Metrics
```bash
# Query API request latency
http_request_duration_seconds_bucket{job="django"}

# Query cache hit rate
django_cache_hits_total / (django_cache_hits_total + django_cache_misses_total)

# Query error rate
rate(http_requests_total{status=~"5.."}[1m])
```

## Bottleneck Identification

### Database Queries
- Use Django Debug Toolbar: `http://localhost:8000/__debug__/`
- Check query count and execution time
- Add `.select_related()` for FK lookups
- Add `.prefetch_related()` for reverse FK queries

### Cache Effectiveness
- Monitor cache hit/miss ratio
- Increase TTL for stable data
- Invalidate strategically on updates

### Network
- Check if response size is reasonable
- Compress with gzip (enabled in production)
- Optimize JSON responses

## Stress Testing

### Find Breaking Point
```bash
locust -f locustfile.py --host=http://localhost:8000 -u 1000 -r 100 --run-time 10m
```

### Expected Results
- System should handle 200-300 concurrent users
- Graceful degradation beyond capacity
- No unhandled exceptions

## Scaling Recommendations

### Vertical Scaling
- Increase server CPU and RAM
- Expected: 30-50% performance improvement

### Horizontal Scaling
- Add more application servers behind load balancer
- Expected: Linear scaling up to database limits

### Database Optimization
- Read replicas for reporting endpoints
- Connection pooling
- Regular index maintenance

## Continuous Performance Testing

### CI/CD Integration
```bash
# Add to GitHub Actions
- name: Run Load Tests
  run: |
    locust -f locustfile.py --host=${{ env.STAGING_URL }} \
      -u 50 -r 2 --run-time 5m --csv=results
    
    # Fail if average response time > 300ms
    python check_performance.py results_stats.csv
```

### Baseline Comparison
- Run tests regularly
- Track performance over time
- Alert on regressions

## Troubleshooting Common Issues

### High Response Times
1. Check database slow queries
2. Monitor cache hit ratio
3. Check server resource usage
4. Review Nginx configuration

### Rate Limiting Errors (429)
1. Expected under peak load
2. Adjust rate limit if too strict
3. Implement token bucket algorithm

### Connection Pooling Issues
1. Increase max connections
2. Reduce connection timeout
3. Implement proper connection reuse

### Memory Leaks
1. Monitor memory usage trend
2. Check for unclosed connections
3. Review cache size limits

## Tools & Commands

### Monitor Application
```bash
# Docker stats
docker stats django_app

# System monitoring
watch -n 1 'ps aux | grep python'

# Nginx access log analysis
tail -f /var/log/nginx/access.log | grep -E "POST|GET"
```

### Database Monitoring
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check slow queries
SELECT query, calls, mean_time FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Check cache hit ratio
SELECT 
  sum(heap_blks_read) as heap_read, 
  sum(heap_blks_hit)  as heap_hit, 
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio 
FROM pg_statio_user_tables;
```