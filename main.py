import asyncio
import datetime

import telegram
from jira import JIRA

# Токен вашего телеграм-бота
TOKEN = '6175353928:AAHplr0s6alYjGowN_5gmNq-uVk7Kdcz_Fg'
# ID чата, в который будут отправляться сообщения
CHAT_ID = '343254672'
# URL JIRA-сервера
JIRA_SERVER = 'https://fk.jira.lanit.ru/'
# Логин и пароль для JIRA
JIRA_LOGIN = 'VOBykov'
JIRA_PASSWORD = '14031999KIRvolodya2023'

# Создаем объект телеграм-бота
bot = telegram.Bot(token=TOKEN)

# Создаем объект JIRA-клиента
jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_LOGIN, JIRA_PASSWORD))


# Функция для отправки сообщения в телеграм
async def send_message(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='HTML')
    except Exception as e:
        print(f'Error sending message: {e}')


# Функция для получения задач в статусе "Блокировано"
def get_blocked_issues():
    query = 'project in (LKP, FCS) AND issuetype in (Проблема) AND status in ("В ожидании воспроизведения", "На воспроизведении", "В ожидании разработчика", ' \
            '"На исправлении", "На уточнении", "В ожидании уточнения", Блокировано) AND ("Ответственный инженер по сопровождению" in (VOBykov, v.berezin, ' \
            'VEremin, BulatovE, yupopova, AMishina, a.karkavin, bondarev) OR assignee in (VOBykov, v.berezin, VEremin, BulatovE, yupopova, ' \
            'AMishina, a.karkavin, bondarev)) and priority = Blocker'
    issues = jira.search_issues(query)
    return issues


# Функция для отправки уведомления о задачах в статусе "Блокировано"
async def send_blocked_issues_notification():
    issues = get_blocked_issues()
    if len(issues) > 0:
        text = 'Внимание! Есть задачи в статусе "Блокировано":\n'
        for issue in issues:
            text += f'- <a href="https://fk.jira.lanit.ru/browse/{issue.key}">{issue.key}</a>: ' \
                    f'{issue.fields.summary} ({issue.fields.assignee})\n'
        await send_message(text)


async def main():
    offset = 0
    # Основной цикл программы
    while True:
        try:
            # Проверяем, что текущий день недели - понедельник-пятница и текущее время 10 утра и 14 часов дня
            current_time = datetime.datetime.now().time()
            current_day = datetime.datetime.now().weekday()
            if current_time >= datetime.time(10, 0) and current_time <= datetime.time(14, 0):
                await send_blocked_issues_notification()

            # Задержка на 30 минут перед следующей итерацией цикла
            await asyncio.sleep(1800)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Запускаем основную функцию
    asyncio.run(main())


if __name__ == "__main__":
    # Запускаем основную функцию
    asyncio.run(main())
