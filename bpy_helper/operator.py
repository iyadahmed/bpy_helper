import traceback
from typing import Callable, Optional, Set

import bpy


class MultiStateModal(bpy.types.Operator):
    _modal_handler: Callable[[bpy.types.Context, bpy.types.Event], Set[str]] = None

    def setup(self, context) -> None:
        ...

    def cleanup(self, context) -> None:
        ...

    def pre_modal_handler(self, context, event) -> Optional[Set[str]]:
        """an event handler that is executed before modal handler,
        if it returns {"RUNNING_MODAL"}, then _modal_handler will be executed after"""
        return {"RUNNING_MODAL"}

    def set_modal_handler(self, modal_handler: Callable[[bpy.types.Context, bpy.types.Event], Set[str]]):
        self._modal_handler = modal_handler

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        self.setup(context)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        try:
            if context.area is not None:
                # Area can be sometimes None
                context.area.tag_redraw()
            retval = self.pre_modal_handler(context, event)
            if retval == {"RUNNING_MODAL"}:
                if self._modal_handler:
                    retval = self._modal_handler(context, event)

            if retval in ({"FINISHED"}, {"CANCELLED"}):
                self.cleanup(context)

            return retval
        except Exception:
            self.report({"ERROR"}, traceback.format_exc())
            self.cleanup(context)
            return {"FINISHED"}


NUM_EVENT_TO_STR = {
    "ZERO": "0",
    "ONE": "1",
    "TWO": "2",
    "THREE": "3",
    "FOUR": "4",
    "FIVE": "5",
    "SIX": "6",
    "SEVEN": "7",
    "EIGHT": "8",
    "NINE": "9",
    "NUMPAD_0": "0",
    "NUMPAD_1": "1",
    "NUMPAD_2": "2",
    "NUMPAD_3": "3",
    "NUMPAD_4": "4",
    "NUMPAD_5": "5",
    "NUMPAD_6": "6",
    "NUMPAD_7": "7",
    "NUMPAD_8": "8",
    "NUMPAD_9": "9",
}


def modal_update_float_input_string_unsigned(op: bpy.types.Operator, event: bpy.types.Event, string_property_name: str):
    assert hasattr(op, string_property_name)
    old_str = getattr(op, string_property_name)
    new_str = old_str
    if (event.type in NUM_EVENT_TO_STR.keys()) and (event.value == "PRESS"):
        new_str = old_str + NUM_EVENT_TO_STR[event.type]

    elif (event.type in ("PERIOD", "NUMPAD_PERIOD")) and (event.value == "PRESS") and ("." not in old_str):
        new_str = old_str + "."

    elif (event.type == "BACK_SPACE") and (event.value == "PRESS") and (len(old_str) > 0):
        new_str = old_str[:-1]

    setattr(op, string_property_name, new_str)
    try:
        return float(new_str)
    except Exception:
        setattr(op, string_property_name, "")
        return None
