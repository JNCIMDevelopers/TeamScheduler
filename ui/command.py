# Standard Library Imports
import logging

# Third-Party Imports
from tkinter import ttk

# Local Imports
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role


class EditAssignmentCommand:
    def __init__(
        self,
        event: Event,
        role: Role,
        old_person: Person,
        new_person: Person,
        tree: ttk.Treeview,
        row_id: str,
        column_index: int,
        logger: logging.Logger,
    ):
        self.event = event
        self.role = role
        self.old_person = old_person
        self.new_person = new_person
        self.tree = tree
        self.row_id = row_id
        self.column_index = column_index
        self.logger = logger
        self.logger.debug(
            f"EditAssignmentClass initialized with event: {event}, role: {role}, "
            f"old_person: {old_person}, new_person: {new_person}, "
            f"tree: {tree}, row_id: {row_id}, column_index: {column_index}"
        )

    def execute(self) -> None:
        if self.old_person:
            self.event.unassign_role(role=self.role, person=self.old_person)
            self.logger.info(
                f"Unassigned {self.old_person.name} from role {self.role} on {self.event.date}"
            )
        if self.new_person:
            self.event.assign_role(role=self.role, person=self.new_person)
            self.logger.info(
                f"Assigned {self.new_person.name} to role {self.role} on {self.event.date}"
            )
        self.update_treeview(name=self.new_person.name if self.new_person else "")

    def undo(self) -> None:
        if self.new_person:
            self.event.unassign_role(role=self.role, person=self.new_person)
            self.logger.info(
                f"Unassigned {self.new_person.name} from role {self.role} on {self.event.date}"
            )
        if self.old_person:
            self.event.assign_role(role=self.role, person=self.old_person)
            self.logger.info(
                f"Assigned {self.old_person.name} to role {self.role} on {self.event.date}"
            )
        self.update_treeview(name=self.old_person.name if self.old_person else "")

    def update_treeview(self, name: str) -> None:
        values = list(self.tree.item(self.row_id, "values"))
        values[self.column_index] = name
        self.tree.item(self.row_id, values=values)
