from copy import deepcopy
from typing import List

from lxml import etree
from xmldiff import actions, main


def get_tag_name(xpath_expr):
    parts = xpath_expr.strip("/").split("/")
    tag_name = parts[-1].split("[")[0]
    return tag_name


class XMLDiffToDeltaConverter:
    def __init__(self, ooxml: str, diffs: List) -> None:
        self.ooxml = ooxml
        self.ooxml_etree = etree.fromstring(ooxml)
        self.edited_ooxml_tree = self.ooxml_etree
        self.diffs = diffs
        self.delta = etree.Element("delta")
        self.CONVERT_MAPPING = {
            actions.DeleteNode: self._convert_DeleteNode,
            actions.InsertNode: self._convert_InsertNode,
            actions.RenameNode: self._convert_RenameNode,
            actions.MoveNode: self._convert_MoveNode,
            actions.UpdateTextIn: self._convert_UpdateTextIn,
            actions.UpdateTextAfter: self._convert_UpdateTextAfter,
            actions.UpdateAttrib: self._convert_UpdateAttrib,
            actions.DeleteAttrib: self._convert_DeleteAttrib,
            actions.InsertAttrib: self._convert_InsertAttrib,
            actions.RenameAttrib: self._convert_RenameAttrib,
        }

    def convert(self):
        for diff in self.diffs:
            method = getattr(self, f"_convert_{type(diff).__name__}", None)
            if method:
                method(diff)
                self.edited_ooxml_tree = main.patch_tree([diff], self.edited_ooxml_tree)
        return etree.tostring(self.delta)

    def _convert_DeleteNode(self, diff: actions.DeleteNode):
        delete = etree.SubElement(self.delta, "deleteNode")
        delete.set("path", diff.node)
        new_value = etree.SubElement(delete, "newValue")
        old_value = etree.SubElement(delete, "oldValue")
        old_value.append(deepcopy(self.edited_ooxml_tree.xpath(diff.node)[0]))

    def _convert_InsertNode(self, diff: actions.InsertNode):
        insert = etree.SubElement(self.delta, "insertNode")
        insert.set("path", diff.target)
        insert.set("position", str(diff.position))
        old_value = etree.SubElement(insert, "oldValue")
        new_value = etree.SubElement(insert, "newValue")
        new_value.text = diff.tag

    def _convert_RenameNode(self, diff: actions.RenameNode):
        rename_node = etree.SubElement(self.delta, "renameNode")
        rename_node.set("path", diff.node)
        old_value = etree.SubElement(rename_node, "oldValue")
        new_value = etree.SubElement(rename_node, "newValue")
        old_value.text = get_tag_name(diff.node)
        new_value.text = diff.tag

    def _convert_MoveNode(self, diff: actions.MoveNode):
        move_node = etree.SubElement(self.delta, "moveNode")
        move_node.set("path", diff.node)
        move_node.set("target_path", diff.target)
        move_node.set("position", str(diff.position))
        old_value = etree.SubElement(move_node, "oldValue")
        new_value = etree.SubElement(move_node, "newValue")
        node = deepcopy(self.edited_ooxml_tree.xpath(diff.node)[0])
        old_value.append(node)
        new_value.append(node)

    def _convert_UpdateTextIn(self, diff: actions.UpdateTextIn):
        update_text_in = etree.SubElement(self.delta, "updateTextIn")
        update_text_in.set("path", diff.node)
        old_value = etree.SubElement(update_text_in, "oldValue")
        new_value = etree.SubElement(update_text_in, "newValue")
        old_value.text = deepcopy(self.edited_ooxml_tree.xpath(diff.node)[0].text)
        new_value.text = diff.text

    def _convert_UpdateTextAfter(self, diff: actions.UpdateTextAfter):
        update_text_after = etree.SubElement(self.delta, "updateTextAfter")
        update_text_after.set("path", diff.node)
        old_value = etree.SubElement(update_text_after, "oldValue")
        new_value = etree.SubElement(update_text_after, "newValue")
        old_value.text = deepcopy(self.edited_ooxml_tree.xpath(diff.node)[0].tail) or ""
        new_value.text = diff.text

    def _convert_UpdateAttrib(self, diff: actions.UpdateAttrib):
        update_attrib = etree.SubElement(self.delta, "updateAttrib")
        update_attrib.set("path", diff.node)
        old_value = etree.SubElement(update_attrib, "oldValue")
        new_value = etree.SubElement(update_attrib, "newValue")
        old_value.set(diff.name, deepcopy(self.edited_ooxml_tree.xpath(diff.node)[0].get(diff.name)))
        new_value.set(diff.name, diff.value)

    def _convert_DeleteAttrib(self, diff: actions.DeleteAttrib):
        update_attrib = etree.SubElement(self.delta, "updateAttrib")
        update_attrib.set("path", diff.node)
        old_value = etree.SubElement(update_attrib, "oldValue")
        new_value = etree.SubElement(update_attrib, "newValue")
        old_value.set(diff.name, deepcopy(self.edited_ooxml_tree.xpath(diff.node)[0].get(diff.name)) or "")

    def _convert_InsertAttrib(self, diff: actions.InsertAttrib):
        update_attrib = etree.SubElement(self.delta, "updateAttrib")
        update_attrib.set("path", diff.node)
        old_value = etree.SubElement(update_attrib, "oldValue")
        new_value = etree.SubElement(update_attrib, "newValue")
        new_value.set(diff.name, diff.value)

    def _convert_RenameAttrib(self, diff: actions.RenameAttrib):
        update_attrib = etree.SubElement(self.delta, "updateAttrib")
        update_attrib.set("path", diff.node)
        old_value = etree.SubElement(update_attrib, "oldValue")
        new_value = etree.SubElement(update_attrib, "newValue")
        value = deepcopy(self.edited_ooxml_tree.xpath(diff.node)[0].get(diff.oldname))
        old_value.set(diff.oldname, value)
        new_value.set(diff.newname, value)


if __name__ == "__main__":
    left = "<document attr1='1' attr2='2' attr3='3'><node>Content</node></document>"
    right = "<document attr1='2' attr4='4'><k>Content New </k><newnode>Ler<n>Test</n>Kert</newnode></document>"
    # right = "<document><node>Content</node><p><p></p></p></document>"
    # left = "<document><node>Content</node><movenode>ABC<n>fd</n></movenode></document>"
    # right = "<document><movenode>ABC<n>fd</n></movenode><node>Content</node></document>"
    diff = main.diff_texts(
        left,
        right,
        diff_options={
            "ratio_mode": "accurate",
        },
    )
    print(diff)
    print(etree.tostring(XMLDiffToDeltaConverter(left, diff).convert()))
