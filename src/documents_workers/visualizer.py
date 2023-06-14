from lxml import etree

RED_COLOR = "FF0000"
YELLOW_COLOR = "FFFF33"
GREEN_COLOR = "00FF00"


class DocumentVisualizer:
    def __init__(self, delta: str, ooxml: str) -> None:
        self.delta = delta
        self.delta_tree = etree.fromstring(self.delta)
        self.ooxml = ooxml
        self.ooxml_tree = etree.fromstring(self.ooxml)

    def to_view(self):
        for action in self.delta_tree.iterchildren():
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

    def __get_or_create_tag(self, root, xpath):
        element = root.xpath(xpath)
        if not element:
            element = etree.SubElement(root, xpath)
        return element[0] if isinstance(element, list) else element

    def _deleteNode_to_view(self, action):
        path = action.get("path")
        node = self.ooxml_tree.xpath(path)[0]
        self.set_element_color(node, RED_COLOR)

    def _insertNode_to_view(self, action):
        target = self.ooxml_tree.xpath(action.get("path"))[0]
        node = target.makeelement(action.find("newValue").text)
        target.insert(int(action.get("position")), node)
        self.set_element_color(target, GREEN_COLOR)

    def _renameNode_to_view(self, action):
        self.ooxml_tree.xpath(action.get("path"))[0].tag = action.find("newValue").text

    def _moveNode_to_view(self, action):
        node = self.ooxml_tree.xpath(action.get("path"))[0]
        self.set_element_color(node, RED_COLOR)
        target = self.ooxml_tree.xpath(action.get("target"))[0]
        target.insert(action.get("position"), node)
        self.set_element_color(target, GREEN_COLOR)

    def _updateTextIn_to_view(self, action):
        node = self.ooxml_tree.xpath(action.get("path"))[0]
        node.text = action.find("newValue").text
        self.set_element_color(node, YELLOW_COLOR)

    def _updateTextAfter_to_view(self, action):
        node = self.ooxml_tree.xpath(action.get("path"))[0]
        node.tail = action.find("newValue").text
        self.set_element_color(node, YELLOW_COLOR)

    def _updateAttrib_to_view(self, action):
        node = self.ooxml_tree.xpath(action.get("path"))[0]
        old_attr = action.find("oldValue").attrib.items()
        new_attr = action.find("newValue").attrib.items()
        if old_attr:
            del node.attrib[old_attr[0][0]]
        if new_attr:
            node.attrib[new_attr[0][0]] = new_attr[0][1]

        self.set_element_color(node, YELLOW_COLOR)

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
