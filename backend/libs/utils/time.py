import re
import time
from contextlib import suppress
from datetime import date, datetime, timedelta
from typing import Iterator, Optional, Union

import pytz
from dateutil.relativedelta import relativedelta

MSK = pytz.timezone('Europe/Moscow')
MSK_FORMAT = '{} МСК{}'
TIME_FORMAT = '%d.%m.%Y, %H:%M'


def time_counter() -> float:
    return time.perf_counter()


def elapsed_time() -> Iterator[float]:
    start_time = time_counter()
    yield 0.0
    yield time_counter() - start_time


def format_relative_to_msk(dt: datetime, tz: Optional[pytz.timezone] = None, fmt: Optional[str] = TIME_FORMAT) -> str:
    """
    Format given datetime relative to MSK locale (Russian time).

    If target timezone is set, output time in this timezone.
    If target timezone (tz) is not set, output time in initial timezone (suppose dt is not naive).
    """
    if tz:
        dt = dt.astimezone(tz)

    dt_str = dt.strftime(fmt)

    # calculate difference at that particular time, not now
    tz_diff = (MSK.localize(dt.replace(tzinfo=None)) - dt).total_seconds() / 3600

    if tz_diff == 0:
        tz_diff_str = ''
    elif tz_diff.is_integer():
        tz_diff_str = f'{tz_diff:+.0f}'
    else:
        tz_diff_str = f'{tz_diff:+.1f}'.replace('.', ',')  # ru_RU locale-specific separator

    return MSK_FORMAT.format(dt_str, tz_diff_str)


def now() -> datetime:
    return datetime.now(pytz.utc)


def parse_date(value: Optional[Union[str, datetime, date]], optional: bool = True) -> Optional[date]:
    if optional and value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()

    with suppress(ValueError):
        return datetime.fromisoformat(value).date()

    _formats = ('%d-%m-%Y %H:%M:%S',
                '%d.%m.%Y',
                '%Y-%m-%d')
    for fmt in _formats:
        with suppress(ValueError):
            return datetime.strptime(value, fmt).date()
    raise ValueError(f'unsupported date format: "{value}"')


def now_msk() -> datetime:
    return datetime.now(tz=MSK)


class RelativeDatetime:
    def __init__(self, years=0, months=0, days=0, leapdays=0, weeks=0,
                 hours=0, minutes=0, seconds=0, microseconds=0):
        self._delta = relativedelta(years=years, months=months, days=days,
                                    leapdays=leapdays, weeks=weeks, hours=hours,
                                    minutes=minutes, seconds=seconds,
                                    microseconds=microseconds)

    @classmethod
    def from_duration(cls, duration: str) -> "RelativeDatetime":
        return cls(**_parse_duration(duration))

    def __eq__(self, other) -> bool:
        if isinstance(other, relativedelta):
            return self._delta == other
        if isinstance(other, datetime):
            return self.in_past == other
        raise NotImplementedError()

    @property
    def in_past(self) -> datetime:
        return now() - self._delta

    @property
    def in_future(self) -> datetime:
        return now() + self._delta

    @property
    def value(self) -> relativedelta:
        return self._delta

    def to_postgres(self) -> str:
        result = []
        for attr in ("years", "months", "days", "hours",
                     "minutes", "seconds", "microseconds"):
            value = getattr(self._delta, attr)
            if value:
                result.append(f"{value} {attr}")
        return ' '.join(result)


def timedelta_from_duration(duration: str) -> timedelta:
    return timedelta(**_parse_duration(duration))


_duration_units = {
    "us": "microseconds",
    "s": "seconds",
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks",
    "mm": "months",
    "y": "years",
}


def _parse_duration(duration: str) -> dict[str, int]:
    if duration in ("0", "+0", "-0"):
        return {}

    pattern = re.compile(r'(\d+)([dhmswuy]+)')
    matches = pattern.findall(duration)
    if not matches:
        raise ValueError(f"Invalid duration {duration}")
    kwargs = {}
    for (value, unit) in matches:
        if unit not in _duration_units:
            raise ValueError(f"Unknown unit {unit} in duration {duration}")
        try:
            kwargs[_duration_units[unit]] = int(value)
        except Exception:
            raise ValueError(f"Invalid value {value} in duration {duration}")
    return kwargs
