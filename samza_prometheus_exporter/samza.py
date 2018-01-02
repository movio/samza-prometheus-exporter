# -*- coding: utf-8 -*-

from re import compile as re

def topic_partition_metric(match):
    return {
        'name': match.group(3),
        'labels': {
            'topic': match.group(1),
            'partition': match.group(2)
        }
    }

def store_metric(match):
    return {
        'name': match.group(2),
        'labels': {
            'store': match.group(1)
        }
    }

def system_metric(match):
    return {
        'name': match.group(2),
        'labels': {
            'system': match.group(1)
        }
    }

def system_topic_metric(match):
    return {
        'name': match.group(3),
        'labels': {
            'system': match.group(1),
            'topic': match.group(2)
        }
    }

def source_metric(match):
    return {
        'name': 'source-' + match.group(2),
        'labels': {
            'source': match.group(1)
        }
    }

def kafka_system_stream_partition_metric(match):
    return {
        'name': match.group(1),
        'labels': {
            'system': match.group(2),
            'stream': match.group(3),
            'partition': match.group(4)
        }
    }

def system_stream_partition_metric(match):
    return {
        'name': match.group(4),
        'labels': {
            'system': match.group(1),
            'stream': match.group(2),
            'partition': match.group(3)
        }
    }

def partition_metric(match):
    return {
        'name': match.group(2),
        'labels': {
            'partition': match.group(1)
        }
    }

def partition_store_metric(match):
    return {
        'name': 'store-' + match.group(3),
        'labels': {
            'partition': match.group(1),
            'store': match.group(2)
        }
    }

def kafka_system_metric(match):
    return {
        'name': 'kafka-' + match.group(2),
        'labels': {
            'system': match.group(1)
        }
    }

"""
Simple metrics are encoded as strings.
Metrics that need a regex to extract labels are encoded as a tuple (regex, parser).
"""
metrics = {
    'org.apache.samza.system.kafka.KafkaSystemProducerMetrics': [
        (re('(.*)-(producer-send-failed)'), kafka_system_metric),
        (re('(.*)-(producer-send-success)'), kafka_system_metric),
        (re('(.*)-(producer-sends)'), kafka_system_metric),
        (re('(.*)-(producer-retries)'), kafka_system_metric),
        (re('(.*)-(flush-ms)'), kafka_system_metric),
        (re('(.*)-(flush-failed)'), kafka_system_metric),
        (re('(.*)-(flushes)'), kafka_system_metric),
        (re('(.*)-(flush-ns)'), kafka_system_metric),
        'serialization error',
    ],
    'org.apache.samza.system.kafka.KafkaSystemConsumerMetrics': {
        (re('(.*)-(\d+)-(bytes-read)'), topic_partition_metric),
        (re('(.*)-(\d+)-(high-watermark)'), topic_partition_metric),
        (re('(.*)-(\d+)-(messages-read)'), topic_partition_metric),
        (re('(.*)-(\d+)-(offset-change)'), topic_partition_metric),
        (re('(.*)-(\d+)-(messages-behind-high-watermark)'), topic_partition_metric),
        (re('(.*)-(reconnects)'), system_metric),
        (re('(.*)-(skipped-fetch-requests)'), system_metric),
        (re('(.*)-(topic-partitions)'), system_metric),
        (re('(.*)-SystemStreamPartition \[(.*), (.*), (.*)\]'), kafka_system_stream_partition_metric),
        'poll-count',
    },
    'org.apache.samza.system.SystemProducersMetrics': {
        'flushes',
        'sends',
        'serialization error',
        (re('(.*)-(flushes)'), source_metric),
        (re('(.*)-(sends)'), source_metric),
    },
    'org.apache.samza.system.SystemConsumersMetrics': {
        'chose-null',
        'chose-object',
        'unprocessed-messages',
        'poll-timeout',
        'ssps-needed-by-chooser',
        'deserialization error',
		'poll-ns',
		'deserialization-ns',
        (re('(.*)-(messages-per-poll)'), kafka_system_metric),
        (re('(.*)-(polls)'), kafka_system_metric),
        (re('(.*)-(ssp-fetches-per-poll)'), kafka_system_metric),
        (re('([^-]*)-(.*)-(messages-chosen)'), system_topic_metric),
    },
    'org.apache.samza.metrics.JvmMetrics': {
        'mem-heap-committed-mb',
        'mem-heap-used-mb',
        'mem-heap-max-mb',
        'mem-non-heap-committed-mb',
        'mem-non-heap-used-mb',
        'mem-non-heap-max-mb',
        'threads-blocked',
        'threads-terminated',
        'threads-timed-waiting',
        'threads-runnable',
        'threads-waiting',
        'threads-new',
        'thread new',
        'ps marksweep-gc-count',
        'ps marksweep-gc-time-millis',
        'ps scavenge-gc-count',
        'ps scavenge-gc-time-millis',
        'gc-count',
        'gc-time-millis',
        'copy-gc-count',
        'copy-gc-time-millis',
        'marksweepcompact-gc-count',
        'marksweepcompact-gc-time-millis',

    },
    'org.apache.samza.job.yarn.SamzaAppMasterMetrics': {
        'released-containers',
        'completed-containers',
        'needed-containers',
        'running-containers',
        'failed-containers',
        'released-containers',
        'job-healthy',
        'http-port',
        'rpc-port',
        'task-count',
        'locality-matched',
        'container-count',
		'heartbeats-expired',
    },
    'org.apache.samza.container.SamzaContainerMetrics': {
        'process-calls',
        'window-calls',
        'send-calls',
        'commit-calls',
        'process-null-envelopes',
        'process-envelopes',
        'process-ms',
        'process-ns',
        'window-ms',
        'window-ns',
        'choose-ms',
        'choose-ns',
        'commit-ms',
        'commit-ns',
        'event-loop-utilization',
        'messages-actually-processed',
		'physical-memory-mb',
		'block-ns',
		'container-startup-time',
		'disk-usage-bytes',
		'executor-work-factor',
		'disk-quota-bytes',
        (re('partition (\d+)-(object-restore-time)'), partition_metric),
        (re('partition (\d+)-(lookup-restore-time)'), partition_metric),
        (re('partition (\d+)-(.*)-(restore-time)'), partition_store_metric),
    },
    'org.apache.samza.storage.kv.KeyValueStoreMetrics': {
        (re('(.*)-(bytes-read)'), store_metric),
        (re('(.*)-(bytes-written)'), store_metric),
        (re('(.*)-(flushes)'), store_metric),
        (re('(.*)-(deletes)'), store_metric),
        (re('(.*)-(deletealls)'), store_metric),
        (re('(.*)-(puts)'), store_metric),
        (re('(.*)-(alls)'), store_metric),
        (re('(.*)-(ranges)'), store_metric),
        (re('(.*)-(gets)'), store_metric),
        (re('(.*)-(getalls)'), store_metric),
    },
    'org.apache.samza.storage.kv.LoggedStoreMetrics': {
        (re('(.*)-(gets)'), store_metric),
        (re('(.*)-(puts)'), store_metric),
        (re('(.*)-(alls)'), store_metric),
        (re('(.*)-(deletes)'), store_metric),
        (re('(.*)-(ranges)'), store_metric),
        (re('(.*)-(flushes)'), store_metric),
    },
    'org.apache.samza.storage.kv.SerializedKeyValueStoreMetrics': {
        (re('(.*)-(flushes)'), store_metric),
        (re('(.*)-(ranges)'), store_metric),
        (re('(.*)-(deletes)'), store_metric),
        (re('(.*)-(deletealls)'), store_metric),
        (re('(.*)-(puts)'), store_metric),
        (re('(.*)-(gets)'), store_metric),
        (re('(.*)-(bytes-deserialized)'), store_metric),
        (re('(.*)-(bytes-serialized)'), store_metric),
        (re('(.*)-(alls)'), store_metric),
    },
    'org.apache.samza.storage.kv.KeyValueStorageEngineMetrics': {
        (re('(.*)-(ranges)'), store_metric),
        (re('(.*)-(flushes)'), store_metric),
        (re('(.*)-(puts)'), store_metric),
        (re('(.*)-(bytes-written)'), store_metric),
        (re('(.*)-(gets)'), store_metric),
        (re('(.*)-(messages-bytes)'), store_metric),
        (re('(.*)-(alls)'), store_metric),
        (re('(.*)-(messages-restored)'), store_metric),
        (re('(.*)-(deletes)'), store_metric),
        (re('(.*)-(bytes-deserialized)'), store_metric),
		(re('(.*)-(flush-ns)'), store_metric),
		(re('(.*)-(all-ns)'), store_metric),
		(re('(.*)-(get-ns)'), store_metric),
		(re('(.*)-(put-ns)'), store_metric),
		(re('(.*)-(release-ns)'), store_metric),
		(re('(.*)-(range-ns)'), store_metric),
		(re('(.*)-(delete-ns)'), store_metric),
    },
    'org.apache.samza.container.TaskInstanceMetrics': {
        'commit-calls',
        'window-calls',
        'process-calls',
        'flush-calls',
        'send-calls',
        'messages-sent',
        'messages-actually-processed',
		'pending-messages',
		'messages-in-flight',
        (re('([^-]*)-(.*)-(\d+)-(offset)'), system_stream_partition_metric),
    },
    'org.apache.samza.storage.kv.CachedStoreMetrics': {
        (re('(.*)-(cache-hits)'), store_metric),
        (re('(.*)-(flushes)'), store_metric),
        (re('(.*)-(flushes-avoided)'), store_metric),
        (re('(.*)-(store-calls)'), store_metric),
        (re('(.*)-(messages-restored)'), store_metric),
        (re('(.*)-(flush-batch-size)'), store_metric),
        (re('(.*)-(put-all-dirty-entries-batch-size)'), store_metric),
        (re('(.*)-(alls)'), store_metric),
        (re('(.*)-(dirty-count)'), store_metric),
        (re('(.*)-(puts)'), store_metric),
        (re('(.*)-(gets)'), store_metric),
        (re('(.*)-(deletes)'), store_metric),
        (re('(.*)-(ranges)'), store_metric),
        (re('(.*)-(cache-size)'), store_metric),
    },
    'org.apache.samza.system.chooser.RoundRobinChooserMetrics': {
        'buffered-messages',
    },
    'org.apache.samza.checkpoint.OffsetManagerMetrics': {
        (re('([^-]*)-(.*)-(\d+)-(checkpointed-offset)'), system_stream_partition_metric),
    },
    'org.apache.samza.system.chooser.BatchingChooserMetrics': {
        'batch-resets',
        'batched-envelopes'
    },
    'org.apache.samza.system.chooser.BootstrappingChooserMetrics': {
        'batch-resets',
	'lagging-batch-streams',
        (re('(.*)-(lagging-partitions)'), store_metric)
    },
	'org.apache.samza.metrics.ContainerProcessManagerMetrics': {
		'running-containers',
		'needed-containers',
		'completed-containers',
		'failed-containers',
		'released-containers',
		'container-count',
		'job-healthy',
		'locality-matched',
		'redundant-notifications',
	},
}
