import flet as f, os, time, textwrap, pyrebase, json
from datetime import datetime


# Load Firebase configuration from JSON file
with open('firebaseServices.json') as config_file:
    config = json.load(config_file)

# Initialize Firebase app
firebase = pyrebase.initialize_app(config)
db = firebase.database()


def get_time_stamp():
    current_datetime = datetime.now()
    uk_date_time = current_datetime.strftime("%d/%m/%Y at %H:%M")
    return f'\U00002796 Completed on {uk_date_time} \U0001F44A'


class Task(f.UserControl):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def wrap_label(self, label):
        wrapper = textwrap.TextWrapper(width=67)
        wrapped_text = wrapper.fill(text=self.task_name)
        return wrapped_text

    def build(self):
        wrapped_label = self.wrap_label(self.task_name)

        self.display_task = f.Checkbox(
            value=False,
            label=wrapped_label,
            on_change=self.status_changed,
        )

        self.edit_name = f.TextField(
            expand=1,
            multiline=True,
            autofocus=True
        )

        self.display_view = f.Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.display_task,
                f.Row(
                    spacing=10,
                    run_spacing=10,
                    controls=[
                        f.IconButton(
                            icon=f.icons.CREATE_OUTLINED,
                            tooltip="Edit",
                            on_click=self.edit_clicked,
                        ),
                        f.IconButton(
                            f.icons.DELETE_OUTLINE,
                            tooltip="Delete",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = f.Row(
            visible=False,
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.edit_name,
                f.IconButton(
                    icon=f.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=f.colors.GREEN,
                    tooltip="Update",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return f.Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        old_task_name = self.task_name
        self.task_name = self.edit_name.value.replace(".", "")
        self.display_task.label = self.wrap_label(self.task_name)
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

        # Update the task name in the database
        task_data = db.child("tasks").child(old_task_name).get().val()
        db.child("tasks").child(old_task_name).remove()
        db.child("tasks").child(self.task_name).set(task_data)

    def status_changed(self, e):
        time.sleep(.5)
        self.completed = self.display_task.value
        if self.completed:
            self.display_task.label = self.wrap_label(self.task_name)

            # Updates the state in the database
            db.child("tasks").child(self.task_name).update({"completed": True})
            db.child("tasks").child(self.task_name).update({"completed_date": get_time_stamp()})

        else:
            self.display_task.label = self.wrap_label(self.task_name)
            db.child("tasks").child(self.task_name).update({"completed": False})
            db.child("tasks").child(self.task_name).child("completed_date").remove()

        self.task_status_change(self)
        self.update()

    def delete_clicked(self, e):
        self.task_delete(self)


class TodoApp(f.UserControl):
    def __init__(self):
        super().__init__()
        self.todo_title = "My Tasks \U0001F4CB"
        self.no_items_prompt = f"Awaiting New Tasks \U000023F3"
        self.no_items_master_prompt = "\U0001F389 You have no new tasks to complete."
        self.no_completed_items_prompt = '\U0001F5D1 You have no completed tasks.'
        self.no_items_master = f.Text(self.no_items_master_prompt)
        self.items_left = f.Text(self.no_items_prompt)
        self.no_completed_items = f.Text(self.no_completed_items_prompt)

        self.dropdown = f.Dropdown(
            icon=f.icons.MORE_HORIZ,
            tooltip='Options',
            alignment=f.alignment.center,
            border_color="transparent",
            border_radius=20,
            width=60,
            on_change=self.dropdown_changed,
            options=[
                f.dropdown.Option("Clear All Tasks"),
                f.dropdown.Option("Export All Tasks"),
            ],
        )

        self.new_task = f.TextField(
            on_submit=self.add_clicked,
            expand=True,
            multiline=True,
            autofocus=True
        )
        self.add_button = (
            f.FloatingActionButton(icon=f.icons.ADD, on_click=self.add_clicked, tooltip='Add Task')
        )
        self.title = f.Row(
            [f.Text(value=self.todo_title, style="headlineMedium")], alignment="center"
        )

    def build(self):
        self.tasks = f.Column()
        self.filter = f.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[f.Tab(text="Active Tasks"), f.Tab(text="Completed Tasks")],
        )

        self.update_button_visibility()
        self.update_completed_tasks_prompt_visibility()

        # application's root control (i.e. "view") containing all other controls
        return f.Column(
            width=600,
            controls=[
                f.Row(
                    alignment="center",
                    controls=[
                        self.title,
                    ],
                ),
                f.Row(
                    alignment="spaceBetween",
                    controls=[
                        f.Row(
                            controls=[
                                self.filter,
                            ],
                        ),
                        self.items_left,
                        self.dropdown,
                    ],
                ),
                f.Row(
                    controls=[
                        self.new_task,
                        self.add_button,
                    ],
                ),
                f.Column(
                    spacing=25,
                    controls=[
                        self.tasks,
                        self.no_items_master,
                        self.no_completed_items,
                    ],
                ),
            ],
        )

    def update_button_visibility(self):
        if self.filter.selected_index == 0:
            self.dropdown.visible = False

        elif self.filter.selected_index == 1:
            self.dropdown.visible = True

    def update_active_count_visibility(self):
        if self.filter.selected_index == 0:
            self.items_left.visible = True

        elif self.filter.selected_index == 1:
            self.items_left.visible = False

    def update_completed_tasks_prompt_visibility(self):
        if self.filter.selected_index == 1 and any(task.completed for task in self.tasks.controls):
            self.no_completed_items.visible = False

        elif self.filter.selected_index == 0:
            self.no_completed_items.visible = False

        else:
            self.no_completed_items.visible = True

    def update_active_count_master_visibility(self):
        if self.filter.selected_index == 0:
            self.no_items_master.visible = True

        elif self.filter.selected_index == 1:
            self.no_items_master.visible = False

    def update_input_visibility(self):
        if self.filter.selected_index == 0:
            self.new_task.visible = True
            self.add_button.visible = True

        elif self.filter.selected_index == 1:
            self.new_task.visible = False
            self.add_button.visible = False

    def add_clicked(self, e):
        task_name = self.new_task.value.strip()

        if task_name:
            task_name = task_name.replace(".", "")
            task = Task(task_name, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

            # Adds to the database
            db.child("tasks").child(task_name).set({"completed": False})

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update_completed_tasks_prompt_visibility()
        self.update()

        # removes task from the database
        db.child("tasks").child(task.task_name).remove()

    def tabs_changed(self, e):
        def update_title():
            if self.filter.selected_index == 0:
                self.title.controls = [f.Text(value=self.todo_title, style="headlineMedium")]

            elif self.filter.selected_index == 1:
                self.title.controls = [f.Text(value="My Completed Tasks \U00002705", style="headlineMedium")]

        def refresh():
            self.update_completed_tasks_prompt_visibility()
            self.update_active_count_master_visibility()
            self.update_input_visibility()
            self.update_active_count_visibility()
            self.update_button_visibility()
            self.update()

        if self.filter.selected_index == 0:
            update_title()
            refresh()

        elif self.filter.selected_index == 1:
            update_title()
            refresh()

    def clear_clicked(self, e):
        completed_tasks = []
        for task in self.tasks.controls[:]:
            if task.completed:
                completed_tasks.append(task)
                self.task_delete(task)

        # Remove all completed tasks from the database
        for task in completed_tasks:
            db.child("tasks").child(task.task_name).remove()

    def dropdown_changed(self, e):
        selected_value = self.dropdown.value

        if selected_value == 'Export All Tasks':
            self.show_completed_tasks(self.fetch_completed_tasks())

        if selected_value == 'Clear All Tasks':
            self.clear_clicked(e)

        self.dropdown.value = None
        self.update()

    @staticmethod
    def fetch_completed_tasks():
        completed_tasks = []
        tasks = db.child("tasks").get().val()

        for task_name, task_data in tasks.items():
            completed = task_data.get("completed", False)
            if completed:
                completed_date = task_data.get("completed_date")
                task = f'{task_name}\n{completed_date}\n\n'
                completed_tasks.append(task)

        return completed_tasks

    @staticmethod
    def show_completed_tasks(func):
        output_file = 'completeTasks.txt'
        with open(output_file, 'w', encoding='utf-8') as w:
            for completed in func:
                w.write(completed)

    def load_tasks_from_database(self):
        tasks = db.child("tasks").get().val()
        if tasks:
            for task_name, task_data in tasks.items():
                task = Task(task_name, self.task_status_change, self.task_delete)
                task.completed = task_data.get("completed", False)
                self.tasks.controls.append(task)
                self.update()

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        active_count = 0
        completed_count = 0

        for task in self.tasks.controls:
            task.visible = (
                    status == "Active Tasks" and not task.completed
                    or (status == "Completed Tasks" and task.completed)
            )

            if task.completed:
                completed_count += 1
            else:
                active_count += 1

        if status == "Active Tasks":
            if active_count == 0:
                self.items_left.value = self.no_items_prompt
                self.no_items_master.value = self.no_items_master_prompt

            elif active_count == 1:
                self.items_left.value = f"{active_count} Active Task \U0001F4A5"

                self.no_items_master.value = ''

            else:
                self.items_left.value = f"{active_count} Active Tasks \U0001F525"
                self.no_items_master.value = ''

        elif status == "Completed Tasks":
            if completed_count == 0:
                self.no_completed_items.visible = True

            else:
                self.no_completed_items.visible = False

        super().update()


def main(page: f.Page):
    page.title = "ToDo App"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    page.update()

    # create application instance
    app = TodoApp()

    # add application's root control to the page
    page.add(app)
    app.load_tasks_from_database()


f.app(target=main, view=f.WEB_BROWSER)
