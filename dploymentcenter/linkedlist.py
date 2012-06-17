class Node(object):
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

    def __repr__(self):
        return "<Node(%r)>" % self.data

    def delete(self):
        """Get rid of the node"""
        self.prev.next = self.next
        self.next.prev = self.prev

class LinkedList(object):
    def __init__(self):
        self._start = Node('Start') # Never moves
        self._end = Node('End') # Never moves
        self._start.next = self._end
        self._end.prev = self._start

    def insert_after(self, node, new_node):
        new_node.prev = node
        new_node.next = node.next
        node.next.prev = new_node
        node.next = new_node

    def insert_before(self, node, new_node):
        new_node.prev = node.prev
        new_node.next = node
        node.prev.next = new_node
        node.prev = new_node

    def append(self, new_node):
        self.insert_before(self._end, new_node)

    def prepend(self, new_node):
        self.insert_after(self._start, new_node)

    def __iter__(self):
        current_node = self._start.next
        while current_node != self._end:
            yield current_node
            current_node = current_node.next
