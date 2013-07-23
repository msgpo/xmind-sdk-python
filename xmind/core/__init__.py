#!/usr/bin/env python

"""
    xmind.core
    ~~~~~~~~~~

    :copyright:
    :license:

"""

__author__ = "woody@xmind.net <Woody Ai>"


from xml.dom import minidom as DOM

from .. import utils


def create_document():
    """:cls: ``xml.dom.Document`` object constructor
    """
    return DOM.Document()


def create_element(tag_name, namespaceURI=None, prefix=None, localName=None):
    """:cls: ``xml.dom.Element`` object constructor
    """
    element = DOM.Element(tag_name, namespaceURI, prefix, localName)

#    if ":" in tag_name:
#        prefix, local_name = tag_name.split(":")
#    else:
#        local_name = tag_name.split(":")
#    element.prefix = prefix
#    element.localName = local_name

    return element


class Node(object):
    """All of components of XMind workbook are subclass of Node
    """
    def __init__(self, node):
        self._node = node

    def _equals(self, obj=None):
        """Compare passed object and current instance
        """
        if obj is None or not isinstance(obj, self.__class__):
            return False
        if obj == self:
            return True
        return self.getImplementation() == obj.getImplementation()

    def getImplementation(self):
        """Get DOM implementation of passed node. Provides a interface for
        manipulate DOM directly
        """
        return self._node

    def getOwnerDocument(self):
        raise Exception(
            """This is method doesn't implementated
            """)

    def setOwnerDocument(self, doc):
        raise Exception(
            """This is method doesn't implementated
            """)

    def getLocalName(self, qualifiedName):
        index = qualifiedName.find(":")
        if index >= 0:
            return qualifiedName[index + 1:]
        else:
            return qualifiedName

    def getPrefix(self, qualifiedName):
        index = qualifiedName.find(":")
        if index >= 0:
            return qualifiedName[:index + 1]

    def appendChild(self, node):
        """Append passed node to the end of child node list of this node
        """
        node.setOwnerDocument(self.getOwnerDocument())

        node_impel = node.getImplementation()

        return self._node.appendChild(node_impel)

    def insertBefore(self, new_node, ref_node):
        """Insert new node before ref_node. Please notice that ref_node
        must be a child of this node.
        """
        new_node.setOwnerDocument(self.getOwnerDocument())

        new_node_imple = new_node.getImplementation()
        ref_node_imple = ref_node.getImplementation()

        return self._node.insertBefore(new_node_imple, ref_node_imple)

    def getChildNodesByTagName(self, tag_name):
        """Search for all children with specified tag name under passed DOM
        implementation, instead of all descendants
        """
        child_nodes = []
        for node in self._node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue

            if node.tagName == tag_name:
                child_nodes.append(node)

        return child_nodes

    def getFirstChildNodeByTagName(self, tag_name):
        child_nodes = self.getChildNodesByTagName(tag_name)

        if len(child_nodes) >= 1:
            return child_nodes[0]

    def getParentNode(self):
        return self._node.parentNode

    def iterChildNodesByTagName(self, tag_name):
        for node in self._node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue

            if node.tagName == tag_name:
                yield node

    def removeChild(self, child_node):
        child_node = child_node.getImplementation()
        self._node.removeChild(child_node)

    def output(self, output_stream):
        return self._node.writexml(output_stream,
                                   addindent="",
                                   newl="",
                                   encoding="utf-8")


class Document(Node):
    def __init__(self, node=None):
        self._node = node or self._documentConstructor()
        # self.arg = arg

    def _documentConstructor(self):
        return DOM.Document()

    @property
    def documentElement(self):
        """Get root element of passed DOM implementation for manipulate
        """
        return self._node.documentElement

    def getOwnerDocument(self):
        return self._node

    def createElement(self, tag_name):
        return self._node.createElement(tag_name)

    def setVersion(self, version):
        element = self.documentElement
        if element and not element.hasAttribute("version"):
            element.setAttribute("version", version)

    def replaceVersion(self, version):
        element = self.documentElement
        if element:
            element.setAttribute("version", version)

    def getElementById(self, id):
        return self._node.getElementById(id)


class Element(Node):
    TAG_NAME = ""

    def __init__(self, node=None):
        tag_name = self.TAG_NAME.encode("utf8")
        self._node = node or self._elementConstructor(tag_name)

    def _elementConstructor(self, tag_name,
                            namespaceURI=None,
                            prefix=None, localName=None):
        element = DOM.Element(tag_name, namespaceURI, prefix, localName)

        prefix = self.getPrefix(tag_name)
        localName = self.getLocalName(tag_name)

        element.prefix = prefix
        element.localName = localName

        return element

    def getOwnerDocument(self):
        return self._node.ownerDocument

    def setOwnerDocument(self, doc_imple):
        self._node.ownerDocument = doc_imple

    def setAttributeNS(self, namespace, attr):
        """Set attributes with namespace to DOM implementation.
        Please notice that namespce must be a pairs of namespace name and
        namespace value. Attr composed by namespceURI, localName and value.
        """
        namespace_name, namespace_value = namespace
        if not self._node.hasAttribute(namespace_name):
            self._node.setAttribute(namespace_name, namespace_value)

        namespaceURI, localName, value = attr
        if not self._node.hasAttributeNS(namespaceURI, localName):
            qualifiedName = "%s:%s" % (namespace_name, localName)
            self._node.setAttributeNS(namespaceURI, qualifiedName, value)

    def getAttribute(self, attr_name):
        """Get attribute with specified name. And allowed get attribute with
        specified name in ``prefix:localName`` format.
        """
        if not self._node.hasAttribute(attr_name):
            localName = self.getLocalName(attr_name)
            if localName != attr_name:
                return self.getAttribute(localName)
            return

        return self._node.getAttribute(attr_name).decode("utf8")

    def setAttribute(self, attr_name, attr_value=None):
        """Set attribute to element. Please notice that if ``attr_value`` is
        None and attribute with specified ``attr_name`` is exist,
        attribute will be removed.
        """
        if attr_value is not None:
            self._node.setAttribute(attr_name,
                                    str(attr_value).encode("utf8"))
        elif self._node.hasAttribute(attr_name):
            self._node.removeAttribute(attr_name)

    def createElement(self, tag_name):
        """Create new element. But created element doesn't add to the child
        node list of this element, invoke :func: ``self.appendChild`` or :func:
        ``self.insertBefore`` to add created element to the child node list of
        this element.
        """
        pass

    def addIdAttribute(self, attr_name):
        if not self._node.hasAttribute(attr_name):
            id = utils.generate_id()
            self._node.setAttribute(attr_name, id)

            if self.getOwnerDocument():
                self._node.setIdAttribute(attr_name)

    def getIndex(self):
        parent = self.getParentNode()
        if parent:
            index = 0
            for node in parent.childNodes:
                if self._node is node:
                    return index
                index += 1

        return -1

    def getTextContent(self):
        text = []
        for node in self._node.childNodes:
            if node.nodeType == DOM.Node.TEXT_NODE:
                text.append(node.data.decode("utf8"))

        if not len(text) > 0:
            return

        text = "\n".join(text)
        return text

    def setTextContent(self, data):
        for node in self._node.childNodes:
            if node.nodeType == DOM.Node.TEXT_NODE:
                self._node.removeChild(node)

        text = DOM.Text()
        text.data = data.encode("utf8")

        self._node.appendChild(text)


def main():
    pass

if __name__ == '__main__':
    main()
