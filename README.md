# TeemO
2026-1 Algorithm Project

## Algorithm Concepts Applied

### 1. Merge Sort (Week 03)
- Purpose: Sort detected threats by severity score in descending order
  before passing results to the Solar LLM
- Method: Divide & Conquer based comparison sort
- Each traffic entry is assigned a threat score based on its label
  (e.g., BENIGN=0, PortScan=3, DoS=7, DDoS=10)
- Merge Sort is applied to rank threats from highest to lowest severity
- Time complexity: O(n log n) guaranteed in all cases
- Chosen over Quick Sort due to stable sorting and no worst-case degradation

### 2. Hash Table with Separate Chaining (Week 10)
- Purpose: Count and detect suspicious source IPs in O(1) average time
- Hash function: h(k) = k mod m (Division Method)
- Collision resolution: Separate Chaining (linked list per slot)
- Each source IP is converted to an integer key and inserted into the hash table
- IPs with request counts exceeding a threshold are flagged as suspicious
- Time complexity: O(1) average for insert and search
