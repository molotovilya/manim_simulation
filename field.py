""" 
для запуска генерации проверьте

1. наличие библитеки Manim (Manim Community v0.18.1)
2. перейдите в место расположения файла 
3. из терминала запустите команду:

manim -pql field.py MultipleParticlesMotion

(в случае если файл называется у вас field.py) 

"""


from manim import *
import numpy as np

class MultipleParticlesMotion(Scene):
    def construct(self):

        # Параметры
        ani_time = 3 # Время анимации 
        N = 200  # Начальное количество точек
        M = 20  # Количество новых точек, добавляемых каждые SPAWN_INTERVAL секунд
        SPAWN_INTERVAL = 0.1  # Интервал появления новых точек в секундах
        PARTICLE_SIZE = 0.05  # Размер точек
        PARTICLE_COLOR = RED  # Цвет точек
        TRACE_COLOR = WHITE  # Цвет пути
        SCREEN_WIDTH = config.frame_width / 2 + 10  # Границы экрана по ширине
        SCREEN_HEIGHT = config.frame_height / 2 + 10  # Границы экрана по высоте
        time_scale = 1  # Фактор замедления времени
        MAX_TRACE_LENGTH = 15  # Максимальная длина пути (в количестве точек)

        # Определяем векторное поле
        def vector_field_func(point):
            x, y = point[:2]

            # движение по спирали из центра 
            # dx = -y + x  # Компонента x
            # dy = x + y   # Компонента y

            # движение по гиперболам 
            # dx = x  # Компонента x
            # dy = -y   # Компонента y

            # движение по окружности 
            dx = y  # Компонента x
            dy = -x   # Компонента y

            return np.array([dx, dy, 0])  # Возвращаем вектор


        # Создаём начальные точки с случайными позициями
        particles = []
        traces = []

        def create_particle():
            particle = Dot(
                point=np.append(np.random.uniform(-5, 5, size=2), 0),
                color=PARTICLE_COLOR,  # Цвет частиц
                radius=PARTICLE_SIZE
            )
            trace = TracedPath(particle.get_center, stroke_color=TRACE_COLOR, stroke_width=1)  # Цвет следа
            self.add(particle, trace)
            # Сохраняем связь между частицей и её трассой
            particle.trace = trace
            # Добавляем updater для движения каждой новой частицы
            particle.add_updater(update_particle)
            return particle, trace

        # Функция для добавления новых частиц
        def spawn_particles():
            new_particles = []
            new_traces = []
            for _ in range(M):
                particle, trace = create_particle()
                new_particles.append(particle)
                new_traces.append(trace)
                particles.append(particle)
                traces.append(trace)
            return new_particles, new_traces
        
        # Обновление движения частиц
        def update_particle(mob, dt, vector_field=vector_field_func):
            pos = mob.get_center()
            velocity = vector_field(pos) * dt * time_scale  # Уменьшаем влияние dt на скорость
            mob.shift(velocity)

            # Ограничение длины следа
            trace = mob.trace  # Теперь ссылка на трассу хранится в атрибуте частицы
            if len(trace.points) > MAX_TRACE_LENGTH:
                trace.points = trace.points[-MAX_TRACE_LENGTH:]  # Оставляем только последние MAX_TRACE_LENGTH точек

        # Удаление точек, выходящих за пределы экрана
        def remove_offscreen_particles():
            nonlocal particles
            for i in reversed(range(len(particles))):
                particle = particles[i]
                pos = particle.get_center()
                if abs(pos[0]) > SCREEN_WIDTH or abs(pos[1]) > SCREEN_HEIGHT:
                    self.remove(particle)  # Удаляем только частицу
                    self.remove(particle.trace)  # Удаляем след
                    particles.pop(i)
                    traces.pop(i)

        # Создаём таймер для добавления точек
        time_elapsed = 0

        def update_scene(dt):
            nonlocal time_elapsed
            time_elapsed += dt
            if time_elapsed >= SPAWN_INTERVAL:
                spawn_particles()
                time_elapsed = 0
            remove_offscreen_particles()

        # Создание начальных частиц
        for _ in range(N):
            particle, trace = create_particle()
            particles.append(particle)
            traces.append(trace)

        # Устанавливаем фон сцены на чёрный
        self.camera.background_color = BLACK

        # Добавляем updater для обновления сцены
        self.add_updater(update_scene)

        # Анимация сцены задаётся по времени (см.параметры)
        self.wait(ani_time)
