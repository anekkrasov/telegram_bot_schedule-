import requests
import json
from datetime import datetime, timedelta


class NNTUSchedule:
    #описание куки браузера
    def __init__(self):
        self.base_url = "https://api.nntu.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/raspisanie'
        })

    def get_departments(self):
        """Получает список отделений"""
        try:
            response = self.session.get(f"{self.base_url}/getdepartments")
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def get_groups(self, department_id):
        """Получает список групп по отделению"""
        try:
            data = {'department_id': department_id}
            response = self.session.post(f"{self.base_url}/getgroups", data=data)
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def get_schedule(self, department_id, group_id, schedule_type=1, date_from=None, date_to=None):
        """Получает расписание"""
        try:
            if date_from is None:
                date_from = datetime.now().strftime('%Y-%m-%d')
            if date_to is None:
                date_to = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

            data = {
                'department_id': department_id,
                'group_id': group_id,
                'type': schedule_type,
                'date_from': date_from,
                'date_to': date_to
            }

            response = self.session.post(f"{self.base_url}/getschedule", data=data)
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def find_group(self, group_name):
        """Находит группу по названию"""
        departments = self.get_departments()
        if not departments:
            return None, None

        for dept in departments:
            groups = self.get_groups(dept['id'])
            if groups:
                for group in groups:
                    if group.get('name') and group_name.upper() in group['name'].upper():
                        return group, dept
        return None, None


def format_schedule(schedule_data, group_name, days_count=7):
    """Форматирует расписание в читаемый вид"""
    if not schedule_data:
        return "❌ Не удалось получить расписание"

    days_map = {
        "1": "Понедельник",
        "2": "Вторник",
        "3": "Среда",
        "4": "Четверг",
        "5": "Пятница",
        "6": "Суббота"
    }

    result = f"📚 Расписание для группы *{group_name}*:\n\n"

    days_added = 0
    for day_num, day_name in days_map.items():
        if day_num in schedule_data and days_added < days_count:
            lessons = schedule_data[day_num]
            result += f"📅 *{day_name}:*\n"

            has_lessons = False
            for slot in lessons:
                if slot:
                    has_lessons = True
                    for lesson in slot:
                        time = lesson.get('para_time', 'Время не указано')
                        subject = lesson.get('predmet_name', 'Предмет не указан')
                        teacher = f"{lesson.get('prepod_surname', '')} {lesson.get('prepod_name', '')}".strip()
                        classroom = lesson.get('aud', '')
                        lesson_type = lesson.get('para_type', '')

                        result += f"🕒 *{time}* ({lesson_type})\n"
                        result += f"📖 {subject}\n"
                        if teacher:
                            result += f"👨‍🏫 {teacher}\n"
                        if classroom:
                            result += f"🚪 Аудитория: {classroom}\n"
                        result += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"

            if not has_lessons:
                result += "🎉 *Пар нет!*\n"

            result += "\n"
            days_added += 1

    return result


def get_today_schedule(group_name):
    """Получает расписание на сегодня"""
    api = NNTUSchedule()

    group, dept = api.find_group(group_name)
    if not group:
        return f"❌ Группа '{group_name}' не найдена"

    # Получаем расписание только на сегодня
    today = datetime.now().strftime('%Y-%m-%d')
    schedule = api.get_schedule(dept['id'], group['id'], date_from=today, date_to=today)

    if not schedule:
        return f"📅 На сегодня у группы *{group['name']}* пар нет 🎉"

    return format_schedule(schedule, group['name'], days_count=1)


def get_week_schedule(group_name):
    """Получает расписание на неделю"""
    api = NNTUSchedule()

    group, dept = api.find_group(group_name)
    if not group:
        return f"❌ Группа '{group_name}' не найдена"

    schedule = api.get_schedule(dept['id'], group['id'])

    if not schedule:
        return f"❌ Не удалось получить расписание для группы *{group['name']}*"

    return format_schedule(schedule, group['name'])


def get_available_groups():
    """Получает список доступных групп"""
    api = NNTUSchedule()

    departments = api.get_departments()
    if not departments:
        return "❌ Не удалось получить список групп"

    result = "📋 *Доступные группы:*\n\n"

    for dept in departments[:3]:  # Берем первые 3 отделения чтобы не перегружать
        groups = api.get_groups(dept['id'])
        if groups:
            # Фильтруем нормальные группы
            valid_groups = [g for g in groups if
                            g.get('name') and g.get('kurs') and g['kurs'] in ['1', '2', '3', '4', '5']]

            if valid_groups:
                result += f"🎓 *{dept['name']}:*\n"
                # Группируем по курсам
                by_course = {}
                for group in valid_groups[:10]:  # Ограничиваем количество
                    course = group['kurs']
                    if course not in by_course:
                        by_course[course] = []
                    by_course[course].append(group['name'])

                for course in sorted(by_course.keys()):
                    result += f"  {course} курс: {', '.join(by_course[course][:3])}\n"
                result += "\n"

    result += "💡 *Использование:*\nНапишите название группы чтобы получить расписание"
    return result


# Примеры использования:
if __name__ == "__main__":
    print("=== ТЕСТ РАБОЧЕГО КОДА ===\n")

    # 1. Получаем список групп
#    print("1. Список групп:")
#    print(get_available_groups())

 #   print("\n" + "=" * 50 + "\n")

    # 2. Расписание на сегодня
#    print("2. Расписание на сегодня:")
#    today_schedule = get_today_schedule("АСИ 24-1")
#    print(today_schedule)

    print("\n" + "=" * 50 + "\n")

    # 3. Расписание на неделю
    print("3. Расписание на неделю:")
    week_schedule = get_week_schedule("АСИ 24-1")
    print(week_schedule)