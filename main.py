import flet as f
import time
from datetime import datetime
import textwrap


class Task(f.UserControl):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    @staticmethod
    def get_time_stamp():
        current_datetime = datetime.now()
        uk_date_time = current_datetime.strftime("%d/%m/%Y at %H:%M")
        return f'{uk_date_time} \U0001F44A'

    def wrap_label(self, label):
        wrapper = textwrap.TextWrapper(width=70)
        wrapped_text = wrapper.fill(text=self.task_name)
        return wrapped_text

    def build(self):
        wrapped_label = self.wrap_label(self.task_name)

        self.display_task = f.Checkbox(
            value=False,
            label=wrapped_label,
            on_change=self.status_changed,
            tooltip='Complete'
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
        self.display_task.label = self.wrap_label(self.edit_name.value)
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        time.sleep(.5)
        self.completed = self.display_task.value
        if self.completed:
            timestamp = self.get_time_stamp()
            self.display_task.label = f"{self.wrap_label(self.task_name)} \U00002796 Completed on {timestamp}"
        else:
            self.display_task.label = self.wrap_label(self.task_name)
        self.update()
        self.task_status_change(self)

    def delete_clicked(self, e):
        self.task_delete(self)


class TodoApp(f.UserControl):
    def __init__(self):
        super().__init__()
        self.todo_title = "To Be Completed \U00002692"
        self.no_items_prompt = f"Awaiting Tasks \U000023F3"
        self.no_items_master_prompt = "\U0001F389 You have no tasks to complete."
        self.no_completed_items_prompt = '\U0001F5D1 You have no completed tasks.'
        self.no_items_master = f.Text(self.no_items_master_prompt)
        self.items_left = f.Text(self.no_items_prompt)
        self.no_completed_items = f.Text(self.no_completed_items_prompt)

        self.clear_button = f.OutlinedButton(
            text="Clear Completed Items", on_click=self.clear_clicked
        )
        self.new_task = f.TextField(
            on_submit=self.add_clicked,
            expand=True,
            multiline=True,
            autofocus=True
        )
        self.add_button = (
            f.FloatingActionButton(icon=f.icons.ADD, on_click=self.add_clicked)
        )
        self.title = f.Row(
            [f.Text(value=self.todo_title, style="headlineMedium")], alignment="center"
        )

    def build(self):
        self.tasks = f.Column()
        self.filter = f.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[f.Tab(text="Active"), f.Tab(text="Completed")],
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
                        self.clear_button,
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
            self.clear_button.visible = False

        elif self.filter.selected_index == 1:
            self.clear_button.visible = True

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
        if self.new_task.value:
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.new_task.focus()
            self.update()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update_completed_tasks_prompt_visibility()
        self.update()

    def tabs_changed(self, e):
        def update_title():
            if self.filter.selected_index == 0:
                self.title.controls = [f.Text(value=self.todo_title, style="headlineMedium")]

            elif self.filter.selected_index == 1:
                self.title.controls = [f.Text(value="Completed \U00002705", style="headlineMedium")]

        def refresh():
            # self.show_completed_tasks(self.fetch_completed_tasks())  # add this to an export completed tasks button
            self.fetch_completed_tasks()
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
        for task in self.tasks.controls[:]:
            if task.completed:
                self.task_delete(task)

    def fetch_completed_tasks(self):
        completed_tasks = []
        for task in self.tasks.controls:
            if self.filter.selected_index == 1 and task.completed:
                completed_tasks.append(task.display_task.label)

        return completed_tasks

    @staticmethod
    def show_completed_tasks(func):
        with open('completed_Tasks.txt', 'a', encoding='utf-8') as w:
            for comp in func:
                w.write(f'{comp} \n')

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "Active" and task.completed is False
                or (status == "Completed" and task.completed)
            )
            if not task.completed:
                count += 1

        if count == 0:
            self.items_left.value = self.no_items_prompt
            self.no_items_master.value = self.no_items_master_prompt
            super().update()

        elif count == 1:
            self.items_left.value = f"{count} Active Task \U0001F4A5"
            self.no_items_master.value = ''
            super().update()

        else:
            self.items_left.value = f"{count} Active Tasks \U0001F525"
            self.no_items_master.value = ''
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


f.app(target=main)
