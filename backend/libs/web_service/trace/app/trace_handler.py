import tracemalloc


class MemoryTrace:
    _last_snapshot = None

    def __init__(self, ):
        self.result = dict()
        self._tracemalloc = tracemalloc
        self.default_exclude_filters: list = [self._tracemalloc.__file__, ]
        self.default_include_filters: list = []

    def __call__(self,
                 root: bool,
                 limit: int,
                 exclude_filters: list,
                 include_filters: list,
                 ):
        self.root = root
        self.limit = limit
        if exclude_filters:
            self.default_exclude_filters.extend(exclude_filters)
        if include_filters:
            self.default_include_filters.extend(include_filters)
        return self

    def is_tracing(self):
        return self._tracemalloc.is_tracing()

    def start(self):
        self._tracemalloc.start()

    def stop(self):
        MemoryTrace._last_snapshot = None
        self._tracemalloc.stop()

    def take_snapshot(self):
        current_snapshot = self._take_snapshot()
        if self.root:
            MemoryTrace._last_snapshot = current_snapshot
        self.get_statistics(current_snapshot)

    def get_statistics(self, current_snapshot):
        self._get_total_memory_usage()
        self._get_leaks(current_snapshot)
        self._get_memory_usage(current_snapshot)

    def _take_snapshot(self):
        snapshot = self._tracemalloc.take_snapshot()
        exclude_filters = [self._tracemalloc.Filter(False, f) for f in self.default_exclude_filters]
        include_filters = [self._tracemalloc.Filter(True, f) for f in self.default_include_filters]
        snapshot = snapshot.filter_traces(filters=[*exclude_filters, *include_filters])
        return snapshot

    def _get_leaks(self, snapshot):
        st = snapshot.compare_to(MemoryTrace._last_snapshot, 'lineno')
        self.result['leaks'] = []
        for stat in st[:self.limit]:
            self.result['leaks'].append({
                'file_path': stat.traceback.__str__(),
                'count': f'{stat.count} (+{stat.count_diff})',
                'size': f'{self._format_size(stat.size, False)} ({self._format_size(stat.size_diff, True)})',

            })

    def _get_memory_usage(self, snapshot):
        top_stats = snapshot.statistics('traceback')
        self.result['memory'] = []
        count = min(self.limit, len(top_stats))
        for i in range(count):
            stat = top_stats[i]
            file = stat.traceback.format().__str__()
            self.result['memory'].append({'file': file,
                                          'blocks': stat.count,
                                          'size': self._format_size(stat.size, False)})

    def _get_total_memory_usage(self):
        traced_memory = self._tracemalloc.get_traced_memory()
        self.result['total_memory'] = {'current': self._format_size(traced_memory[0], False),
                                       'peak': self._format_size(traced_memory[1], False)}

    def _format_size(self, size, sign):
        return self._tracemalloc._format_size(size, sign)
