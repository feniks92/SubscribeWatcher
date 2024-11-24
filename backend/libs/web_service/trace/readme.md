## Утилита по проведения анализа потребления памяти и процессора

## Установка

### Добавляем зависимость в pyprogect.toml

```
[tool.poetry.dependencies]
service_trace = {path = "../../tools/service_trace", develop = true}
```

### Устанавливаем service_trace

```
poetry install
```

### в main.py

```
from tools.service_trace.uvicorn import run_uvicorn_with_trace

if __name__ == "__main__":
    from app.app import app
    run_uvicorn_with_trace(app)
```

### в settings.py

если требуется отчет по CPU (html\speedscope\flamegraph), по умолчанию включен

```
PROFILING_CPU_ENABLED = true
```

### Запускаем сервис

```
export ENV_FOR_DYNACONF=LOCAL
python3 main.py
```

приложение должно работать без изменений

## Трассировка

### По памяти

После запуска приложения в ROUTES сервиса

[/api/internal/docs](http://0.0.0.0/api/internal/docs) (по умолчанию, при наличии internal router)

[/docs](http://0.0.0.0/docs)

добавляются POST ручки трассировки:

    /take_snapshot - запускает трассировку и делает снимок объектов по памяти
    /stop_trace - останавливает трассировку

/take_snapshot body

```

    {
      "root": true,
      "limit": 5,
      "exclude_filters": [
        "*env*",
        "*frozen*",
        "*string*"
      ],
      "include_filters": []
    }
```

* "root": true - делает базовый снимок
* "root": false - делает оследующие снимоки и выводит изменения по отношению к базовому снику
* "limit": 5 - кол-во отображаемых объектов памяти
* "exclude_filters" - исключает объекты из наблюдения
* "include_filters" - включает объекты в наблюдение

### По процессору

должен быть включен

    PROFILING_CPU_ENABLED = true

в запрос добавляются query

    profile: true
    profile_format: html\speedscope

Пример:

http://127.0.0.1:8097/api/v1/start?profile=true&profile_format=html

В результате в корне приложения формируется отчет в виде html или json (для дальнейшего построения flamegraph)

### Python console

Так же к работающему приложению можно подключиться

`>>> telnet 127.0.0.1 20101`

`>>> console`

И далее можно анализировать код или потребление памяти использую различные инструменты,
например [objgraph](https://objgraph.readthedocs.io/en/stable/objgraph.html)
