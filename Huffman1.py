import heapq
from collections import defaultdict

class HuffmanNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def walk(self, code, acc):
        self.left.walk(code, acc + "1")  
        self.right.walk(code, acc + "0")  

class HuffmanLeaf:
    def __init__(self, char):
        self.char = char

    def walk(self, code, acc):
        code[self.char] = acc or "0"

class HuffmanElement:
    def __init__(self, freq, node):
        self.freq = freq
        self.node = node

    def __lt__(self, other):
        return self.freq < other.freq

def huffman_code(freq):
    heap = []
    for char, f in freq.items():
        heap.append(HuffmanElement(f, HuffmanLeaf(char)))
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        heapq.heappush(heap, HuffmanElement(left.freq + right.freq, HuffmanNode(left.node, right.node)))

    root = heapq.heappop(heap).node
    code = {}
    root.walk(code, "")
    return code


simboli = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9']
verjetnosti = [0.25, 0.20, 0.15, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04]
freq = {simboli[i]: verjetnosti[i] for i in range(len(simboli))}
codes = huffman_code(freq)

print("Huffmanove kode:")
for char, code in sorted(codes.items()):
    print(f"{char}: {code}")
