#write a bytestream to the file at path dest
def handle_uploaded_file(bytestream, dest):
    with open(dest, 'wb+') as destination:
        for chunk in bytestream.chunks():
            destination.write(chunk)