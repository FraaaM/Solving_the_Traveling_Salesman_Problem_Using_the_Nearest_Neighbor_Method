import tkinter as tk
from tkinter import ttk
import math

class TSPApp:
    NODE_SIZE = 15
    MIN_SPACING = 50
    SELECTION_RADIUS = 20

    def __init__(self, root):
        self.root = root
        self.root.title("Решение задачи маршрута (Прототип)") 
        self.root.geometry("1000x700")

        self.nodes = []  # Список узлов
        self.edges = []  # Список рёбер
        self.history = []  # История для отмены действий
        # TODO: Добавить поддержку удалённых узлов (deleted_nodes) в будущем
        self.node_id_tracker = 0  # Счётчик узлов
        self.active_node = None  # Выбранный узел
        self.active_label_id = None  # ID текста выбора узла

        self._setup_ui()  # Настройка интерфейса
        self._center_window()  # Центрирование окна

    def _setup_ui(self):
        # Основной фрейм
        core_frame = tk.Frame(self.root)
        core_frame.pack(fill="both", expand=True)
        core_frame.grid_columnconfigure(0, weight=1)
        core_frame.grid_columnconfigure(1, weight=1)
        core_frame.grid_rowconfigure(0, weight=1)

        # Левый фрейм для канвасов
        panel_left = tk.Frame(core_frame)
        panel_left.grid(row=0, column=0, sticky="nsew")
        panel_left.grid_rowconfigure(0, weight=1)
        panel_left.grid_rowconfigure(1, weight=1)
        panel_left.grid_columnconfigure(0, weight=1)

        # Входной канвас (для добавления узлов)
        input_section = tk.LabelFrame(panel_left, text="Граф ввода")
        input_section.grid(row=0, column=0, sticky="nsew")
        self.input_area = tk.Canvas(input_section, bg="lightgray")
        self.input_area.grid(row=0, column=0, sticky="nsew")
        input_section.grid_rowconfigure(0, weight=1)
        input_section.grid_columnconfigure(0, weight=1)

        # Выходной канвас (пока пустой)
        output_section = tk.LabelFrame(panel_left, text="Граф результата")
        output_section.grid(row=1, column=0, sticky="nsew")
        self.output_area = tk.Canvas(output_section, bg="lightgray")
        self.output_area.grid(row=0, column=0, sticky="nsew")
        output_section.grid_rowconfigure(0, weight=1)
        output_section.grid_columnconfigure(0, weight=1)

        # Правый фрейм для управления
        panel_right = tk.Frame(core_frame)
        panel_right.grid(row=0, column=1, sticky="nsew")
        panel_right.grid_rowconfigure(0, weight=2)
        panel_right.grid_rowconfigure(1, weight=1)
        panel_right.grid_rowconfigure(2, weight=1)
        panel_right.grid_columnconfigure(0, weight=1)

        # Таблица рёбер (пока без данных)
        edges_section = tk.LabelFrame(panel_right, text="Список связей")
        edges_section.grid(row=0, column=0, sticky="nsew")
        self.edge_table = ttk.Treeview(edges_section, columns=("From", "To", "Cost"), show="headings")
        self.edge_table.heading("From", text="Начало")
        self.edge_table.heading("To", text="Конец")
        self.edge_table.heading("Cost", text="Вес")
        self.edge_table.pack(fill="both", expand=True)
        for col in ("From", "To", "Cost"):
            self.edge_table.column(col, width=60, stretch=True)

        # Кнопки управления
        control_section = tk.LabelFrame(panel_right, text="Управление")
        control_section.grid(row=1, column=0, sticky="nsew")
        tk.Button(control_section, text="Найти маршрут", command=self._solve_tsp).pack(fill="x", expand=True)
        tk.Button(control_section, text="Назад", command=self._revert_last_step).pack(fill="x", expand=True)
        tk.Button(control_section, text="Сбросить", command=self._reset_all).pack(fill="x", expand=True)

        # Панель результатов
        self.result_container = tk.LabelFrame(panel_right, text="Итоги")
        self.result_container.grid(row=2, column=0, sticky="nsew")
        tk.Label(self.result_container, text="Ожидание").pack(fill="both", expand=True)

        # Привязка событий 
        self.input_area.bind("<Button-1>", self._place_node)
        # TODO: Добавить обработку правого клика для связей в следующем коммите

    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _place_node(self, event):
        pos_x, pos_y = event.x, event.y
        for node in self.nodes:
            dist = math.sqrt((pos_x - node["x_coord"])**2 + (pos_y - node["y_coord"])**2)
            if dist < self.MIN_SPACING:
                return

        self.node_id_tracker += 1  # TODO: Добавить поддержку удалённых узлов позже
        node_id = self.node_id_tracker
        new_node = {"id": node_id, "x_coord": pos_x, "y_coord": pos_y}
        self.nodes.append(new_node)

        node_shape = self.input_area.create_oval(pos_x - self.NODE_SIZE, pos_y - self.NODE_SIZE, 
                                                 pos_x + self.NODE_SIZE, pos_y + self.NODE_SIZE, fill="green")
        label_id = self.input_area.create_text(pos_x, pos_y, text=str(node_id), fill="white")

        self.history.append(("node_added", new_node, node_shape, label_id))

    def _pick_node_for_link(self, event):
        # TODO: Реализовать выбор узлов и добавление рёбер в следующем коммите
        pass

    def _render_directed_link(self, start, end):
        # TODO: Добавить отрисовку рёбер после реализации _pick_node_for_link
        pass

    def _display_optimal_route(self, route, graph_data):
        # TODO: Реализовать отображение маршрута после завершения алгоритма TSP
        pass

    def _render_link_on_output(self, start, end):
        # TODO: Добавить отрисовку рёбер на выходном канвасе позже
        pass

    def _solve_tsp(self):
        # TODO: Реализовать алгоритм TSP в будущем коммите
        for widget in self.result_container.winfo_children():
            widget.destroy()
        tk.Label(self.result_container, text="Функция в разработке").pack(fill="both", expand=True)

    def _revert_last_step(self):
        # Базовая отмена добавления узла
        if not self.history:
            return
        last_step = self.history.pop()
        if last_step[0] == "node_added":
            self.nodes.remove(last_step[1])
            self.input_area.delete(last_step[2])
            self.input_area.delete(last_step[3])
        # TODO: Добавить поддержку отмены рёбер позже

    def _reset_all(self):
        # Базовый сброс
        self.input_area.delete("all")
        self.output_area.delete("all")
        self.nodes.clear()
        self.node_id_tracker = 0
        for widget in self.result_container.winfo_children():
            widget.destroy()
        tk.Label(self.result_container, text="Очищено").pack(fill="both", expand=True)
        # TODO: Очистить таблицу рёбер и связи после их реализации

if __name__ == "__main__":
    app = tk.Tk()
    tsp_app = TSPApp(app)
    app.mainloop()