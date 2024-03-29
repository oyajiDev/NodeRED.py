# -*- coding: utf-8 -*-
import os, htmlgenerator as hg, gc, json, traceback
from types import MethodType
from typing import List
from threading import Thread
from ..red.editor.widget import Widget
from ..red.editor.editor import Editor
from .communicator import NodeCommunicator
from ...templates.package import package_json
from ...templates.html import node_html
from ...templates.javascript import node_js
from .. import __path__



class Node:
    def __init__(self, name:str, category:str, version:str, description:str, author:str, keywords:List[str], icon:str, color:str, widgets:List[Widget], node_func:MethodType):
        # name of node cannot contain spaces
        if " " in name.strip():
            raise NameError("Node name cannot contain spaces!")
        
        # category of node cannot contain - or ,
        if "-" in category.strip() or "," in category.strip():
            raise NameError("Category cannot contain '-' or ','!")
        
        # remove default keyword in extra keywords
        self.keywords = [
            keyword
            for keyword in keywords
            if not keyword in ( "node-red", )
        ]

        self.name, self.category, self.version, self.description, self.author, self.icon, self.color, self.editor =\
            name, category, version, description, author, icon, color, Editor(widgets)

        self.__node_func = node_func

    def create(self, node_red_user_dir:str, node_red_user_cache_dir:str):
        self.__communicator = NodeCommunicator(os.path.join(node_red_user_cache_dir, "node_message.json"), self.name)
        node_dir = os.path.join(node_red_user_dir, "node_modules", self.name if self.name.startswith("nodered-py-") else f"nodered-py-{self.name}")
        os.makedirs(os.path.join(node_dir, "lib"))

        # render editor
        rendered_editor = self.editor.render()
        self.__props_map = rendered_editor.props_map

        # write package.json
        with open(os.path.join(node_dir, "package.json"), "w", encoding = "utf-8") as pjw:
            pjw.write(package_json(self.name, self.version, self.description, self.author, self.keywords))

        # write html
        with open(os.path.join(node_dir, "lib", f"{self.name}.html"), "w", encoding = "utf-8") as nhw:
            nhw.write(node_html(
                self.name, self.icon, self.category, self.color,
                "\n".join([ hg.render(element, {}) for element in rendered_editor.elements ]),
                rendered_editor.props,
                rendered_editor.prepare, rendered_editor.cancel, rendered_editor.save
            ))

        # write javascript
        with open(os.path.join(node_dir, "lib", f"{self.name}.js"), "w", encoding = "utf-8") as njw:
            njw.write(node_js(self.name, [ name for name in rendered_editor.props.keys() if not name == "np-var_name" ], node_red_user_cache_dir))

    def __run(self, raw_props:dict, msg:dict, output_file:str):
        gc.enable()

        print(f"\n{self.name} started\n===================================")
        try:
            props = {}
            for name, map_info in self.__props_map.items():
                if not name == "name":
                    if isinstance(map_info, list):
                        props[name] = [
                            raw_props[var_name]
                            for var_name in map_info
                        ]
                    elif isinstance(map_info, dict):
                        props[name] = {
                            key: raw_props[var_name]
                            for key, var_name in map_info.items()
                        }
                    else:
                        props[name] = raw_props[map_info]

            resp = self.__node_func(self.__communicator, props, msg)
            del props
            print("============================= ended\n")

            resp.update({ "state": "success", "name": self.name })
            gc.collect()
        except:
            resp = { "state": "fail", "name": self.name, "message": traceback.format_exc() }

        try:
            with open(output_file, "w", encoding = "utf-8") as ofw:
                json.dump(resp, ofw, indent = 4)
        except:
            os.remove(output_file)
            resp["req"]["body"] = {}
            self.__write_node_output(output_file, resp)

    def run(self, raw_props:dict, msg:dict, output_file:str):
        Thread(target = self.__run, args = ( raw_props, msg, output_file ), daemon = True).start()
