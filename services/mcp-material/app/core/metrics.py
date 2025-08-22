from prometheus_client import Counter, Histogram


REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path", "status"],
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10),
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "HTTP requests count",
    ["method", "path", "status"],
)

PARSE_ROWS = Counter(
    "parse_rows_total",
    "Rows extracted by parse_drawing",
    ["engine"],  # pdfplumber/camelot/ifc
)

PRICE_ITEMS = Counter(
    "price_items_total",
    "Items processed by price_bom",
    ["result"],  # priced|gap_unit|gap_price|gap_other
)

QUALITY_COVERAGE = Histogram(
    "pricing_coverage_ratio",
    "Coverage ratio: priced_items / total_items",
    buckets=(0.0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0),
)

