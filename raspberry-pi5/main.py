from multiprocessing import Process, Queue

class CustomObject:
    def init(self, value):
        self.value = value

def worker(queue):
    obj = queue.get()
    obj.value += 10
    print(f"Processed value: {obj.value}")

if __name__ == "__main__":
    queue = Queue()
    obj = CustomObject(5)
    queue.put(obj)

    process = Process(target=worker, args=(queue,))
    process.start()
    process.join()