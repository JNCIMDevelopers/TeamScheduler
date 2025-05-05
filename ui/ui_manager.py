# Standard Library Imports
import os
import sys
import subprocess
import traceback

# Third-Party Imports
import customtkinter
from tkcalendar import DateEntry
from tkinter import messagebox

# Local Imports
from config import (
    LOG_FILE_PATH,
    SCHEDULE_CSV_FILE_PATH,
    SCHEDULE_DETAILS_HTML_FILE_PATH,
)
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

    Attributes:
        app (customtkinter.CTk): The main application instance, responsible for managing the app window.
        schedule_handler (UIScheduleHandler): A handler for managing schedule-related logic and data.
        title (str): The title of the application window.
    """

    def __init__(
        self,
        app: customtkinter.CTk,
        schedule_handler: UIScheduleHandler,
        title: str,
    ):
        """
        Initializes the UIManager with the main app instance, schedule handler, and window title.

        Args:
            app (customtkinter.CTk): The main application instance.
            schedule_handler (UIScheduleHandler): The handler responsible for managing the schedule.
            title (str): The title for the application window.
        """
        self.app = app
        self.schedule_handler = schedule_handler
        self.title = title

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
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.app.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create frame to hold all widgets
        self.app.frame = customtkinter.CTkFrame(master=self.app)
        self.app.frame.pack(pady=20, padx=60, fill="both", expand=True)

        # Add widgets to the frame
        self.add_widgets()

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
            self.schedule_handler.create_schedule(
                start_date=start_date, end_date=end_date
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
