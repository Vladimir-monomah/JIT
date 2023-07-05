import os
import asyncio
import datetime
import logging

import telegram
from jira import JIRA

# Токен вашего телеграм-бота
TOKEN = '6175353928:AAHplr0s6alYjGowN_5gmNq-uVk7Kdcz_Fg'
# ID чата, в который будут отправляться сообщения
CHAT_ID = '-1001696187652'
# URL JIRA-сервера
JIRA_SERVER = 'https://fk.jira.lanit.ru/'
# Логин и пароль для JIRA
JIRA_LOGIN = 'VOBykov'
JIRA_PASSWORD = '14031999KIRvolodya2023'

# Получите абсолютный путь к папке, в которой находится main.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем папку для логов с текущим временем и датой
log_folder = os.path.join(current_dir, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
os.makedirs(log_folder, exist_ok=True)

# Настройки логирования
logging.basicConfig(filename=os.path.join(log_folder, 'program.log'), level=logging.INFO)

# Создаем объект телеграм-бота
bot = telegram.Bot(token=TOKEN)

# Создаем объект JIRA-клиента
jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_LOGIN, JIRA_PASSWORD))

# Создаем объект логгера
logger = logging.getLogger(__name__)


# Функция для отправки сообщения в телеграм
async def send_message(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='HTML')
    except Exception as e:
        logger.error(f'Error sending message: {e}')


# Функция для получения задач в статусе "В ожидании уточнения"
def get_blocked_issues():
    query = 'project in (LKP, FCS) AND status not in (Closed, Resolved, Закрыт, Закрыта, Закрыто, "Спецификация обновлена", "Ответ получен", "Ответ дан") ' \
            'AND (type = Проблема OR type = Уточнение AND "ZFK (код бюджета)" = ' \
            'ZFK-4603 AND issueFunction not in linkedIssuesOfAll("type=\'Головная задача тестирования\'") OR issueFunction in linkedIssuesOfAll("type=\'Проблема\'")) ' \
            'AND component in ("ЛКП ЭА", "РДИК", "Электронное актирование (ЛК 44ФЗ)", "Односторонний отказ", "Односторонний отказ ЛКЗ", "Односторонний отказ ЛКП", "РК") ' \
            'AND component not in ("Автоматизированное тестирование") ' \
            'AND assignee in (Belyh, taisheva, PDidenko, mkolpakov, sultasheva, ISobolev, ochernikova, avmishina, Rajabov) ORDER BY assignee ASC, type ASC, ' \
            '"Багрейтинг проблемы" DESC, priority DESC'
    issues = jira.search_issues(query)
    return issues


# Функция для отправки уведомления о задачах в статусе "В ожидании уточнения"
async def send_blocked_issues_notification():
    try:
        issues = get_blocked_issues()
        if len(issues) > 0:
            text = 'Внимание! Есть задачи в статусе "В ожидании уточнения":\n'
            for issue in issues:
                text += f'- <a href="https://fk.jira.lanit.ru/browse/{issue.key}">{issue.key}</a>: ' \
                        f'{issue.fields.summary} ({issue.fields.assignee})\n'
            await send_message(text)
    except Exception as e:
        logger.error(f'Error sending blocked issues notification: {e}')


async def main():
    offset = 0
    is_running = False  # Флаг для отслеживания состояния выполнения программы
    # Основной цикл программы
    while True:
        try:
            # Проверяем, что текущий день недели - понедельник-пятница и текущее время 10 утра и 14 часов дня
            current_time = datetime.datetime.now().time()
            current_day = datetime.datetime.now().weekday()
            # Проверяем, что текущее время находится в заданных временных интервалах
            if current_day >= 0 and current_day <= 4 and current_time >= datetime.time(10, 0) and current_time <= datetime.time(14, 0):
                if not is_running:
                    # Запускаем программу
                    is_running = True
                    logger.info("Program started")
                    await send_blocked_issues_notification()
                else:
                    # Проверяем, выполнилась ли уже задача отправки уведомления
                    if await is_blocked_issues_notification_sent():
                        # Задача выполнена, завершаем программу
                        logger.info("Program completed")
                        return
            else:
                if is_running:
                    # Останавливаем программу
                    is_running = False
                    logger.info("Program stopped")

            # Задержка перед следующей итерацией цикла
            await asyncio.sleep(1800)  # Можно увеличить или уменьшить интервал

        except Exception as e:
            logger.error(f'Error in main loop: {e}')

        # Функция для проверки выполнения задачи отправки уведомления
        async def is_blocked_issues_notification_sent():
            # Ваша логика проверки выполнения задачи
            # В этом примере мы просто возвращаем False
            return False


if __name__ == "__main__":
    # Запускаем основную функцию
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f'Error in main function: {e}')
