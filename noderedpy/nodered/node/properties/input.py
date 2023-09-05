# -*- coding: utf-8 -*-
import htmlgenerator as hg
from typing import Union
from .property import Property
from ...red.editor.widget import Widget, RenderedWidget


class InputProperty(Property, Widget):
    def __init__(self, name:str, default:Union[int, float, str] = None, required:bool = False, display_name:str = None, display_icon:str = None, one_line:bool = False):
        """
        Property to change value

        name: str, required
            name of InputProperty
        default: Union[int, float, str], default ""
            default value of InputProperty
        required: bool, default False
            set required or not
        display_name: str, default None
            name to display in Node-RED edit dialog
        display_icon: str, default None
            icon to display in Node-RED edit dialog (for available icons, see https://fontawesome.com/v4/icons/)
        """
        if default is None:
            if isinstance(default, int):
                default = 0
            elif isinstance(default, float):
                default = 0.0
            else:
                default = ""
        elif not isinstance(default, (int, float, str)):
            raise TypeError("InputProperty can accept types: [ 'int', 'float', 'str' ]")

        Property.__init__(self, name, default, required, display_name)
        Widget.__init__(self)

        if display_icon is None:
            if isinstance(default, (int, float)):
                self.display_icon = "fa fa-sort-numeric-asc"
            else:
                self.display_icon = "fa fa-font"
        else:
            self.display_icon = display_icon

        self.one_line = one_line

    def render(self) -> RenderedWidget:
        rendered = RenderedWidget(
            props = { self.var_name: { "value": self.default } },
            props_map = { self.name: self.name },
            html = "",
            prepare = "", cancel = "", save = ""
        )
        if self.one_line:
            rendered.html = hg.render(
                hg.DIV(
                    hg.LABEL(
                        hg.I(_class = self.display_icon, style = "margin-right:5px;"),
                        hg.SPAN(self.display_name),
                        style = "display:flex;align-items:center;"
                    ),
                    hg.INPUT(
                        id = f"node-input-{self.var_name}",
                        type = "text",
                        style = "margin-left:10px;flex:1;"
                    ),
                    _class = "form-row",
                    style = "display:flex;flex-flow:row;"
                ), {}
            )
        else:
            rendered.html = hg.render(
                hg.DIV(
                    hg.LABEL(
                        hg.I(_class = self.display_icon), " ",
                        hg.SPAN(self.display_name)
                    ),
                    _class = "form-row",
                    style = "margin-bottom: 0px;"
                ), {}
            ) + hg.render(
                hg.DIV(
                    hg.INPUT(
                        id = f"node-input-{self.var_name}",
                        type = "text",
                        style = "width: 100%;"
                    ),
                    _class = "form-row"
                ), {}
            )

        return rendered