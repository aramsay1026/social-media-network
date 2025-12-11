class LinkedDictionary:
    # Simple dictionary implementation
    def __init__(self):
        self.dict = {}

    def add(self, key, value):
        self.dict[key] = value

    def remove(self, key):
        if key in self.dict:
            del self.dict[key]

    def get_value(self, key):
        return self.dict.get(key, None)

    def get_keys(self):
        return self.dict.keys()

class LinkedQueue:
    # Simple queue implementation using list
    def __init__(self):
        self.queue = []

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        return None

    def is_empty(self):
        return len(self.queue) == 0