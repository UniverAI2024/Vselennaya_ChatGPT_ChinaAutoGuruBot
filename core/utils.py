import pandas as pd
from openpyxl import Workbook
from dbase.dbworker import get_df_users, get_df_docs, get_df_history, get_all_users, add_history, update_dialog_state
from datetime import datetime, timezone, timedelta
import re


timezone_offset = 3.0  # Pacific Standard Time (UTC+03:00)
tzinfo = timezone(timedelta(hours=timezone_offset))


def close_run_dialog():
    users = get_all_users()
    for user in users:
        user_id = user[0]
        last_interaction_time = datetime.strptime(user[5], "%Y-%m-%d %H:%M:%S")
        last_interaction_time = last_interaction_time.replace(tzinfo=tzinfo)

        if (datetime.now(tzinfo) - last_interaction_time).total_seconds() / 3600 > 3 and user[15] == 0 and user[7] != 'start':
            # Запись истории
            history_data = (
                user_id,
                "Консультация сайт",
                user[10],
                0,
                user[11],
                datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S"),
                user[12],
                user[15]
            )
            add_history(history_data)
            update_dialog_state(user_id, 'start')

        if (datetime.now(tzinfo) - last_interaction_time).total_seconds() / 3600 > 12 and user[15] == 1 and user[7] != 'start':
            # Запись истории
            history_data = (
                user_id,
                "Консультация ТГ-бот",
                user[10],
                0,
                user[11],
                datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S"),
                user[12],
                user[15]
            )
            add_history(history_data)
            update_dialog_state(user_id, 'start')


def split_messages(text):
    splitters = ['Пользователь:', 'Ассистент:']

    split_regex = '|'.join('(?=' + re.escape(s) + ')' for s in splitters)
    parts = re.split(split_regex, text)

    # Удаляем пустые строки
    parts = [part for part in parts if part.strip()]
    return parts


def get_report():

    # Заголовки столбцов
    columns_users = [
        'user_id', 'phone_number', 'first_name', 'last_name', 'username', 'last_interaction', 'num_queries'
    ]

    columns_docs = [
        'doc_id', 'doc_name', 'last_update'
    ]

    columns_history = [
        'user_id', 'score_name', 'score_text', 'score', 'time_duration', 'date_estimate', 'num_token'
    ]

    sheet_name = ['Пользователи', 'Документы', 'Оценки']
    sheet_col_width = [
        {'A:A': 12, 'B:B': 20, 'C:C': 20, 'D:D': 20, 'E:E': 30, 'F:F': 20, 'G:G': 20},
        {'A:A': 14, 'B:B': 80, 'C:C': 20},
        {'A:A': 12, 'B:B': 14, 'C:C': 80, 'D:D': 12, 'E:E': 20, 'F:F': 20, 'G:G': 20}
        ]

    df_users = get_df_users()[columns_users]
    df_docs = get_df_docs()[columns_docs]
    df_score = get_df_history()[columns_history]
    name_report = f'report_ChinaAutoGuruBot_{datetime.now(tzinfo).strftime("%d.%m.%Y_%H.%M.%S")}.xlsx'
    with pd.ExcelWriter(name_report) as writer:
        workbook = writer.book
        df_users.to_excel(writer, sheet_name=sheet_name[0], index=False)
        df_docs.to_excel(writer, sheet_name=sheet_name[1], index=False)
        df_score.to_excel(writer, sheet_name=sheet_name[2], index=False)
        cell_format = workbook.add_format({'align': 'left', 'text_wrap': 'true'})
        for i, sh_status in enumerate(sheet_name):
            sheet = writer.sheets[sh_status]
            for key in sheet_col_width[i].keys():
                sheet.set_column(str(key), int(sheet_col_width[i][key]), cell_format)
    return name_report

if __name__ == '__main__':
    text = """
    Пользователь: Добрый вечер, знаю, у вас сегодня не хватит времени ответить, но прикрепляю сразу же колаб, проблема в сохранении модели. Я создал 
колбеки, сохранение после каждой эпохи. Они сохраняют модель, но после загрузки она не работает, выдаёт ошибку. Пробовал сохранять напрямую 
после обучения. Ошибка, та же самая не могу понять, в чем причина.
Ассистент: Добрый вечер! Спасибо за ваш вопрос. Я понимаю, что у вас возникла проблема с сохранением модели в колабе. Чтобы помочь вам разобраться, мне нужно больше информации о том, как вы сохраняете и загружаете модель. 

Ошибки могут возникать по разным причинам, но я могу предложить несколько возможных решений. 

1. Убедитесь, что вы правильно указываете путь для сохранения и загрузки модели. Убедитесь, что путь указан полностью и правильно.

2. Проверьте, что модель сохраняется и загружается в том же формате. Например, если вы сохраняете модель в формате .h5, убедитесь, что вы загружаете модель также в формате .h5.

3. Проверьте, что модель правильно компилируется после загрузки. Возможно, вам нужно повторно скомпилировать модель после загрузки.

4. Убедитесь, что все необходимые зависимости и библиотеки установлены и актуальны. Возможно, проблема связана с несовместимостью версий.

Если вы предоставите больше информации о коде, который вы используете для сохранения и загрузки модели, я смогу дать более точные рекомендации.
    

Пользователь: Добрый вечер, знаю, у вас сегодня не хватит"""

    for part in split_messages(text):
        print(part.strip())
    print(split_messages(text))