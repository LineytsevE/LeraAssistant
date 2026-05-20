import tinytuya
import sys

# Настройки
DEVICE_ID = 'bf70a38629ee62797fw0gl'
IP = '192.168.0.12'
KEY = r"N3E]/2/xet>l`wSt"  # Сырая строка

print("Инициализация универсального класса Device...")
d = tinytuya.Device(DEVICE_ID, IP, KEY)
d.set_version(3.4)
d.set_socketTimeout(3)

# ТЕСТ 1: Просто чтение статуса
print("\n--- ТЕСТ 1: Чтение статуса ---")
try:
    status = d.status()
    print("Ответ розетки (Статус):", status)
except Exception as e:
    print("Ошибка при запросе статуса:", e)

# ТЕСТ 2: Отправка сырой команды на включение через DP 1
print("\n--- ТЕСТ 2: Отправка сырой команды (Включение) ---")
try:
    # Создаем сырой payload: '1' - это ID переключателя (switch_1), True - включить
    payload = d.generate_payload(tinytuya.CONTROL, {'1': True})
    res = d.send(payload)
    print("Ответ розетки (Команда):", res)
except Exception as e:
    print("Ошибка при отправке команды:", e)