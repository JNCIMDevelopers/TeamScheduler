# Standard Library Imports
import os
import sys
import subprocess
import traceback
from typing import List, Tuple, Callable
from datetime import datetime, date

# Third-Party Imports
import customtkinter
import tksheet
from tkcalendar import DateEntry
from tkinter import messagebox

# Local Imports
from config import (
    LOG_FILE_PATH,
    SCHEDULE_CSV_FILE_PATH,
    SCHEDULE_DETAILS_HTML_FILE_PATH,
)
from schedule_builder.builders.file_builder import get_schedule_data_for_csv
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
        self.undo_stack: list[EditAssignmentCommand] = []
        self.redo_stack: list[EditAssignmentCommand] = []

    # --- Public ---
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
        self._add_widgets()

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

        date_validation_message = self.schedule_handler.validate_dates(
            start_date=start_date, end_date=end_date
        )
        if date_validation_message:
            self._configure_validation_error_message(text=date_validation_message)
            return

        # Adjust dates if they are outside the available range
        start_date, end_date, is_adjusted = (
            self.schedule_handler.adjust_dates_within_range(
                start_date=start_date, end_date=end_date
            )
        )

        # Display alert message if dates were adjusted
        if is_adjusted:
            self._configure_alert_message(
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
            self._configure_error_message(message="An unexpected error occurred.")

    def show_schedule_popup(
        self, events: List[Event], team: List[Person], start_date: date, end_date: date
    ) -> None:
        """
        Displays a popup window with an editable preview of the schedule.

        Args:
            events (List[Event]): The list of events to display in the schedule.
            team (List[Person]): The list of team members involved in the schedule.
            start_date (date): The start date for the schedule.
            end_date (date): The end date for the schedule.
        """
        # Reset undo and redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Data
        schedule_data = get_schedule_data_for_csv(events=events)

        # Create a new popup window
        popup = customtkinter.CTkToplevel(self.app)
        popup.title("Schedule Preview")
        window_width = 1200
        window_height = 425
        x, y = self._get_window_position(
            window_width=window_width, window_height=window_height
        )
        popup.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Make popup the focus
        popup.transient(self.app)
        popup.grab_set()
        popup.focus_set()

        # Create a frame for the sheet
        frame = customtkinter.CTkFrame(popup)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Setup sheet
        columns = schedule_data[0]
        sheet = tksheet.Sheet(frame, data=schedule_data[1:], headers=columns)
        sheet.enable_bindings(("single_select", "cell_select"))
        sheet.pack(fill="both", expand=True)

        # Add double click event handler for editing blank cells
        self._handle_cell_editing(
            sheet=sheet,
            events=events,
            on_edit_command=self._execute_edit_command,
        )

        # Add undo button
        undo_btn = customtkinter.CTkButton(
            popup, text="Undo", command=lambda: self._undo_last_edit(sheet), width=10
        )
        undo_btn.pack(side="left", padx=5, pady=10)

        # Add redo button
        redo_btn = customtkinter.CTkButton(
            popup, text="Redo", command=lambda: self._redo_last_edit(sheet), width=10
        )
        redo_btn.pack(side="left", padx=5, pady=10)

        # Add a close button
        def close_popup():
            try:
                sheet.dehighlight_all()
                popup.destroy()
                self.schedule_handler.export_schedule(
                    start_date=start_date, end_date=end_date, events=events, team=team
                )
                self._configure_output_links()
            except PermissionError:
                self.app.logger.error(traceback.format_exc())
                self._configure_error_message(
                    message="Please close any open\noutput files and try again."
                )
            except Exception:
                self.app.logger.error(traceback.format_exc())
                self._configure_error_message(message="An unexpected error occurred.")

        close_btn = customtkinter.CTkButton(popup, text="Close", command=close_popup)
        close_btn.pack(pady=10)

    # --- Widget Management Methods ---
    def _add_widgets(self) -> None:
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

    def _reset_output_labels(self) -> None:
        """
        Resets the confirmation and output labels in the UI.

        Clears any existing text or bindings to ensure clean output for new messages or links.
        """
        self.app.confirmation_label.unbind("<Button-1>")
        self.app.output_link_label.unbind("<Button-1>")
        self.app.output_link_label.configure(text="", text_color="#4682B4")

    def _configure_alert_message(self, message: str) -> None:
        """
        Configures and displays an alert message in the UI.

        Args:
            message (str): The message to display in the alert dialog box.
        """
        messagebox.showinfo("Alert", message)
        self.app.logger.warning(message)

    def _configure_validation_error_message(self, text: str) -> None:
        """
        Displays a validation error message on the confirmation label.

        Args:
            text (str): The error message to display in red on the UI.
        """
        self._reset_output_labels()
        self.app.confirmation_label.configure(
            text=text,
            font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
            text_color="red",
            cursor="arrow",
        )

    def _configure_output_links(self) -> None:
        """
        Configures the UI to display links to the schedule and schedule details.

        Adds clickable labels that allow the user to open schedule-related files directly.
        """
        self._reset_output_labels()

        # Display link for schedule
        self.app.confirmation_label.bind(
            "<Button-1>",
            lambda e: self._handle_open_schedule_file(
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
            lambda e: self._handle_open_schedule_file(
                event=e,
                label=self.app.output_link_label,
                filepath=SCHEDULE_DETAILS_HTML_FILE_PATH,
            ),
        )
        self.app.output_link_label.configure(text="View Schedule Details")

    def _configure_error_message(self, message: str) -> None:
        """
        Configures the UI to display an error message with a link to the log file.

        Args:
            message (str): The error message to display in the UI.
        """
        self._reset_output_labels()
        self.app.confirmation_label.configure(
            text=message,
            font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
            text_color="red",
            cursor="arrow",
        )
        self.app.output_link_label.bind(
            "<Button-1>",
            lambda e: self._handle_open_schedule_file(
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

    # --- File Handling ---
    def _handle_open_schedule_file(
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

    # --- Undo/Redo ---
    def _execute_edit_command(self, command: EditAssignmentCommand) -> None:
        """
        Executes an edit command and manages the undo/redo stacks.

        Args:
            command (EditAssignmentCommand): The command to execute.
        """
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def _undo_last_edit(self, sheet: tksheet.Sheet) -> None:
        """
        Undoes the last edit made to the schedule.

        Args:
            sheet (tksheet.Sheet): The tksheet instance to update after undoing.
        """
        sheet.dehighlight_all()
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def _redo_last_edit(self, sheet: tksheet.Sheet) -> None:
        """
        Redoes the last undone edit made to the schedule.

        Args:
            sheet (tksheet.Sheet): The tksheet instance to update after redoing.
        """
        sheet.dehighlight_all()
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)

    # --- Sheet Editing ---

    def _handle_cell_editing(
        self,
        sheet: tksheet.Sheet,
        events: List[Event],
        on_edit_command: Callable,
    ) -> None:
        """
        Binds cell editing events to the Treeview.

        Args:
            sheet (tksheet.Sheet): The tksheet instance to bind the events to.
            events (List[Event]): The list of events to be displayed in the Treeview.
            on_edit_command (Callable): Function for editing cells.
        """

        def on_click(event):
            selected = sheet.get_selected_cells()
            if not selected:
                return

            # Ignore click events on the first column (role) and first two rows (preacher, graphics)
            row, col = list(selected)[0]
            if col == 0 or row in [0, 1]:
                return

            # Get the currently assigned name
            currently_assigned_name = sheet.get_cell_data(r=row, c=col)

            # Get event and role information
            role_str = sheet.get_cell_data(r=row, c=0)
            event_date_str = sheet.headers(index=col)
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

            # Add a blank option to the dropdown
            available_names = [""] + available_names

            # Destroy any existing dropdodown before creating a new one
            sheet.delete_dropdown("all", "all")

            # Create dropdown in the cell
            sheet.dropdown(
                row,
                col,
                values=available_names,
                set_value=currently_assigned_name,
                state="readonly",
                redraw=True,
            )

            def on_dropdown_select(event):
                selected_name = sheet.get_cell_data(r=row, c=col)
                if selected_name is None or selected_name == currently_assigned_name:
                    return

                old_person = (
                    event_obj.get_person_by_name(name=currently_assigned_name)
                    if currently_assigned_name
                    else None
                )
                new_person = (
                    event_obj.get_person_by_name(name=selected_name)
                    if selected_name
                    else None
                )

                # Save command to undo/redo stack
                cmd = EditAssignmentCommand(
                    event=event_obj,
                    role=role,
                    old_person=old_person,
                    new_person=new_person,
                    sheet=sheet,
                    row=row,
                    column=col,
                    logger=self.app.logger,
                )
                on_edit_command(cmd)
                self._highlight_cells_with_value(sheet=sheet, value=selected_name)

            sheet.extra_bindings([("end_edit_cell", on_dropdown_select)])

        sheet.extra_bindings([("cell_select", on_click)])

    def _highlight_cells_with_value(
        self, sheet: tksheet.Sheet, value: str, bg: str = "#fff59d"
    ):
        sheet.dehighlight_all()
        if not value:
            return

        data = sheet.get_sheet_data()
        for r, row in enumerate(data):
            for c, cell in enumerate(row):
                if cell == value:
                    sheet.highlight_cells(row=r, column=c, bg=bg)

    # --- Utility ---
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
