import sys
import os
import zlib

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the code below to pass the first stage
    #
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

            

        
            




    

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
