import heapq
import hashlib
from collections import defaultdict
import sys
import struct
import os

sys.stdout.reconfigure(encoding='utf-8')

class HuffmanNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def walk(self, code, acc):
        self.left.walk(code, acc + "0")
        self.right.walk(code, acc + "1")

class HuffmanLeaf:
    def __init__(self, pair):
        self.pair = pair

    def walk(self, code, acc):
        code[self.pair] = acc or "0"

class HuffmanElement:
    def __init__(self, freq, node):
        self.freq = freq
        self.node = node

    def __lt__(self, other):
        return self.freq < other.freq

def huffman_code(freq):
    heap = []
    for pair, f in freq.items():
        heap.append(HuffmanElement(f, HuffmanLeaf(pair)))
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        heapq.heappush(heap, HuffmanElement(left.freq + right.freq, HuffmanNode(left.node, right.node)))

    root = heapq.heappop(heap).node
    code = {}
    root.walk(code, "")
    return code, root

def calculate_frequencies(data):
    freq = defaultdict(int)
    for i in range(0, len(data) - 1, 2):
        pair = data[i:i+2]
        freq[pair] += 1
    
    return freq

def encode_data(data, codes):
    encoded_data = ''
    for i in range(0, len(data) - 1, 2):
        pair = data[i:i+2]
        encoded_data += codes[pair]
    padding = 8 - len(encoded_data) % 8
    encoded_data += '0' * padding
    padded_info = "{:08b}".format(padding)
    return padded_info + encoded_data

def save_encoded_file(output_path, root, encoded_data):
    with open(output_path, 'wb') as f:
        tree_structure = []
        def serialize_tree(node):
            if isinstance(node, HuffmanLeaf):
                tree_structure.append((1, node.pair))
            else:
                tree_structure.append((0,))
                serialize_tree(node.left)
                serialize_tree(node.right)

        serialize_tree(root)
        serialized_tree = bytearray()
        for node in tree_structure:
            if node[0] == 1:
                serialized_tree.append(1)
                serialized_tree.extend(node[1])
            else:
                serialized_tree.append(0)

        tree_size = len(serialized_tree)
        f.write(struct.pack('>I', tree_size))
        f.write(serialized_tree)
        
        encoded_bytes = bytearray()
        for i in range(0, len(encoded_data), 8):
            byte = encoded_data[i:i+8]
            encoded_bytes.append(int(byte, 2))
        f.write(encoded_bytes)

def load_encoded_file(input_path):
    with open(input_path, 'rb') as f:
        tree_size = struct.unpack('>I', f.read(4))[0]
        serialized_tree = f.read(tree_size)
        
        def deserialize_tree(iterator):
            flag = next(iterator)
            if flag == 1:
                return HuffmanLeaf(bytes([next(iterator), next(iterator)]))
            else:
                left = deserialize_tree(iterator)
                right = deserialize_tree(iterator)
                return HuffmanNode(left, right)
        
        tree_iterator = iter(serialized_tree)
        root = deserialize_tree(tree_iterator)
        
        encoded_data = f.read()
        encoded_bits = ''.join(f"{byte:08b}" for byte in encoded_data)
        return root, encoded_bits

def decode_data(encoded_bits, root):
    decoded_bytes = bytearray()
    current_node = root
    padding = int(encoded_bits[:8], 2)
    encoded_bits = encoded_bits[8:-padding] if padding > 0 else encoded_bits[8:]
    
    i = 0
    while i < len(encoded_bits):
        bit = encoded_bits[i]
        i += 1
        current_node = current_node.left if bit == '0' else current_node.right
        
        if isinstance(current_node, HuffmanLeaf):
            decoded_bytes.extend(current_node.pair)
            current_node = root

    return decoded_bytes

def calculate_md5(data):
    return hashlib.md5(data).hexdigest()

def main():
    input_file = 'input.bin'
    output_file = 'output.huf'
    decode_file = 'decoded_output.bin'

    file_type = input_file.split('.')[-1]

    if file_type == 'txt':
        with open(input_file, 'r', encoding='utf-8') as f:
            data = f.read().encode('utf-8')
    else:
        with open(input_file, 'rb') as f:
            data = f.read()

    frequencies = calculate_frequencies(data)
    codes, root = huffman_code(frequencies)
    encoded_data = encode_data(data, codes)
    save_encoded_file(output_file, root, encoded_data)

    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)

    print(f"Prvotna velikost: {original_size} bajtov")
    print(f"Velikost po kompresiji: {compressed_size} bajtov")
    print(f"Razmerje kompresije: {original_size / compressed_size:.2f}")

    root, encoded_bits = load_encoded_file(output_file)
    if root is None:
        return

    decoded_data = decode_data(encoded_bits, root)

    if file_type == 'txt':
        with open(decode_file, 'w', encoding='utf-8') as f:
            f.write(decoded_data.decode('utf-8'))
    else:
        with open(decode_file, 'wb') as f:
            f.write(decoded_data)

    original_md5 = calculate_md5(data)
    decompressed_md5 = calculate_md5(decoded_data)

    print(f"Ujemanje MD5: {original_md5 == decompressed_md5}")

if __name__ == "__main__":
    main()
