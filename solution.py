from typing import List
from collections import defaultdict
import json

class Solution:
    def __init__(self, data_file_path: str, protocol_json_path: str):
        self.data_file_path = data_file_path
        self.protocol_json_path = protocol_json_path
        self.version = ""
        self.message_counts = defaultdict(int)
        self.size_mismatch = set()
        self.size_non_dynamic_sizes = defaultdict(set)
        self.load_protocol_json_path()
        self.analyze_data()

    def load_protocol_json_path(self):
     with open(self.protocol_json_path) as f: 
      self.protocols = json.load(f)

    def fps_to_count(self, fps: int)->int:
     fps_map = {1 : 1, 9 : 48, 18: 48, 36: 164}  #fbs table
     return fps_map.get(fps, 0)
    
    def parse_message(self, line: str):
     msg_parts = line.strip().split(", ")
     protocol_id = msg_parts[2]
     excepted_length =  int(msg_parts[3].split()[0])   # 4 bytes  -> 4
     message_data = msg_parts[4]
     return protocol_id, excepted_length, message_data

    def analyze_message(self, protocol_id: str, expected_len: int, data:str):
     self.message_counts[protocol_id] += 1 
     actual_len = len(data.split())
     if expected_len != actual_len:
        self.size_mismatch.add(protocol_id) 
    
     if not self.protocols["protocols"][protocol_id].get("dynamic_size", True):
        self.size_non_dynamic_sizes[protocol_id].add(expected_len)


    def extract_version(self, first_line: str):
       protocol_id, expected_len, data = self.parse_message(first_line)
       self.analyze_message(protocol_id, expected_len, data)

       if protocol_id == "0x1":  
          hex_values = data.split()
          self.version = ''.join(chr(int(hex_value, 16)) for hex_value in hex_values)
        
    def analyze_data(self):
       with open(self.data_file_path) as f: 
          self.extract_version(f.readline())
          for line in f:
             protocol_id, expected_len, data = self.parse_message(line)

          self.analyze_message(protocol_id, expected_len, data)

    # Question 1: What is the version name used in the communication session?
    def q1(self) -> str:
        return self.version

    # Question 2: Which protocols have wrong messages frequency in the session compared to their expected frequency based on FPS?
    def q2(self) -> List[str]:
        wrong_msg_freq = [] 
        for protocol_id, actual_count in self.message_counts.items():
           fps = self.protocols["protocols"][protocol_id]["fps"]
           expected_count = self.fps_to_count(fps)  
           if actual_count != expected_count:
              wrong_msg_freq.append(protocol_id)
        return wrong_msg_freq

    # Question 3: Which protocols are listed as relevant for the version but are missing in the data file?
    def q3(self) -> List[str]:
          version_spec = self.protocols["protocols_by_version"][self.version]
          missing = []
         
          for protocol in version_spec["protocols"]:
            if version_spec["id_type"] == "dec":
                protocol_id = f"0x{int(protocol):x}"
            else:
                protocol_id = f"0x{protocol}"

            if protocol_id not in self.message_counts:
                missing.append(protocol_id)
          return missing

          
    # Question 4: Which protocols appear in the data file but are not listed as relevant for the version?
    def q4(self) -> List[str]:
       extra = []
       version_spec = self.protocols["protocols_by_version"][self.version]
       excepted_protocols = set(version_spec["protocols"])
       for protocol_id in self.message_counts: 
          protocol_number = protocol_id.lstrip("0x")
          if version_spec["id_type"] == "dec":
             protocol_number = str(int(protocol_number, 16))
          if protocol_number not in excepted_protocols:
             extra.append(protocol_id)
       return extra

    # Question 5: Which protocols have at least one message in the session with mismatch between the expected size integer and the actual message content size?
    def q5(self) -> List[str]:
        return list(self.size_mismatch)
    
    # Question 6: Which protocols are marked as non dynamic_size in protocol.json, but appear with inconsistent expected message sizes Integer in the data file?
    def q6(self) -> List[str]:
        d = []
        for protocol_id, size in self.size_non_dynamic_sizes.items():
           if len(size) > 1:
            d.append(protocol_id)
        return d
           
def main():
   sol = Solution("data.txt", "./protocol.json")
   print("version:", sol.q1())
   print("wrong msg freq:", sol.q2())
   print("not listed:", sol.q3())
   print("extra listed:", sol.q4())
   print("size_mismatch:", sol.q5())
   print("non dynamic_size in protocol.json:", sol.q6())
 
if __name__ == "__main__":
   main()