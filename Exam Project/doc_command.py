import os

def list_files_in_directory(directory):
    l=[]
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                l.append(os.path.join(root, file))
    return l                

if __name__ == "__main__":
    current_directory = "Main"
    l=list_files_in_directory(current_directory)
    l.sort()
    print("python3 -m pdoc", end=" ")
    for file in l:
        print("'"+file+"'", end=" ")
    print ("-o documentation")    