from typing import Self
from ndf_parse import Mod
from ndf_parse.model import List
import Utils as utl

class NdfFileSet(object):
    def __init__(self: Self, mod: Mod, parent_msg: utl.Message, base_path: str = "", *paths: str):
        self.mod = mod
        self.parent_msg = parent_msg
        self.paths = utl.ndf.root_paths(base_path, paths)
        self.loaded_files: dict[str, List] = {}
       
    def __enter__(self: Self):
        self.msg = self.parent_msg.nest("Loading ndf files", child_padding=self.msg_length)
        self.msg.__enter__()
        for path in self.paths:
            yield self.mod.edit(path).current_tree
    
    def __exit__(self: Self, exc_type, exc_value, traceback):
        with self.msg.nest("Writing edits", child_padding=self.msg_length) as write_msg:
            for edit in self.mod.edits:
                with write_msg.nest(f"Writing {edit.file_path}") as _:
                    self.mod.write_edit(edit)
        self.msg.__exit__(self, exc_type, exc_value, traceback)
        self.loaded_files = {}

    @property
    def msg_length(self: Self):
        return max([len(x) for x in self.paths]) + len("Editing ")