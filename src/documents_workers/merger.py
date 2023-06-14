from lxml import etree

PURPLE_COLOR = "006633"
GREEN_COLOR = "7F00FF"


class Merger:
    def __init__(self, left_delta: str, right_delta: str, ooxml: str, new_ooxml: str):
        self.left_delta = etree.fromstring(left_delta)
        self.left_delta_tree = etree.fromstring(left_delta)
        self.right_delta = right_delta
        self.right_delta_tree = etree.fromstring(right_delta)
        self.ooxml_tree = etree.fromstring(ooxml)
        self.new_ooxml_tree = etree.fromstring(new_ooxml)

        self.merge_delta_tree = etree.ElementTree("delta")

    def merge(self):
        self.conflict_xpaths = []
        for action in self.right_delta_tree.iterchildren():
            path = action.get("path")

            if "/".join(path.rsplit("/", 2)[:-1]) in self.conflict_xpaths:
                continue

            conflict_path = self.is_has_conflict_path(path)
            if conflict_path:
                self.add_conflict_to_delta(conflict_path)
            else:
                self.merge_delta_tree.append(action)
        return self.to_view()

    def is_has_conflict_path(self, path):
        for action in self.left_delta_tree.iterchildren():
            if "path" in action.attrib:
                action_path = action.attrib["path"]
                if action.attrib["path"] == path:
                    self.conflict_xpaths.append(path)
                    return action

                path = path.split("/").get(2, None)
                if path.split("/").get(2, None) == action_path.split("/")(2, None):
                    self.conflict_xpaths.append(path)
                    return path

    def add_conflict_to_delta(self, path):
        conflict = etree.SubElement("conflict")
        conflict.text = path

    def to_view(self):
        for action in self.merge_delta_tree.iterchildren():
            method = getattr(self, f"_{action.tag}_to_view", None)
            if method:
                try:
                    method(action)
                except BaseException as e:
                    continue
        return etree.tostring(self.ooxml_tree)

    def set_element_color(self, element, color):
        if element.tag == "w:p":
            self.set_paragraph_color(element, color)
        elif element.tag == "w:sectPr":
            self.set_section_color(element, color)
        elif element.tag == "w:tc":
            self.set_cell_color(element, color)
        elif element.tag == "w:tr":
            self.set_row_color(element, color)
        elif element.tag == "w:tbl":
            self.set_table_color(element, color)
        elif element.tag == "w:col":
            self.set_column_color(element, color)

    def _deleteNode_to_view(self, action):
        path = action.get("path")
        node = self.ooxml_tree.xpath(path)[0]
        node.getparent().remove(node)

    def _insertNode_to_view(self, action):
        target = self.ooxml_tree.xpath(action.get("path"))[0]
        node = target.makeelement(action.find("newValue").text)
        target.insert(int(action.get("position")), node)

    def _renameNode_to_view(self, action):
        self.ooxml_tree.xpath(action.get("path"))[0].tag = action.find("newValue").text

    def _moveNode_to_view(self, action):
        node = self.ooxml_tree.xpath(action.get("path"))[0]
        node.getparent().remove(node)
        target = self.ooxml_tree.xpath(action.get("target"))[0]
        target.insert(action.get("position"), node)

    def _updateTextIn_to_view(self, action):
        self.ooxml_tree.xpath(action.get("path"))[0].text = action.find("newValue").text

    def _updateTextAfter_to_view(self, action):
        self.ooxml_tree.xpath(action.get("path"))[0].tail = action.find("newValue").text

    def _updateAttrib_to_view(self, action):
        node = self.ooxml_tree.xpath(action.get("path"))[0]
        old_attr = action.find("oldValue").attrib.items()
        new_attr = action.find("newValue").attrib.items()
        if old_attr:
            del node.attrib[old_attr[0][0]]
        if new_attr:
            node.attrib[new_attr[0][0]] = new_attr[0][1]

    def _conflict_to_view(self, action):
        node = self.ooxml_tree.xpath(action.text)
        target = self.new_ooxml_tree.xpath(action.text)
        self.set_element_color(node, PURPLE_COLOR)
        self.set_element_color(node, GREEN_COLOR)
        node.get_parent().insert(2, target)

    def set_paragraph_color(self, paragraph, color):
        rPr = paragraph.xpath(".//w:rPr")
        if not rPr:
            rPr = etree.SubElement(paragraph, "w:rPr")
        else:
            rPr = rPr[0]
        color_element = rPr.xpath(".//w:color")
        if not color_element:
            color_element = etree.SubElement(rPr, "w:color")
        else:
            color_element = color_element[0]
        color_element.attrib["w:val"] = color

    def set_section_color(self, section, color):
        sectPr = section.xpath(".//w:sectPr")
        if not sectPr:
            sectPr = etree.SubElement(section, "w:sectPr")
        else:
            sectPr = sectPr[0]
        background_element = sectPr.xpath(".//w:background")
        if not background_element:
            background_element = etree.SubElement(sectPr, "w:background")
        else:
            background_element = background_element[0]
        background_element.attrib["w:color"] = color

    def set_column_color(self, column, color):
        colPr = column.xpath(".//w:colPr")
        if not colPr:
            colPr = etree.SubElement(column, "w:colPr")
        else:
            colPr = colPr[0]
        shading_element = colPr.xpath(".//w:shd")
        if not shading_element:
            shading_element = etree.SubElement(colPr, "w:shd")
        else:
            shading_element = shading_element[0]
        shading_element.attrib["w:fill"] = color

    def set_table_color(self, table, color):
        tblPr = table.xpath(".//w:tblPr")
        if not tblPr:
            tblPr = etree.SubElement(table, "w:tblPr")
        else:
            tblPr = tblPr[0]
        tblStyle_element = tblPr.xpath(".//w:tblStyle")
        if not tblStyle_element:
            tblStyle_element = etree.SubElement(tblPr, "w:tblStyle")
        else:
            tblStyle_element = tblStyle_element[0]
        tblStyle_element.attrib["w:val"] = color

    def set_row_color(self, row, color):
        trPr = row.xpath(".//w:trPr")
        if not trPr:
            trPr = etree.SubElement(row, "w:trPr")
        else:
            trPr = trPr[0]
        shading_element = trPr.xpath(".//w:shd")
        if not shading_element:
            shading_element = etree.SubElement(trPr, "w:shd")
        else:
            shading_element = shading_element[0]
        shading_element.attrib["w:fill"] = color

    def set_cell_color(self, cell, color):
        tcPr = cell.xpath(".//w:tcPr")
        if not tcPr:
            tcPr = etree.SubElement(cell, "w:tcPr")
        else:
            tcPr = tcPr[0]
        shading_element = tcPr.xpath(".//w:shd")
        if not shading_element:
            shading_element = etree.SubElement(tcPr, "w:shd")
        else:
            shading_element = shading_element[0]
        shading_element.attrib["w:fill"] = color
