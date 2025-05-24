# Standard Library Imports
import os
import sys
import subprocess
import traceback
from typing import List, Tuple, Callable
from datetime import datetime, date

# Third-Party Imports
import customtkinter
from tkcalendar import DateEntry
from tkinter import messagebox, ttk

# Local Imports
from config import (
    LOG_FILE_PATH,
    SCHEDULE_CSV_FILE_PATH,
    SCHEDULE_DETAILS_HTML_FILE_PATH,
)
from schedule_builder.builders.file_builder import (
    get_schedule_data_for_csv,
    format_data_for_csv,
)
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role
from ui.command import EditAssignmentCommand
from ui.ui_schedule_handler import UIScheduleHandler

# Appearance settings for customtkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


class UIManager:
    """
    Manages the user interface for the scheduling application.

    This class handles the setup of the main window, widget creation, and event handling
    for various UI elements. It is responsible for displaying and updating the schedule-related
    UI, including date entries, buttons, confirmation messages, and links to schedule outputs.
    """

    def __init__(
        self,
        app: customtkinter.CTk,
        schedule_handler: UIScheduleHandler,
        title: str,
    ):
        """
        Initializes an instance of the UIManager class.

        Args:
            app (customtkinter.CTk): The main application instance.
            schedule_handler (UIScheduleHandler): The handler responsible for managing the schedule.
            title (str): The title for the application window.
        """
        self.app = app
        self.schedule_handler = schedule_handler
        self.title = title
        self.active_combo = None

    def setup(self) -> None:
        """
        Sets up the user interface by configuring the window, layout, and widgets.

        This method centers the window on the screen and adds the necessary UI components such as
        labels, date entry fields, buttons, and other elements to the window.
        """
        # Setup window
        self.app.title(self.title)
        self.app.STANDARD_FONT = "Roboto"
        self.app.CONFIRMATION_LABEL_FONT_SIZE = 20

        window_width = 500
        window_height = 375
        x, y = self._get_window_position(
            window_width=window_width, window_height=window_height
        )
        self.app.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create frame to hold all widgets
        self.app.frame = customtkinter.CTkFrame(master=self.app)
        self.app.frame.pack(pady=20, padx=60, fill="both", expand=True)

        # Add widgets to the frame
        self.add_widgets()

    def _get_window_position(
        self, window_width: int, window_height: int
    ) -> Tuple[int, int]:
        """
        Calculates the position to center the window on the screen.

        Returns:
            tuple: A tuple containing the x and y coordinates for centering the window.
        """
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        return x, y

    def add_widgets(self) -> None:
        """
        Adds all widgets (labels, buttons, date pickers) to the main window.
        """
        # Title label
        self.app.title_label = customtkinter.CTkLabel(
            master=self.app.frame,
            text="Schedule Builder",
            font=(self.app.STANDARD_FONT, 24),
        )
        self.app.title_label.pack(pady=20)

        # Start date label and entry
        self.app.start_date_label = customtkinter.CTkLabel(
            master=self.app.frame, text="START DATE", font=(self.app.STANDARD_FONT, 14)
        )
        self.app.start_date_label.pack()
        self.app.start_date_entry = DateEntry(
            master=self.app.frame,
            selectmode="day",
            locale="en_US",
            date_pattern="MM/dd/yyyy",
            font=(self.app.STANDARD_FONT, 12),
        )
        self.app.start_date_entry.pack(pady=(0, 10))

        # End date label and entry
        self.app.end_date_label = customtkinter.CTkLabel(
            master=self.app.frame, text="END DATE", font=(self.app.STANDARD_FONT, 14)
        )
        self.app.end_date_label.pack()
        self.app.end_date_entry = DateEntry(
            master=self.app.frame,
            selectmode="day",
            locale="en_US",
            date_pattern="MM/dd/yyyy",
            font=(self.app.STANDARD_FONT, 12),
        )
        self.app.end_date_entry.pack(pady=(0, 10))

        # Create button
        self.app.create_button = customtkinter.CTkButton(
            master=self.app.frame,
            text="CREATE",
            command=self.handle_create_button_click,
            font=(self.app.STANDARD_FONT, 14),
        )
        self.app.create_button.pack(pady=10)

        # Confirmation label
        self.app.confirmation_label = customtkinter.CTkLabel(
            master=self.app.frame,
            text="",
            font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
            wraplength=350,
        )
        self.app.confirmation_label.pack(pady=5)

        # Schedule details ouput label
        self.app.output_link_label = customtkinter.CTkLabel(
            master=self.app.frame,
            text="",
            font=(
                self.app.STANDARD_FONT,
                self.app.CONFIRMATION_LABEL_FONT_SIZE,
                "underline",
            ),
            text_color="#4682B4",
            cursor="hand2",
            wraplength=350,
        )
        self.app.output_link_label.pack(pady=5)

    def show_schedule_popup(
        self, events: List[Event], team: List[Person], start_date: date, end_date: date
    ) -> None:
        # Undo, redo stack
        self.undo_stack: list[EditAssignmentCommand] = []
        self.redo_stack: list[EditAssignmentCommand] = []

        # Data
        data = get_schedule_data_for_csv(events=events)
        formatted_data = format_data_for_csv(data=data)

        # Create a new popup window
        popup = customtkinter.CTkToplevel(self.app)
        popup.title("Schedule Preview")
        window_width = 1200
        window_height = 400
        x, y = self._get_window_position(
            window_width=window_width, window_height=window_height
        )
        popup.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Make popup the focus
        popup.transient(self.app)
        popup.grab_set()
        popup.focus_set()

        # Create a frame for the Treeview
        frame = ttk.Frame(popup)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Define columns (customize as needed)
        columns = formatted_data[0]
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)

        # Insert schedule data
        for record in formatted_data[1:]:
            tree.insert("", "end", values=record)

        tree.pack(fill="both", expand=True)

        # Add horizontal scrollbar
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")

        def on_edit_command(command: EditAssignmentCommand) -> None:
            command.execute()
            self.undo_stack.append(command)
            self.redo_stack.clear()

        # Add double click event handler for editing blank cells
        row_ids = list(tree.get_children())
        self._handle_cell_editing(
            tree=tree,
            row_ids=row_ids,
            columns=columns,
            events=events,
            on_edit_command=on_edit_command,
        )

        def undo_last_edit():
            self._close_combobox()
            if self.undo_stack:
                command = self.undo_stack.pop()
                command.undo()
                self.redo_stack.append(command)

        def redo_last_edit():
            self._close_combobox()
            if self.redo_stack:
                command = self.redo_stack.pop()
                command.execute()
                self.undo_stack.append(command)

        # Add undo and redo buttons
        undo_btn = customtkinter.CTkButton(
            popup, text="Undo", command=undo_last_edit, width=10
        )
        undo_btn.pack(side="left", padx=5, pady=10)

        redo_btn = customtkinter.CTkButton(
            popup, text="Redo", command=redo_last_edit, width=10
        )
        redo_btn.pack(side="left", padx=5, pady=10)

        # Add a close button
        def close_popup():
            try:
                popup.destroy()
                self.schedule_handler.export_schedule(
                    start_date=start_date, end_date=end_date, events=events, team=team
                )
                self.configure_output_links()
            except PermissionError:
                self.app.logger.error(traceback.format_exc())
                self.configure_error_message(
                    message="Please close any open\noutput files and try again."
                )
            except Exception:
                self.app.logger.error(traceback.format_exc())
                self.configure_error_message(message="An unexpected error occurred.")

        close_btn = customtkinter.CTkButton(popup, text="Close", command=close_popup)
        close_btn.pack(pady=10)

    def _handle_cell_editing(
        self,
        tree: ttk.Treeview,
        row_ids: List[str],
        columns: List[str],
        events: List[Event],
        on_edit_command: Callable,
    ) -> None:
        """
        Binds cell editing events to the Treeview.

        Args:
            tree (ttk.Treeview): The Treeview widget.
            columns (List[str]): The list of column names.
            events (List[Event]): The list of events to be displayed in the Treeview.
        """

        def on_click(event):
            # Check if the click event region is a cell
            region = tree.identify_region(event.x, event.y)
            if region != "cell":
                return

            # Ignore click events on the first column (role) and first two rows (preacher, graphics)
            row_id = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            column_index = int(column.replace("#", "")) - 1
            if column_index == 0 or row_id in row_ids[:2]:
                return

            # Get the currently assigned name
            values = list(tree.item(row_id, "values"))
            currently_assigned_name = values[column_index].strip()

            # Get event and role information
            role_str = values[0]
            event_date_str = columns[column_index]
            formatted_event_date_str = datetime.strptime(
                event_date_str, "%B %d, %Y"
            ).strftime("%Y-%m-%d")
            event_obj = self.schedule_handler.get_event_by_date(
                events=events, event_date_str=formatted_event_date_str
            )
            role = Role(role_str)

            # Get available names for the selected event and role
            available_names = (
                self.schedule_handler.get_available_replacements_for_event(
                    event=event_obj, role=role
                )
            )
            if not available_names:
                return

            # Create a combobox for selecting a name
            self._close_combobox()
            x, y, width, height = tree.bbox(row_id, column)
            combo = ttk.Combobox(tree, values=available_names, state="readonly")
            combo.place(x=x, y=y, width=width, height=height)
            combo.focus_set()
            self.active_combo = combo

            def on_select(event, currently_assigned_name):
                selected_name = combo.get()
                if not selected_name or selected_name == currently_assigned_name:
                    self._close_combobox()
                    return

                old_person = (
                    event_obj.get_person_by_name(name=currently_assigned_name)
                    if currently_assigned_name
                    else None
                )
                new_person = event_obj.get_person_by_name(name=selected_name)

                # Save command to undo/redo stack
                cmd = EditAssignmentCommand(
                    event=event_obj,
                    role=role,
                    old_person=old_person,
                    new_person=new_person,
                    tree=tree,
                    row_id=row_id,
                    column_index=column_index,
                    logger=self.app.logger,
                )
                on_edit_command(cmd)
                self._close_combobox()

            combo.bind(
                "<<ComboboxSelected>>",
                lambda event: on_select(event, currently_assigned_name),
            )
            combo.bind("<Escape>", self._close_combobox)

            return "break"  # Prevent default behavior of the treeview

        tree.bind("<Button-1>", on_click)

    def _close_combobox(self, event=None) -> None:
        """
        Closes the currently active combobox if it exists.

        Args:
            event: The event that triggered this method (if any).
        """
        if self.active_combo:
            try:
                self.active_combo.destroy()
            except Exception:
                pass
            self.active_combo = None

    def reset_output_labels(self) -> None:
        """
        Resets the confirmation and output labels in the UI.

        Clears any existing text or bindings to ensure clean output for new messages or links.
        """
        self.app.confirmation_label.unbind("<Button-1>")
        self.app.output_link_label.unbind("<Button-1>")
        self.app.output_link_label.configure(text="", text_color="#4682B4")

    def configure_alert_message(self, message: str) -> None:
        """
        Configures and displays an alert message in the UI.

        Args:
            message (str): The message to display in the alert dialog box.
        """
        messagebox.showinfo("Alert", message)
        self.app.logger.warning(message)

    def configure_validation_error_message(self, text: str) -> None:
        """
        Displays a validation error message on the confirmation label.

        Args:
            text (str): The error message to display in red on the UI.
        """
        self.reset_output_labels()
        self.app.confirmation_label.configure(
            text=text,
            font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
            text_color="red",
            cursor="arrow",
        )

    def configure_output_links(self) -> None:
        """
        Configures the UI to display links to the schedule and schedule details.

        Adds clickable labels that allow the user to open schedule-related files directly.
        """
        self.reset_output_labels()

        # Display link for schedule
        self.app.confirmation_label.bind(
            "<Button-1>",
            lambda e: self.handle_open_schedule_file(
                event=e,
                label=self.app.confirmation_label,
                filepath=SCHEDULE_CSV_FILE_PATH,
            ),
        )
        self.app.confirmation_label.configure(
            text="View Schedule",
            font=(
                self.app.STANDARD_FONT,
                self.app.CONFIRMATION_LABEL_FONT_SIZE,
                "underline",
            ),
            text_color="#4682B4",
            cursor="hand2",
        )

        # Display link for schedule details
        self.app.output_link_label.bind(
            "<Button-1>",
            lambda e: self.handle_open_schedule_file(
                event=e,
                label=self.app.output_link_label,
                filepath=SCHEDULE_DETAILS_HTML_FILE_PATH,
            ),
        )
        self.app.output_link_label.configure(text="View Schedule Details")

    def configure_error_message(self, message: str) -> None:
        """
        Configures the UI to display an error message with a link to the log file.

        Args:
            message (str): The error message to display in the UI.
        """
        self.reset_output_labels()
        self.app.confirmation_label.configure(
            text=message,
            font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
            text_color="red",
            cursor="arrow",
        )
        self.app.output_link_label.bind(
            "<Button-1>",
            lambda e: self.handle_open_schedule_file(
                event=e, label=self.app.output_link_label, filepath=LOG_FILE_PATH
            ),
        )
        self.app.output_link_label.configure(
            text="Click to view logs.",
            font=(
                self.app.STANDARD_FONT,
                self.app.CONFIRMATION_LABEL_FONT_SIZE,
                "underline",
            ),
        )

    def handle_open_schedule_file(
        self, event, label: customtkinter.CTkLabel, filepath: str
    ) -> None:
        """
        Opens the specified schedule file and updates the link color.

        Args:
            event: The event that triggered this handler (if any).
            label (customtkinter.CTkLabel): The label associated with the file link.
            filepath (str): The path to the file to open.
        """
        full_path = os.path.abspath(filepath)
        if sys.platform == "win32":
            os.startfile(full_path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, full_path])

        label.configure(text_color="#9b30ff")

    def handle_create_button_click(self) -> None:
        """
        Handles the 'CREATE' button click event.

        Validates the input dates, adjusts them if necessary, creates the schedule, and
        updates the UI with results or error messages.
        """
        start_date = self.app.start_date_entry.get_date()
        end_date = self.app.end_date_entry.get_date()

        self.app.logger.debug(f"Start Date Entry: {str(start_date)}")
        self.app.logger.debug(f"End Date Entry: {str(end_date)}")

        # Missing input validation
        if not start_date or not end_date:
            self.configure_validation_error_message(text="Missing Input!")
            return

        # Invalid date range validation
        if start_date > end_date:
            self.configure_validation_error_message(text="Invalid Input!")
            return

        if (
            not self.schedule_handler.is_within_date_range(start_date)
            and not self.schedule_handler.is_within_date_range(end_date)
            and not self.schedule_handler.is_preaching_schedule_within_date_range(
                start_date, end_date
            )
        ):
            self.configure_validation_error_message(
                text="No preaching schedule available within specified dates!"
            )
            return

        # Adjust dates if they are outside the available range
        start_date, end_date, is_adjusted = (
            self.schedule_handler.adjust_dates_within_range(
                start_date=start_date, end_date=end_date
            )
        )

        # Display alert message if dates were adjusted
        if is_adjusted:
            self.configure_alert_message(
                message=f"Preaching schedule is only available from {str(start_date)} to {str(end_date)}."
            )

        # Create schedule and display output links
        try:
            events, updated_team = self.schedule_handler.build_schedule(
                start_date=start_date, end_date=end_date
            )
            self.show_schedule_popup(
                events=events,
                team=updated_team,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception:
            self.app.logger.error(traceback.format_exc())
            self.configure_error_message(message="An unexpected error occurred.")
