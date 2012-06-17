from dploymentcenter.linkedlist import *

def test_initialize_linked_list():
    linked_list = LinkedList()

def test_add_to_list():
    linked_list = LinkedList()
    linked_list.append(Node(1))
    for node in linked_list:
        assert node.data == 1

def test_iterate_list_properly():
    linked_list = LinkedList()
    linked_list.append(Node(1))
    linked_list.append(Node(2))
    linked_list.append(Node(3))
    data = map(lambda a: a.data, linked_list)
    print data
    assert data == [1,2,3]

def test_list_delete():
    linked_list = LinkedList()
    linked_list.append(Node(1))
    linked_list.append(Node(2))
    linked_list.append(Node(3))
    for node in linked_list:
        if node.data == 2:
            node.delete()
    data = map(lambda a: a.data, linked_list)
    print data
    assert data == [1,3]
