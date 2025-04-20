# Standard Library Imports
import os
import sys
import subprocess
import traceback

# Third-Party Imports
import customtkinter
from tkinter import messagebox

# Local Imports
from paths import LOG_FILE_PATH, SCHEDULE_CSV_FILE_PATH, SCHEDULE_DETAILS_HTML_FILE_PATH
from ui.ui_schedule_handler import UIScheduleHandler


class UIEventHandler:
    """
    Handles user interactions and events in the application.

    This class manages button clicks, file opening, and error handling for
    the user interface.
    """

    def __init__(
        self, app: customtkinter.CTk, schedule_handler: UIScheduleHandler
    ) -> None:
        """
        Initializes the event handler with the application and schedule handler.

        Args:
            app (customtkinter.CTk): The main application instance.
            schedule_handler (UIScheduleHandler): The handler for schedule-related logic.
        """
        self.app = app
        self.schedule_handler = schedule_handler

    def handle_open_schedule_file(
        self, event, label: customtkinter.CTkLabel, filepath: str
    ) -> None:
        """
        Opens a schedule file based on the operating system and updates the link color.

        Args:
            event: The event that triggered this handler (if any).
            label (customtkinter.CTkLabel): The label that was clicked.
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

        This method validates the input dates, adjusts them if necessary, creates
        a schedule, and updates the UI with the results or error messages.
        """
        start_date = self.app.start_date_entry.get_date()
        self.app.logger.debug(f"Start Date: {str(start_date)}")

        end_date = self.app.end_date_entry.get_date()
        self.app.logger.debug(f"End Date: {str(end_date)}")

        if not start_date or not end_date:
            self.reset_output_labels()
            self.app.confirmation_label.configure(
                text="Missing Input!",
                font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
                text_color="red",
                cursor="arrow",
            )
            return

        if start_date > end_date:
            self.reset_output_labels()
            self.app.confirmation_label.configure(
                text="Invalid Input!",
                font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
                text_color="red",
                cursor="arrow",
            )
            return

        if (
            not self.schedule_handler.is_within_date_range(start_date)
            and not self.schedule_handler.is_within_date_range(end_date)
            and not self.schedule_handler.is_preaching_schedule_within_date_range(
                start_date, end_date
            )
        ):
            self.reset_output_labels()
            self.app.confirmation_label.configure(
                text="No preaching schedule available within specified dates!",
                font=(self.app.STANDARD_FONT, self.app.CONFIRMATION_LABEL_FONT_SIZE),
                text_color="red",
                cursor="arrow",
            )
            return

        start_date, end_date, is_adjusted = (
            self.schedule_handler.adjust_dates_within_range(
                start_date=start_date, end_date=end_date
            )
        )
        if is_adjusted:
            message = f"Preaching schedule is only available from {str(start_date)} to {str(end_date)}."
            messagebox.showinfo("Alert", message)
            self.app.logger.warning(message)

        try:
            self.app.create_schedule(start_date=start_date, end_date=end_date)

            self.reset_output_labels()
            self.app.confirmation_label.bind(
                "<Button-1>",
                lambda e: self.handle_open_schedule_file(
                    e,
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

            self.app.output_link_label.bind(
                "<Button-1>",
                lambda e: self.handle_open_schedule_file(
                    e, self.app.output_link_label, SCHEDULE_DETAILS_HTML_FILE_PATH
                ),
            )
            self.app.output_link_label.configure(text="View Schedule Details")
        except PermissionError:
            self.handle_schedule_creation_exception(
                message="Please close any open\noutput files and try again."
            )
        except Exception:
            self.handle_schedule_creation_exception(
                message="An unexpected error occurred."
            )

    def reset_output_labels(self) -> None:
        """
        Resets the confirmation and output labels in the UI.

        This method clears any existing text or bindings on the labels.
        """
        self.app.confirmation_label.unbind("<Button-1>")
        self.app.output_link_label.unbind("<Button-1>")
        self.app.output_link_label.configure(text="", text_color="#4682B4")

    def handle_schedule_creation_exception(self, message: str) -> None:
        """
        Handles exceptions that occur during schedule creation.

        Logs the error, resets the output labels, and updates the UI with an error message.

        Args:
            message (str): The error message to display on the confirmation label.
        """
        self.app.logger.error(traceback.format_exc())
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
                e, self.app.output_link_label, LOG_FILE_PATH
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
