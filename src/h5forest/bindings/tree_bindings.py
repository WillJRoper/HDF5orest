"""A module containing the keybindings for the file tree.

This module contains the keybinding functions for the file tree. The functions
in this module should not be called directly, but are intended to be used by
the application.
"""
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer
from prompt_toolkit.widgets import Label


def _init_tree_bindings(app):
    """
    Set up the keybindings for the basic UI.

    These are always active and are not dependent on any leader key.
    """

    @app.error_handler
    def move_up_ten(event):
        """Move up ten lines."""
        # Get the current position
        pos = app.current_position

        # Move up 10 lines
        for row in range(app.current_row - 1, app.current_row - 11, -1):
            # Compute the position at this row
            pos -= len(app.tree.tree_text_split[row]) + 1

            if pos < 0:
                pos = 0
                break

        # Move the cursor
        app.set_cursor_position(app.tree.tree_text, pos)

    @app.error_handler
    def move_down_ten(event):
        """Move down ten lines."""
        # Get the current position
        pos = app.current_position

        # Move down 10 lines
        for row in range(app.current_row, app.current_row + 10):
            # Compute the position at this row
            pos += len(app.tree.tree_text_split[row]) + 1

            if row + 1 > app.tree.height - 1:
                pos = app.tree.length - len(
                    app.tree.tree_text_split[app.tree.height - 1]
                )
                break

        # Ensure we don't overshoot
        if pos > app.tree.length:
            pos = app.tree.length - len(
                app.tree.tree_text_split[app.tree.height - 1]
            )

        # Move the cursor
        app.set_cursor_position(app.tree.tree_text, pos)

    @app.error_handler
    def expand_collapse_node(event):
        """
        Expand the node under the cursor.

        This uses lazy loading so only the group at the expansion point
        will be loaded.
        """
        # Get the current cursor row and position
        current_row = app.current_row
        current_pos = app.current_position

        # Get the node under the cursor
        node = app.tree.get_current_node(current_row)

        # If we have a dataset just do nothing
        if node.is_dataset:
            app.print(f"{node.path} is not a Group")
            return

        # If the node has no children, do nothing
        if not node.has_children:
            app.print(f"{node.path} has no children")
            return

        # If the node is already open, close it
        if node.is_expanded:
            app.tree.close_node(node, current_row, app.tree_content)
        else:  # Otherwise, open it
            app.tree.update_tree_text(node, current_row, app.tree_content)

        # Reset the cursor position post update
        app.set_cursor_position(app.tree.tree_text, new_cursor_pos=current_pos)

    # Bind the functions
    app.kb.add(
        "{",
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(move_up_ten)
    app.kb.add(
        "}",
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(move_down_ten)
    app.kb.add(
        "enter",
        filter=Condition(lambda: app.app.layout.has_focus(app.tree_content)),
    )(expand_collapse_node)

    # Add hot keys
    hot_keys = [
        ConditionalContainer(
            Label("Enter → Open Group"),
            filter=Condition(
                lambda: app.app.layout.has_focus(app.tree_content)
            ),
        ),
        ConditionalContainer(
            Label("{ → Move Up 10 Lines"),
            filter=Condition(
                lambda: app.app.layout.has_focus(app.tree_content)
            ),
        ),
        ConditionalContainer(
            Label("} → Move Down 10 Lines"),
            filter=Condition(
                lambda: app.app.layout.has_focus(app.tree_content)
            ),
        ),
    ]

    return hot_keys
