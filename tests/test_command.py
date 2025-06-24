import pytest
from unittest.mock import MagicMock
from ui.command import EditAssignmentCommand


@pytest.fixture
def mock_event():
    event = MagicMock()
    event.date = "2025-05-18"
    event.unassign_role = MagicMock()
    event.assign_role = MagicMock()
    return event


@pytest.fixture
def mock_person1():
    person = MagicMock()
    person.name = "TestPerson1"
    return person


@pytest.fixture
def mock_person2():
    person = MagicMock()
    person.name = "TestPerson2"
    return person


@pytest.fixture
def mock_sheet():
    sheet = MagicMock()
    return sheet


@pytest.fixture
def mock_logger():
    return MagicMock()


def test_execute_assigns_and_unassigns(
    mock_event, mock_person1, mock_person2, mock_sheet, mock_logger
):
    # Arrange
    role = "TestRole"
    cmd = EditAssignmentCommand(
        event=mock_event,
        role=role,
        old_person=mock_person1,
        new_person=mock_person2,
        sheet=mock_sheet,
        row=1,
        column=1,
        logger=mock_logger,
    )
    cmd.update_sheet = MagicMock()

    # Act
    cmd.execute()

    # Assert
    mock_event.unassign_role.assert_called_with(role=role, person=mock_person1)
    mock_event.assign_role.assert_called_with(role=role, person=mock_person2)
    cmd.update_sheet.assert_called()


def test_execute_with_no_old_person_only_assigns(
    mock_event, mock_person2, mock_sheet, mock_logger
):
    # Arrange
    role = "TestRole"
    cmd = EditAssignmentCommand(
        event=mock_event,
        role=role,
        old_person=None,
        new_person=mock_person2,
        sheet=mock_sheet,
        row=1,
        column=1,
        logger=mock_logger,
    )
    cmd.update_sheet = MagicMock()

    # Act
    cmd.execute()

    # Assert
    mock_event.unassign_role.assert_not_called()
    mock_event.assign_role.assert_called_with(role=role, person=mock_person2)
    cmd.update_sheet.assert_called()


def test_execute_with_no_new_person_only_unassigns(
    mock_event, mock_person1, mock_sheet, mock_logger
):
    # Arrange
    role = "TestRole"
    cmd = EditAssignmentCommand(
        event=mock_event,
        role=role,
        old_person=mock_person1,
        new_person=None,
        sheet=mock_sheet,
        row=1,
        column=1,
        logger=mock_logger,
    )
    cmd.update_sheet = MagicMock()

    # Act
    cmd.execute()

    # Assert
    mock_event.unassign_role.assert_called_with(role=role, person=mock_person1)
    mock_event.assign_role.assert_not_called()
    cmd.update_sheet.assert_called()


def test_undo_reverts_assignment(
    mock_event, mock_person1, mock_person2, mock_sheet, mock_logger
):
    # Arrange
    role = "TestRole"
    cmd = EditAssignmentCommand(
        event=mock_event,
        role=role,
        old_person=mock_person1,
        new_person=mock_person2,
        sheet=mock_sheet,
        row=1,
        column=1,
        logger=mock_logger,
    )
    cmd.update_sheet = MagicMock()

    # Act
    cmd.undo()

    # Assert
    mock_event.unassign_role.assert_called_with(role=role, person=mock_person2)
    mock_event.assign_role.assert_called_with(role=role, person=mock_person1)
    cmd.update_sheet.assert_called()


def test_undo_with_no_old_person_only_unassigns(
    mock_event, mock_person1, mock_sheet, mock_logger
):
    # Arrange
    role = "TestRole"
    cmd = EditAssignmentCommand(
        event=mock_event,
        role=role,
        old_person=None,
        new_person=mock_person1,
        sheet=mock_sheet,
        row=1,
        column=1,
        logger=mock_logger,
    )
    cmd.update_sheet = MagicMock()

    # Act
    cmd.undo()

    # Assert
    mock_event.unassign_role.assert_called_with(role=role, person=mock_person1)
    mock_event.assign_role.assert_not_called()
    cmd.update_sheet.assert_called()


def test_undo_with_no_new_person_only_assigns(
    mock_event, mock_person1, mock_sheet, mock_logger
):
    # Arrange
    role = "TestRole"
    cmd = EditAssignmentCommand(
        event=mock_event,
        role=role,
        old_person=mock_person1,
        new_person=None,
        sheet=mock_sheet,
        row=1,
        column=1,
        logger=mock_logger,
    )
    cmd.update_sheet = MagicMock()

    # Act
    cmd.undo()

    # Assert
    mock_event.unassign_role.assert_not_called()
    mock_event.assign_role.assert_called_with(role=role, person=mock_person1)
    cmd.update_sheet.assert_called()
