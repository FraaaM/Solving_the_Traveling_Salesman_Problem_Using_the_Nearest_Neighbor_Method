import tkinter as tk
from tkinter import ttk
import math
from tkinter.simpledialog import askinteger

class TSPApp:
    NODE_SIZE = 12
    MIN_SPACING = 40
    SELECTION_RADIUS = 17

    def __init__(self, root):
        self.root = root
        self.root.title("Решение задачи маршрута")
        self.root.geometry("1000x700")

        self.nodes = []
        self.connections = []
        self.history = []
        self.deleted_nodes = []
        self.node_id_tracker = 0
        self.active_node = None
        self.active_label_id = None
        self.use_modification_var = tk.BooleanVar(value=True)  


        self._setup_ui()
        self._center_window()

    def _setup_ui(self):
        core_frame = tk.Frame(self.root)
        core_frame.pack(fill="both", expand=True)
        core_frame.grid_columnconfigure(0, weight=1)
        core_frame.grid_columnconfigure(1, weight=1)
        core_frame.grid_rowconfigure(0, weight=1)

        panel_left = tk.Frame(core_frame)
        panel_left.grid(row=0, column=0, sticky="nsew")
        panel_left.grid_rowconfigure(0, weight=1)
        panel_left.grid_rowconfigure(1, weight=1)
        panel_left.grid_columnconfigure(0, weight=1)

        input_section = tk.LabelFrame(panel_left, text="Граф ввода")
        input_section.grid(row=0, column=0, sticky="nsew")
        self.input_area = tk.Canvas(input_section, bg="lightgray")
        self.input_area.grid(row=0, column=0, sticky="nsew")
        input_section.grid_rowconfigure(0, weight=1)
        input_section.grid_columnconfigure(0, weight=1)

        output_section = tk.LabelFrame(panel_left, text="Граф результата")
        output_section.grid(row=1, column=0, sticky="nsew")
        self.output_area = tk.Canvas(output_section, bg="lightgray")
        self.output_area.grid(row=0, column=0, sticky="nsew")
        output_section.grid_rowconfigure(0, weight=1)
        output_section.grid_columnconfigure(0, weight=1)

        panel_right = tk.Frame(core_frame)
        panel_right.grid(row=0, column=1, sticky="nsew")
        panel_right.grid_rowconfigure(0, weight=2)
        panel_right.grid_rowconfigure(1, weight=1)
        panel_right.grid_rowconfigure(2, weight=1)
        panel_right.grid_columnconfigure(0, weight=1)

        edges_section = tk.LabelFrame(panel_right, text="Список связей")
        edges_section.grid(row=0, column=0, sticky="nsew")
        self.edge_table = ttk.Treeview(edges_section, columns=("From", "To", "Cost"), show="headings")
        self.edge_table.heading("From", text="Начало")
        self.edge_table.heading("To", text="Конец")
        self.edge_table.heading("Cost", text="Вес")
        self.edge_table.pack(fill="both", expand=True)
        for col in ("From", "To", "Cost"):
            self.edge_table.column(col, width=60, stretch=True)
        
        control_section = tk.LabelFrame(panel_right, text="Управление")
        control_section.grid(row=1, column=0, sticky="nsew")
        ttk.Checkbutton(control_section, text="Использовать модификацию", variable=self.use_modification_var).pack(fill="x", expand=True)
        tk.Button(control_section, text="Найти маршрут", command=self._solve_tsp).pack(fill="x", expand=True)
        tk.Button(control_section, text="Назад", command=self._revert_last_step).pack(fill="x", expand=True)
        tk.Button(control_section, text="Сбросить", command=self._reset_all).pack(fill="x", expand=True)

        self.result_container = tk.LabelFrame(panel_right, text="Итоги")
        self.result_container.grid(row=2, column=0, sticky="nsew")
        tk.Label(self.result_container, text="Ожидание").pack(fill="both", expand=True)

        self.input_area.bind("<Button-1>", self._place_node)
        self.input_area.bind("<Button-3>", self._pick_node_for_link)

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

        if self.deleted_nodes:
            node_id = min(self.deleted_nodes)
            self.deleted_nodes.remove(node_id)
        else:
            self.node_id_tracker += 1
            node_id = self.node_id_tracker

        new_node = {"id": node_id, "x_coord": pos_x, "y_coord": pos_y}
        self.nodes.append(new_node)

        node_shape = self.input_area.create_oval(pos_x - self.NODE_SIZE, pos_y - self.NODE_SIZE, 
                                                 pos_x + self.NODE_SIZE, pos_y + self.NODE_SIZE, fill="green")
        label_id = self.input_area.create_text(pos_x, pos_y, text=str(node_id), fill="white")

        self.history.append(("node_added", new_node, node_shape, label_id))

    def _pick_node_for_link(self, event):
        pos_x, pos_y = event.x, event.y
        for node in self.nodes:
            dist = math.sqrt((pos_x - node["x_coord"])**2 + (pos_y - node["y_coord"])**2)
            if dist < self.SELECTION_RADIUS:
                if self.active_node is None:
                    self.active_node = node
                    self.active_label_id = self.input_area.create_text(node["x_coord"], node["y_coord"] - 30, 
                                                                      text=f"Выбран узел: {node['id']}", fill="green")
                    return
                else:
                    if self.active_node != node:
                        existing_link_idx = -1
                        for idx, link in enumerate(self.connections):
                            if link[0] == self.active_node["id"] and link[1] == node["id"]:
                                existing_link_idx = idx
                                break

                        if existing_link_idx != -1:
                            old_weight = self.connections[existing_link_idx][2]
                            new_weight = askinteger("Вес связи", 
                                                    f"Связь {self.active_node['id']} → {node['id']} существует. Вес: {old_weight}\nНовый вес:")
                            if new_weight is not None:
                                old_link = self.connections[existing_link_idx]
                                self.connections[existing_link_idx] = (self.active_node["id"], node["id"], new_weight, old_link[3])
                                self.edge_table.item(self.edge_table.get_children()[existing_link_idx], 
                                                     values=(self.active_node["id"], node["id"], new_weight))
                                self.history.append(("link_updated", old_link, self.connections[existing_link_idx]))

                            self.input_area.delete(self.active_label_id)
                            self.active_node = None
                            self.active_label_id = None
                            return

                        weight = askinteger("Вес связи", f"Укажите вес для связи {self.active_node['id']} → {node['id']}:")
                        if weight is None:
                            return

                        link_id = self._render_directed_link(self.active_node, node)
                        if link_id:
                            self.connections.append((self.active_node["id"], node["id"], weight, link_id))
                            self.edge_table.insert("", "end", values=(self.active_node["id"], node["id"], weight))
                            self.history.append(("link_added", (self.active_node["id"], node["id"], weight, link_id)))

                        self.input_area.delete(self.active_label_id)
                        self.active_node = None
                        self.active_label_id = None
                    else:
                        self.input_area.delete(self.active_label_id)
                        self.active_node = None
                        self.active_label_id = None

    def _render_directed_link(self, start, end):
        dx = end["x_coord"] - start["x_coord"]
        dy = end["y_coord"] - start["y_coord"]
        length = math.sqrt(dx**2 + dy**2)
        if length == 0:
            return None
        dx /= length
        dy /= length
        begin_x = start["x_coord"] + dx * self.NODE_SIZE
        begin_y = start["y_coord"] + dy * self.NODE_SIZE
        finish_x = end["x_coord"] - dx * self.NODE_SIZE
        finish_y = end["y_coord"] - dy * self.NODE_SIZE
        link_id = self.input_area.create_line(begin_x, begin_y, finish_x, finish_y, 
                                              arrow=tk.LAST, fill="black", width=2, 
                                              arrowshape=(8, 8, 4))
        return link_id

    def _display_optimal_route(self, route, graph_data):
        self.output_area.delete("all")
        for node_id in route:
            node = next(n for n in self.nodes if n["id"] == node_id)
            self.output_area.create_oval(node["x_coord"] - self.NODE_SIZE, node["y_coord"] - self.NODE_SIZE, 
                                         node["x_coord"] + self.NODE_SIZE, node["y_coord"] + self.NODE_SIZE, fill="green")
            self.output_area.create_text(node["x_coord"], node["y_coord"], text=str(node_id), fill="white")
        for i in range(len(route) - 1):
            start_node = next(n for n in self.nodes if n["id"] == route[i])
            end_node = next(n for n in self.nodes if n["id"] == route[i + 1])
            self._render_link_on_output(start_node, end_node)
        start_node = next(n for n in self.nodes if n["id"] == route[-1])
        end_node = next(n for n in self.nodes if n["id"] == route[0])
        self._render_link_on_output(start_node, end_node)

    def _render_link_on_output(self, start, end):
        dx = end["x_coord"] - start["x_coord"]
        dy = end["y_coord"] - start["y_coord"]
        length = math.sqrt(dx**2 + dy**2)
        if length == 0:
            return
        dx /= length
        dy /= length
        begin_x = start["x_coord"] + dx * self.NODE_SIZE
        begin_y = start["y_coord"] + dy * self.NODE_SIZE
        finish_x = end["x_coord"] - dx * self.NODE_SIZE
        finish_y = end["y_coord"] - dy * self.NODE_SIZE
        self.output_area.create_line(begin_x, begin_y, finish_x, finish_y, 
                                     arrow=tk.LAST, fill="red", width=2, 
                                     arrowshape=(8, 8, 4))

    def _choose_start_node(self, graph_data):
        min_cost = float('inf')
        start_node = None

        # Ищем узел с минимальной стоимостью перехода к ближайшему соседу
        for node in self.nodes:
            if graph_data[node["id"]]:  
                min_neighbor_cost = min(graph_data[node["id"]].values())
                if min_neighbor_cost < min_cost:
                    min_cost = min_neighbor_cost
                    start_node = node

        return start_node if start_node else self.nodes[0]  

    def _solve_tsp(self):
        for widget in self.result_container.winfo_children():
            widget.destroy()
        if len(self.nodes) < 2:
            tk.Label(self.result_container, text="Слишком мало узлов для расчёта").pack(fill="both", expand=True)
            self.output_area.delete("all")
            return
        
        # Строим граф
        graph_data = {node["id"]: {} for node in self.nodes}
        for link in self.connections:
            graph_data[link[0]][link[1]] = link[2]

        optimal_route = None
        min_total_cost = float('inf')

        use_modification = self.use_modification_var.get()
        start_nodes = self.nodes if use_modification else [self._choose_start_node(graph_data)] 

        for start_node in start_nodes:
            visited_nodes = {n["id"]: False for n in self.nodes}
            current_route = [start_node["id"]]
            total_cost = 0
            visited_nodes[start_node["id"]] = True
            current = start_node

            while len(current_route) < len(self.nodes):
                smallest_cost = float('inf')
                next_node_id = None

                # Ищем ближайшего соседа
                for neighbor, cost in graph_data[current["id"]].items():
                    if not visited_nodes[neighbor] and cost < smallest_cost:
                        smallest_cost = cost
                        next_node_id = neighbor

                if next_node_id is None:
                    break

                current_route.append(next_node_id)
                total_cost += smallest_cost
                visited_nodes[next_node_id] = True
                current = next(n for n in self.nodes if n["id"] == next_node_id)

            # Проверяем, можно ли вернуться в стартовый узел
            if len(current_route) == len(self.nodes) and start_node["id"] in graph_data[current["id"]]:
                total_cost += graph_data[current["id"]][start_node["id"]]
                if total_cost < min_total_cost:
                    min_total_cost = total_cost
                    optimal_route = current_route

        # Отображаем результат
        if optimal_route:
            result_text = f"Оптимальный маршрут: {' → '.join(map(str, optimal_route))} → {optimal_route[0]}\nОбщая стоимость: {min_total_cost}"
            self._display_optimal_route(optimal_route, graph_data)
        else:
            result_text = "Маршрут не найден"
            self.output_area.delete("all")
        tk.Label(self.result_container, text=result_text).pack(fill="both", expand=True)

    def _revert_last_step(self):
        if not self.history:
            return
        last_step = self.history.pop()
        if last_step[0] == "node_added":
            self.deleted_nodes.append(last_step[1]["id"])
            self.nodes.remove(last_step[1])
            self.input_area.delete(last_step[2])
            self.input_area.delete(last_step[3])
            if self.active_node == last_step[1]:
                if self.active_label_id:
                    self.input_area.delete(self.active_label_id)
                self.active_node = None
                self.active_label_id = None
        elif last_step[0] == "link_added":
            link_to_remove = last_step[1]
            self.connections = [link for link in self.connections if not (link[0] == link_to_remove[0] and link[1] == link_to_remove[1])]
            if link_to_remove[3]:
                self.input_area.delete(link_to_remove[3])
            for row in self.edge_table.get_children():
                if self.edge_table.item(row, "values")[:2] == (str(link_to_remove[0]), str(link_to_remove[1])):
                    self.edge_table.delete(row)
                    break
        elif last_step[0] == "link_updated":
            old_link, new_link = last_step[1], last_step[2]
            for i, link in enumerate(self.connections):
                if link[0] == new_link[0] and link[1] == new_link[1]:
                    self.connections[i] = old_link
                    self.edge_table.item(self.edge_table.get_children()[i], values=(old_link[0], old_link[1], old_link[2]))
                    break

    def _reset_all(self):
        self.edge_table.delete(*self.edge_table.get_children())
        self.input_area.delete("all")
        self.output_area.delete("all")
        self.nodes.clear()
        self.connections.clear()
        self.node_id_tracker = 0
        self.active_node = None
        if self.active_label_id:
            self.input_area.delete(self.active_label_id)
            self.active_label_id = None
        for widget in self.result_container.winfo_children():
            widget.destroy()
        tk.Label(self.result_container, text="Очищено").pack(fill="both", expand=True)

if __name__ == "__main__":
    app = tk.Tk()
    tsp_app = TSPApp(app)
    app.mainloop()