# Task 3. Docker

Dockerfile и docker-compose для бота «Копилка».

## Сборка и запуск
`ash
docker compose -f Task_3_Docker/docker-compose.yml build
docker compose -f Task_3_Docker/docker-compose.yml up -d
`

## Остановка
`ash
docker compose -f Task_3_Docker/docker-compose.yml down
`

Переменные берутся из Task_2_Bot/.env. Данные хранятся в volume kopilka_data (bind к /app/data).
