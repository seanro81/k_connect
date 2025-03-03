from jinja2 import Template
import sys
import json

from settings.config import logging


metrics_template = """
{% for metric in metrics %}
# HELP {{ metric.Name }} {{ metric.Description }}
# TYPE {{ metric.Name }} {{ metric.Type }}
{{ metric.Name }} {{ metric.Value }}{% endfor %}
"""


async def json_to_prometheus(json_str: str):
    metrics = []
    metrics_data = json.loads(json_str)
    for k, v in metrics_data.items():
        metrics.append(v)

    tmpl = Template(metrics_template)

    # Выполнение шаблона и вывод результата
    try:
        output = tmpl.render(metrics=metrics)
        logging.info(f"json_to_prometheus: Метрики обработанны {output}")
        return output
    except Exception as e:
        logging.error(f"json_to_prometheus: Ошибка выполнения шаблона : {str(e)}")
        raise



