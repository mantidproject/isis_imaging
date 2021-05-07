Dynamic Registering
===================

The Command Line Interface (CLI) and the Graphical User Interface (GUI) are both
built at runtime.

Common module for Registering
-----------------------------

The work for the registering is done in a common module -
:code:`algorithms.registrator`. The :code:`registrator.py` file provides the
generic functions are used for each interface. In order for the functions to be
generic they take an object in which to register (for CLI it will be an
:code:`ArgumentParser`, for GUI it will be the :code:`QMainWindow`), referred to
as :code:`the_object` in the file.

The :code:`register_into` function will only do some sanity checks and then loops over
the files in the directory/package that's been provided. Then it will call the
:code:`func` parameter, which will be a different function depending on whether
we are registering into the CLI or the GUI, and will forward :code:`the_object`
into which we're registering and the module directory. It will not do any
importing.

At this point the :code:`func` parameter function is executed and it will go to
function that's been provided. Currently only CLI and GUI are available, and
that may change, but the following text will assume it only has one of those
two.

When the :code:`func` parameter is executed we go into either
:code:`cli_registrator.py` or :code:`gui_registrator.py` and execute the
:code:`xxx_register` function that will assert the state of the program - that
we have the correct object. It will them proceed to call the importing function
from the generic :code:`registrator` module which will try the importing and the
extended importing (looks for a module with _cli or _gui appended to the name),
and, if it succeeds importing either the normal or extended, it will execute the
:code:`func_to_do_registering` function, which will either be from the
:code:`cli` or the :code:`gui` module, depending on the caller.

If not found a warning will be shown to the user that the package was not found.

Command Line Interface (CLI)
----------------------------

The registering here is simply to add the flags to the :code:`ArgumentParser`.
It will add a new group for each filter.

Graphical User Interface (GUI)
------------------------------

The registering here is a bit more complicated, we call the module that contains
the :code:`_gui_register` function, and that function will build the dialog's
visuals. Afterwards we assert that the function has returned the correct class
and has set an execute function. Then we create a :code:`QAction` that either uses the
module's name as it's name, or a special constant :code:`GUI_MENU_NAME`. The name here
will be the one that shows in the drop down menu in the GUI.

The :code:`QAction` is then set up to show the dialog when it's triggered (clicked by
the user), and the action is added to the menu.
