import traceback
from typing import Callable, Optional, Protocol, Set, Union

import bpy


class BaseMultiStateModal(Protocol):
    _modal_handler: Callable[[bpy.types.Context, bpy.types.Event], Set[str]]

    def setup(self, context) -> None:
        ...

    def cleanup(self, context) -> None:
        ...

    def pre_modal_handler(self, context, event) -> Optional[Set[str]]:
        # an event handler gets executed before modal handler
        # if it returns {"RUNNING_MODAL"}, then _modal_handler will be executed after
        ...

    def set_modal_handler(self, modal_handler: Callable[[bpy.types.Context, bpy.types.Event], Set[str]]):
        self._modal_handler = modal_handler

    def invoke(self, context, event):
        self.setup(context)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(
        self: Union[bpy.types.Operator, "BaseMultiStateModal"],
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        try:
            context.area.tag_redraw()
            retval = self.pre_modal_handler(context, event)
            if retval == {"RUNNING_MODAL"}:
                retval = self._modal_handler(context, event)

            if retval in ({"FINISHED"}, {"CANCELLED"}):
                self.cleanup(context)

            return retval
        except Exception:
            self.report({"ERROR"}, traceback.format_exc())
            self.cleanup(context)
            return {"FINISHED"}
