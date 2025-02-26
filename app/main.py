import uvicorn
from fastapi import FastAPI

from jinja2 import Template

import sys
import asyncio


# Структура для хранения информации о работнике
employees = [
    {
        "FullName": "Александр Смирнов",
        "Salaries": [50000, 52000, 54000, 55000],
    },
    {
        "FullName": "Екатерина Петрова",
        "Department": "Маркетинг",
        "Salaries": [60000, 62000, 64000, 65000],
    },
]

# Шаблон для отображения информации о работниках
employee_template = """
{% for employee in employees %}
Работник: {{ employee.FullName }}{% if employee.Department %} / Отдел: {{ employee.Department }}{% endif %}
Выплаченная зарплата: {% for salary in employee.Salaries %}{{ salary }} {% endfor %}
{% endfor %}
"""

app = FastAPI()


@app.get("/metrics")
def metrics():
    # Создание шаблона
    tmpl = Template(employee_template)

    # Выполнение шаблона и вывод результата
    try:
        output = tmpl.render(employees=employees)
        print(output)
    except Exception as e:
        print(f"Ошибка при выполнении шаблона: {e}", file=sys.stderr)
        sys.exit(1)
    return output

#https://www.geeksforgeeks.org/mediator-method-python-design-pattern/

@app.on_event("startup")
async def kafka_consume():
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(consumer_modify_(loop), loop)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
