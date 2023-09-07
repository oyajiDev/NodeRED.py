# -*- coding: utf-8 -*-
import htmlgenerator as hg
from typing import List, Any
from .property import Property
from ...red.editor.widget import Widget, RenderedWidget


class ComboBoxProperty(Property, Widget):
    def __init__(self, name:str, items:List[Any], default:Any = None, required:bool = False, display_name:str = None, display_icon:str = None, one_line:bool = False):
        """
        Property to select value from lists

        name: str, required
            name of ComboBoxProperty
        items: List[Any], required
            items of ComboBoxProperty
        default: Any, default None
            default value of ComboBoxProperty
        required: bool, default False
            set required or not
        display_name: str, default None
            name to display in Node-RED edit dialog
        display_icon: str, default None
            icon to display in Node-RED edit dialog (for available icons, see https://fontawesome.com/v4/icons/)
        """
        if not isinstance(items, list):
            raise TypeError("items of ComboBoxProperty must be type: 'list'")
        
        if default is None:
            if len(items) > 0:
                default = items[0]
            else:
                default = ""
        
        Property.__init__(self, name, default, required, display_name, display_icon if display_icon else "fa fa-filter")
        Widget.__init__(self)
        self.items = items
        self.one_line = one_line

    def render(self) -> RenderedWidget:
        rendered = RenderedWidget(
            props = { self.var_name: { "value": self.default, "required": self.required } },
            props_map = { self.name: self.name }
        )

        if self.one_line:
            rendered.elements.append(
                hg.DIV(
                    hg.LABEL(
                        hg.I(_class = self.display_icon, style = "margin-right:5px;"),
                        hg.SPAN(self.display_name),
                        style = "display:flex;align-items:center;"
                    ),
                    hg.SELECT(
                        *[
                            hg.OPTION(
                                str(item),
                                value = str(item)
                            )
                            for item in self.items
                        ],
                        id = f"node-input-{self.var_name}-select",
                        style = "margin-left:10px;flex:1;"
                    ),
                    hg.INPUT(
                        id = f"node-input-{self.var_name}",
                        type = "text",
                        style = "display:none;"
                    ),
                    _class = "form-row",
                    style = "display:flex;flex-flow:row;"
                )
            )
        else:
            rendered.elements.extend([
                hg.DIV(
                    hg.LABEL(
                        hg.I(_class = self.display_icon), " ",
                        hg.SPAN(self.display_name)
                    ),
                    _class = "form-row",
                    style = "margin-bottom: 0px;"
                ),
                hg.DIV(
                    hg.SELECT(
                        *[
                            hg.OPTION(
                                str(item),
                                value = str(item)
                            )
                            for item in self.items
                        ],
                        id = f"node-input-{self.var_name}-select",
                        style = "width:100%;"
                    ),
                    hg.INPUT(
                        id = f"node-input-{self.var_name}",
                        type = "text",
                        style = "display:none;"
                    ),
                    _class = "form-row"
                )
            ])

        rendered.prepare = f"""
            $('#node-input-{self.var_name}-select').val($('#node-input-{self.var_name}').val());"""
        rendered.save = f"""
            $('#node-input-{self.var_name}').val($('#node-input-{self.var_name}-select').val());"""

        return rendered
