Создание кастомного коннектора Apache kafka to Prometheus
================================================================================================================
  Сервис настроен на чтение метрик в формате json из топика Kafka
  преобразует полученные метрики в формат  Prometheus и публикует на ручке /metrics

  подробнее:
    Сервис работает в асинхронных потоках 
     1) Чтение топика test-topic-app и при получении сообщения запись сообщения в базу
     2) публикация ручки /metrics  - чтение из базы актуальные метрики конвертация в формат  Prometheus

Техстек 
==================================================================================================================
     python 3.12
     aiokafka
     asyncpg
     fastapi
     Jinja2
     oc windows (не обязательно - на ней разрабатывалась и тестировалась)

Установка Python
==================================================================================================================
      python -m venv venv 
      python -m pip install --upgrade pip
Активания изолированого окружения и установка  библиотек
==================================================================================================================
     venv\scripts\activate.bat (windows)
     source venv/bin/activate
     pip install -r requirements.txt

Запуск 
=================================================================================================================
     python main.py

Настройка переменных окружения:
================================================================================================================
    файл .env
    - Брокеры   KAFKA_SERVERS='kafka-0:9092,kafka-1:9092,kafka-2:9092'
    - Коннект к Базе 
                DB_HOST=postgres
                DB_PORT=5432
                DB_NAME=customers
                DB_USER=postgres-user
                DB_PASSWORD=postgres-pw
   

Сотсав проекта 
=================================================================================================================
    adapters - адаптеры для работы с внешними ресурсами (база данных, kafka)
           kafka.py - job для чтения сообщений
           pg.py  - функционал для работы с базой данных
    utils 
          promrthius.py - конвертов из  json в   Prometheus
    settings
          config.py  - конфигурация логера ,настройки 
         
    main.py 
          - инициализация asgi  сервера uvicorn , запуск JOB и предоставление API для сборщика метрик
    .env         - переменные окружения проекта


Результат
=================================================================================================================
     doc\prometheus_targets.png     -- добавлен endpoint для сборки метрик сервиса app
     doc\dashboard.png              -- дашборд с метриками Alloc, FreeMemory, PollCount, TotalMemory
     grafana\dashboards\app-1741024561105.json -- дашборд с метриками Alloc, FreeMemory, PollCount, TotalMemory





Максимизируйте скорость записи данных в Kafka — Source Record Write rate. 
================================================================================================================
   Чтобы повысить пропускную способность, изменяйте параметры:
   batch.size, linger.ms, buffer.memory и compression.type. 
    
   Как считаем 
    Record Size Average   avg  528 bytes  -- размер сообщения 
    buffer.memory  32mb                   -- дефалтовое значение буфера 
    batch.size = batch.max.rows * record_size_average_in_bytes  -- формула расчета 
   
   Результат

    Эксперимент	batch.size	linger.ms	compression.type	buffer.memory	source-record-write-rate max (кops/sec)          source-record-write-rate avg (кops/sec)  
    1	        500	        1000	     none	            33554432	           4.69                                      2.38 
    2	        528*100    	1000         none	            100000000              124                                       4.95 
    3	        528*100     500	         none               100000000              136                                       28.3 
	4           528*100     500	         yes                100000000              97.5                                      9.57 

    -- компрессия явно ест ресурсы 
    -- 3 вариант настроек - лучший 


Настройка Debezium коннектора 
================================================================================================================

    Коннектор  
     {
      "name": "postgres-source",
      "config":    {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "postgres-user",
      "database.password": "postgres-pw",
      "database.dbname": "customers",
      "database.server.name": "customers",
      "table.whitelist": "public.customers",
      "transforms": "unwrap",
      "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
      "transforms.unwrap.drop.tombstones": "false",
      "transforms.unwrap.delete.handling.mode": "rewrite",
      "topic.prefix": "customers",
      "topic.creation.enable": "true",
      "topic.creation.default.replication.factor": "-1",
      "topic.creation.default.partitions": "-1",
      "skipped.operations": "none",
      "name": "postgres-source"
     },
     "tasks": [   {
        "connector": "postgres-source",
        "task": 0
     }],
     "type": "source"
     }   
  

    Лог Дебезиума

    #Первоначальная репликация 

    2025-02-19 21:09:06 2025-02-19 18:09:06.406 GMT [118] STATEMENT:  CREATE_REPLICATION_SLOT "debezium"  LOGICAL decoderbufs 
    2025-02-19 21:09:06 2025-02-19 18:09:06.406 GMT [118] LOG:  exported logical decoding snapshot: "00000006-00000009-1" with 0 transaction IDs
    2025-02-19 21:09:06 2025-02-19 18:09:06.406 GMT [118] STATEMENT:  CREATE_REPLICATION_SLOT "debezium"  LOGICAL decoderbufs 
    2025-02-19 21:09:06 2025-02-19 18:09:06.679 GMT [118] LOG:  starting logical decoding for slot "debezium"
    2025-02-19 21:09:06 2025-02-19 18:09:06.679 GMT [118] DETAIL:  Streaming transactions committing after 0/1A43618, reading WAL from 0/1A435E0.
    2025-02-19 21:09:06 2025-02-19 18:09:06.679 GMT [118] STATEMENT:  START_REPLICATION SLOT "debezium" LOGICAL 0/1A43618
    2025-02-19 21:09:06 2025-02-19 18:09:06.679 GMT [118] LOG:  logical decoding found consistent point at 0/1A435E0
    2025-02-19 21:09:06 2025-02-19 18:09:06.679 GMT [118] DETAIL:  There are no running transactions.
    2025-02-19 21:09:06 2025-02-19 18:09:06.679 GMT [118] STATEMENT:  START_REPLICATION SLOT "debezium" LOGICAL 0/1A43618
    2025-02-19 21:10:46 2025-02-19 18:10:46.965 GMT [28] LOG:  checkpoint starting: time
    2025-02-19 21:10:47 2025-02-19 18:10:47.287 GMT [28] LOG:  checkpoint complete: wrote 4 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.304 s, sync=0.005 s, total=0.323 s; sync files=3, longest=0.003 s, average=0.002 s; distance=0 kB, estimate=398 kB; lsn=0/1A436B0, redo lsn=0/1A43678
    2025-02-19 20:45:46 
    2025-02-19 20:45:46 PostgreSQL Database directory appears to contain a database; Skipping initialization
    2025-02-19 20:45:46 

    # update update users set name = upper(name)
    2025-02-19 21:55:46 2025-02-19 18:55:46.985 GMT [28] LOG:  checkpoint starting: time
    2025-02-19 21:55:47 2025-02-19 18:55:47.107 GMT [28] LOG:  checkpoint complete: wrote 2 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.104 s, sync=0.005 s, total=0.123 s; sync files=2, longest=0.004 s, average=0.003 s; distance=0 kB, estimate=358 kB; lsn=0/1A43A10, redo lsn=0/1A439D8



     {
	"schema": {
		"type": "struct",
		"fields": [
			{
				"type": "int32",
				"optional": false,
				"field": "id"
			},
			{
				"type": "string",
				"optional": true,
				"field": "name"
			},
			{
				"type": "string",
				"optional": true,
				"field": "private_info"
			},
			{
				"type": "string",
				"optional": true,
				"field": "__deleted"
			}
		],
		"optional": false,
		"name": "customers.public.users.Value"
	},
	"payload": {
		"id": 1,
		"name": "ALEX",
		"private_info": "Alex@email.com",
		"__deleted": "false"
	}
   }


     # insert   
     #INSERT INTO users (id, name, private_info) VALUES (5, 'Diana11', 'Diana@email.com');

    2025-02-19 20:44:48 2025-02-19 17:44:48.244 GMT [49] LOG:  checkpoint complete: wrote 922 buffers (5.6%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.015 s, sync=0.061 s, total=0.088 s; sync files=301, longest=0.009 s, average=0.001 s; distance=4249 kB, estimate=4249 kB; lsn=0/19D4AC0, redo lsn=0/19D4AC0

    {
	"schema": {
		"type": "struct",
		"fields": [
			{
				"type": "int32",
				"optional": false,
				"field": "id"
			},
			{
				"type": "string",
				"optional": true,
				"field": "name"
			},
			{
				"type": "string",
				"optional": true,
				"field": "private_info"
			},
			{
				"type": "string",
				"optional": true,
				"field": "__deleted"
			}
		],
		"optional": false,
		"name": "customers.public.users.Value"
	},
	"payload": {
		"id": 4,
		"name": "Diana1",
		"private_info": "Diana@email.com",
		"__deleted": "false"
	}
   }

    # delete 
    # DELETE from users WHERE name='Diana1';

     1)
    {
	"schema": {
		"type": "struct",
		"fields": [
			{
				"type": "int32",
				"optional": false,
				"field": "id"
			},
			{
				"type": "string",
				"optional": true,
				"field": "name"
			},
			{
				"type": "string",
				"optional": true,
				"field": "private_info"
			},
			{
				"type": "string",
				"optional": true,
				"field": "__deleted"
			}
		],
		"optional": false,
		"name": "customers.public.users.Value"
	},
	"payload": {
		"id": 4,
		"name": null,
		"private_info": null,
		"__deleted": "true"
	}
    }
    2) сообщение с пустым value 
  
       key = {"schema":{"type":"struct","fields":[{"type":"int32","optional":false,"field":"id"}],"optional":false,"name":"customers.public.users.Key"},"payload":{"id":4}
   
      customers=# select * from users;
       id |  name   |  private_info
      ----+---------+-----------------
        1 | ALEX    | Alex@email.com
        2 | DIAN    | Dian@email.com
        3 | XENIA   | Xenia@email.com
        5 | Diana11 | Diana@email.com
       (4 rows)
  
   
        

    



   
            
    
     