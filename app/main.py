import sys
import os
import zlib
import hashlib

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
            print("Initialized git directory")
    elif command == "cat-file" and sys.argv[2] == "-p":
        hash = sys.argv[3]
        folder = hash[:2]
        filename = hash[2:]
        path = f".git/objects/{folder}/{filename}"
        with open(path,"rb") as f:
            data = f.read()
            data = zlib.decompress(data)
            x = data.find(b'\x00')
            content = data[x+1:]
            content_decoded = content.decode("utf-8")
            print (content_decoded,end = "")
    elif command == "hash-object" and sys.argv[2] == "-w":
        with open(sys.argv[3], "rb") as f:
            contents = f.read()
            header = f"blob {len(contents)}\0".encode("utf-8")
            sha1_hash = hashlib.sha1(header + contents).hexdigest()
            print(sha1_hash)
            folder,filename = sha1_hash[:2],sha1_hash[2:]
            path = f".git/objects/{folder}/{filename}"

            os.makedirs(f".git/objects/{folder}",exist_ok = True)
            with open(path,"wb") as f:
                f.write(zlib.compress(header + contents))
    elif command == "ls-command" and sys.argv[2] == "--name-only":
        hash = sys.argv[3]
        folder = hash[:2]
        filename = hash[2:]
        path = f".git/objects/{folder}/{filename}"
        with open(path,"rb") as f:
            data= zlib.decompress(f.read())
            null_index = data.find(b'\x00')
            entries_data=data[null_index+1:]
            i = 0
            names = []
            while i< len(entries_data):
                null_byte_index = entries_data.find(b'\x00', i)
                entry = entries_data[i:null_byte_index]  # slices <mode> <name>
                mode, name = entry.split(b' ', 1)
                names.append(name.decode())
                i = null_byte_index + 1 + 20 
            names.sort()
            for name in names:
                print(name)
           



               
               












            

        
            




    

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
