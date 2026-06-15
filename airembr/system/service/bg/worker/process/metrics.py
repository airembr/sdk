from typing import Optional

from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, push_to_gateway

from airembr.core.singleton import Singleton
from airembr.system.decorator.throttler import throttle
from airembr.system.process.logging.log_handler import get_logger
from pararun.protocol.metrics_protocol import MetricsProtocol
from airembr.system.config.global_config import global_settings

logger = get_logger(__name__)

class PrometheusMeters:

    def __init__(self):
        self._repo = {}
        self._new_data = False
        super().__init__()

    def fetch(self, key: str, factory):
        if key not in self._repo:
            self._repo[key] = factory()
        self._new_data = True
        return self._repo[key]

    def clear(self):
        self._new_data = False

    @property
    def has_new(self) -> bool:
        return self._new_data


class PrometheusMetrics(metaclass=Singleton):

    def __init__(self, prefix):
        self.prefix = prefix
        self.gateway = global_settings.prometheus_gateway
        self.job_name = f'{prefix}_worker'
        self.registry = CollectorRegistry()
        self.metrics_repo = PrometheusMeters()

    @throttle(seconds=5)
    def throttled_push_metric(self):
        self.push_metric()

    def push_metric(self):
        if not self.metrics_repo.has_new:
            return

        try:
            push_to_gateway(
                self.gateway,
                job=self.job_name,
                registry=self.registry,
                timeout=1  # Collection timeout
            )

            self.metrics_repo.clear()
        except Exception as e:
            logger.warning(f"Prometheus push failed: {e}")

    def gauge(self, name: str, description: str):
        name = f"{self.prefix}_{name}"
        meter_factory = lambda: Gauge(name, description, registry=self.registry)
        return self.metrics_repo.fetch(name, meter_factory)

    def counter(self, name: str, description: str):
        name = f"{self.prefix}_{name}"
        meter_factory = lambda: Counter(name, description, registry=self.registry)
        return self.metrics_repo.fetch(name, meter_factory)

    def histogram(self, name: str, description: str, buckets=None):
        """
        Returns a Histogram metric with the given name and description.
        Optional `buckets` list can define latency ranges (in seconds).
        """
        if buckets is None:
            buckets = Histogram.DEFAULT_BUCKETS

        name = f"{self.prefix}_{name}"
        meter_factory = lambda:  Histogram(name, description, registry=self.registry, buckets=buckets)
        return self.metrics_repo.fetch(name, meter_factory)


class MetricsAdapter(MetricsProtocol):
    def __init__(self, prefix):
        if global_settings.enable_prometheus:
            if global_settings.prometheus_gateway is None:
                raise ValueError(
                    "Prometheus is enabled but prometheus gateway is not set. Worker requires prometheus gateway to be set.")
            self._adapter = PrometheusMetrics(prefix)
        else:
            self._adapter = None

    @property
    def enabled(self) -> bool:
        return self._adapter is not None

    @property
    def adapter(self) -> Optional[PrometheusMetrics]:
        return self._adapter

    def push_metrics(self):
        if self._adapter:
            self._adapter.push_metric()

    def throttled_push_metrics(self):
        if self._adapter:
            self._adapter.throttled_push_metric()
