import sys
import os
import zlib
import hashlib
import time


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
    elif command == "ls-tree" and sys.argv[2] == "--name-only":
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
    elif command == "write-tree":
        
        def write_tree(dir_path="."):
            entries = []

            # Go through everything in the directory
            for entry in sorted(os.listdir(dir_path)):
                if entry == ".git":  # never include .git itself
                    continue

                full_path = os.path.join(dir_path, entry)

                # CASE 1: FILE 
                if os.path.isfile(full_path):
                    # Read the file
                    with open(full_path, "rb") as f:
                        data = f.read()

                    # Build a blob object ("blob <size>\0<contents>")
                    blob_data = f"blob {len(data)}\0".encode() + data
                    blob_sha = hashlib.sha1(blob_data).hexdigest()

                    # Save the blob to .git/objects if not already there
                    folder, filename = blob_sha[:2], blob_sha[2:]
                    obj_path = f".git/objects/{folder}/{filename}"
                    if not os.path.exists(obj_path):
                        os.makedirs(f".git/objects/{folder}", exist_ok=True)
                        with open(obj_path, "wb") as f:
                            f.write(zlib.compress(blob_data))

                    # Add this file entry to the tree (mode + name + binary sha)
                    entries.append(b"100644 " + entry.encode() + b"\0" + bytes.fromhex(blob_sha))

                #  CASE 2: DIRECTORY
                elif os.path.isdir(full_path):
                    # Recursively write the subdirectory tree
                    subtree_sha = write_tree(full_path)

                    # Add the directory entry to the parent tree
                    entries.append(b"40000 " + entry.encode() + b"\0" + bytes.fromhex(subtree_sha))

            # BUILD THIS DIRECTORY'S TREE OBJECT
            body = b"".join(entries)
            header = f"tree {len(body)}\0".encode()
            full_data = header + body

            # Compute the SHA-1 of this tree object
            tree_sha = hashlib.sha1(full_data).hexdigest()

            # Save the tree object
            folder, filename = tree_sha[:2], tree_sha[2:]
            obj_path = f".git/objects/{folder}/{filename}"
            if not os.path.exists(obj_path):
                os.makedirs(f".git/objects/{folder}", exist_ok=True)
                with open(obj_path, "wb") as f:
                    f.write(zlib.compress(full_data))

            # Return this tree’s SHA to the parent
            return tree_sha

        # Start from the current directory and print the root tree SHA
        root_sha = write_tree(".")
        print(root_sha)
    elif command == "commit-tree":
        tree_sha = sys.argv[2]
        parent_sha = sys.argv[4]
        message = sys.argv[6]

        author_name = "Nathan"
        author_email = "nathanrbel@gmail.com"
        timestamp = int(time.time())
        timezone = "+0000"

        commit_content = (
        f"tree {tree_sha}\n"
        f"parent {parent_sha}\n"
        f"author {author_name} <{author_email}> {timestamp} {timezone}\n"
        f"committer {author_name} <{author_email}> {timestamp} {timezone}\n"
        f"\n"
        f"{message}\n"
    )
        
        commit_bytes = commit_content.encode()
        header = f"commit {len(commit_bytes)}\0".encode()
        full_data = header + commit_bytes

        # Hash it
        commit_sha = hashlib.sha1(full_data).hexdigest()

        #store it
        folder, filename = commit_sha[:2], commit_sha[2:]
        obj_path = f".git/objects/{folder}/{filename}"
        if not os.path.exists(obj_path):
            os.makedirs(f".git/objects/{folder}", exist_ok=True)
            with open(obj_path, "wb") as f:
                f.write(zlib.compress(full_data))

        # Print commit hash
        print(commit_sha)
        



           



               
               












            

        
            




    

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
