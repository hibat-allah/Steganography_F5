#! read a msg frome a .txt file
def file_str(file_name):
    with open(file_name, 'r') as myfile:
        message=myfile.read()
    return message
#! write a msg into a .txt file
def str_file(message,file_name):
    file1 = open(file_name, "w")
    file1.write(message)
    file1.close()

    return file1
