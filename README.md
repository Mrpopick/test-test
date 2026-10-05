## Запуск

~~~powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d --wait
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
~~~

Docker Compose поднимает PostgreSQL на localhost:5433; приложение запускается локально на http://127.0.0.1:8000.
Таблицы и тарифы создаются при запуске приложения.
Проверка доступности: http://127.0.0.1:8000/health, документация API: http://127.0.0.1:8000/docs.

В другом окне PowerShell запустите тесты:

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q
~~~

Тесты используют временную реализацию хранилища и не требуют PostgreSQL. Для ручной проверки реальной базы запустите приложение по инструкции выше.

## Примеры запросов

Сначала получите ID тарифа:

~~~powershell
curl.exe http://127.0.0.1:8000/tariffs
~~~

Подставьте UUID тарифа из ответа и ID созданного платежа:

~~~powershell
curl.exe -i -X POST http://127.0.0.1:8000/payments -H "Content-Type: application/json" -H "Idempotency-Key: example-1" --data-raw '{\"tariff_id\":\"00000000-0000-0000-0000-000000000000\",\"email\":\"student@example.com\",\"method\":\"installment\",\"installment_months\":3,\"promo_code\":\"kvitto10\"}'
curl.exe http://127.0.0.1:8000/payments/ID
~~~

Повтор POST с тем же Idempotency-Key возвращает тот же платёж с кодом 200. Новый платёж имеет статус pending. Банк может перевести его в succeeded или failed, а succeeded — в refunded; запрещённый переход возвращает 409.

~~~powershell
curl.exe -i -X POST http://127.0.0.1:8000/webhooks/bank -H "Content-Type: application/json" --data-raw '{\"payment_id\":1,\"status\":\"succeeded\"}'
~~~
