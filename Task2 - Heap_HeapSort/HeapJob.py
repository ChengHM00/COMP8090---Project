# Construct max heap for heap sort
class MaxHeap:

    def __init__(self):
    #Initial empty heap
        self.data = []

    def insert(self, value):
    #insert new value to the heap
        """Insert a value into the max-heap."""
        self.data.append(value)
        self._bubble_up(len(self.data) - 1)

    def extract_max(self):
    # remove and return the maximum element from the heap
        """Remove and return the maximum element."""
        if not self.data:
            return None
        if len(self.data) == 1:
            return self.data.pop()

        max_value = self.data[0]
        self.data[0] = self.data.pop()   # Move last element to root
        self._bubble_down(0)
        return max_value

    def peek(self):
    # getMax(), Return the maximum element without removing 
        """Return max element without removing."""
        return self.data[0] if self.data else None

    
    def _bubble_up(self, index):
    # Restore the heap property after insertion.
        parent = (index - 1) // 2
        while index > 0 and self.data[index] > self.data[parent]:
            self.data[index], self.data[parent] = self.data[parent], self.data[index]
            index = parent
            parent = (index - 1) // 2

    def _bubble_down(self, index):
    # Restore the heap property after removal of the root.
        size = len(self.data)
        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            largest = index

            if left < size and self.data[left] > self.data[largest]:
                largest = left
            if right < size and self.data[right] > self.data[largest]:
                largest = right

            if largest == index:
                break

            self.data[index], self.data[largest] = self.data[largest], self.data[index]
            index = largest

#heap sort using the MaxHeap
def heap_sort(items):
    heap = MaxHeap()
    
    # Build heap
    for item in items:
        heap.insert(item)

    # Extract in sorted order
    sorted_items = []
    while heap.peek() is not None:
        sorted_items.append(heap.extract_max())

    return sorted_items

 # Example data: (priority, job_name)           
jobs = [
    (2, "Job A"),
    (5, "Job B"),
    (3, "Job C"),
    (1, "Job D")
]

# Perform heap sort on the job list
sorted_jobs = heap_sort(jobs)

print("Sorted order:")
for prio, name in sorted_jobs:
    print(f"{name} (priority {prio})")

