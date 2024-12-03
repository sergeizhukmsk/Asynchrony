import asyncio


async def start_strongman(name, power):
    print(f'Силач {name} начал соревнования.')

    for ball_number in range(1, 6):
        # Задержка обратно пропорциональна силе (чем больше сила, тем меньше задержка)
        await asyncio.sleep(1 / power)
        print(f'Силач {name} поднял {ball_number}')

    print(f'Силач {name} закончил соревнования.')


async def start_tournament():
    # Создаем 3 задачи для соревнований
    task1 = asyncio.create_task(start_strongman('Pasha', 3))
    task2 = asyncio.create_task(start_strongman('Denis', 4))
    task3 = asyncio.create_task(start_strongman('Apollon', 5))

    # Ожидаем завершения всех задач
    await task1
    await task2
    await task3


# Запуск асинхронной функции start_tournament
if __name__ == '__main__':
    asyncio.run(start_tournament())
