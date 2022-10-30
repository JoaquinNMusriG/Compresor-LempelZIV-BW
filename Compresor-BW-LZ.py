import os
from tkinter import filedialog
import binascii
from operator import itemgetter #BW

def BW(s):
    n = len(s)
    m = sorted([s[i:n]+s[0:i] for i in range(n)])
    I = m.index(s)
    L = ''.join([q[-1] for q in m])
    return (I, L)

def match(i, string):
    long_coincidence = 1
    pos_coincidence = string[i-16:i].find(string[i])
    if pos_coincidence == -1:
        bin_no_coincidence = bin(ord(string[i])).removeprefix('0b')
        byte_to_store = int("1"+ "0"*(7-len(bin_no_coincidence)) + bin_no_coincidence,2)
    else:
        window = string[i-16:i]
        while window.find(string[i:i+long_coincidence]) != -1:         
            pos_coincidence = window.find(string[i:i+long_coincidence])
            if i + long_coincidence + 1 < len(string) and long_coincidence < 8:
                long_coincidence += 1
            else:
                long_coincidence += 1
                break
        pos_coincidence = bin(pos_coincidence).removeprefix('0b')
        long_aux = bin(long_coincidence-1).removeprefix('0b')
        long_coincidence -= 1

        if len(pos_coincidence) < 4:
            pos_coincidence = "0"*(4-len(pos_coincidence)) + pos_coincidence
        if len(long_aux) < 3:
            long_aux = "0"*(3-len(long_aux)) + long_aux
            
        byte_to_store = int("0"+ pos_coincidence + long_aux,2)
    return long_coincidence, byte_to_store

def LempelZiv(string):
    window_size = 16 
    #bytes_pos_size = 4
    #bytes_long_size = 3
    window = string[0:window_size]
    final_string = bytearray(window_size)
    for i, ch in enumerate(window):
        final_string[i] = int(bin(ord(ch)).removeprefix('0b'),2)

    i += 1
    while i < len(string):
        long_coincidence, byte_to_store = match(i, string)
        final_string.append(byte_to_store)
        i += long_coincidence
    
    compress = bytes(final_string)
    return compress 

def IBW(I, L):
    n = len(L)
    X = sorted([(i, x) for i, x in enumerate(L)], key=itemgetter(1))

    T = [None for i in range(n)]
    for i, y in enumerate(X):
        j, _ = y
        T[j] = i

    Tx = [I]
    for i in range(1, n):
        Tx.append(T[Tx[i-1]])

    S = [L[i] for i in Tx]
    S.reverse()
    return ''.join(S)

def Rmatch(j, string, window):
    long_coincidence = 1
    if ord(string[j]) > 127:
        string_readed = chr(int(bin(ord(string[j])).removeprefix('0b')[1:],2))
    else:
        coincide_byte = bin(ord(string[j])).removeprefix('0b')
        if len(coincide_byte) < 8:
            coincide_byte = "0"*(8-len(coincide_byte)) + coincide_byte

        pos = int(coincide_byte[1:5],2)
        length = int(coincide_byte[5:8],2)
        string_readed = window[pos:pos+length]
        long_coincidence = length
    return long_coincidence, string_readed

def RLempelZiv(string_compressed):
    window_size = 16
    j = 16
    string_descompressed = string_compressed[0:window_size] 
    while j < len(string_compressed):
        long_coincidence, string_readed = Rmatch(j, string_compressed, string_descompressed[window_size-16:window_size])
        string_descompressed += string_readed
        j += 1
        window_size += long_coincidence
    
    return string_descompressed

if __name__ == '__main__':
    menu = input("\n\nIngrese la opcion deseada: \n1: Comprimir un archivo\n2: Descomprimir un archivo\nAnyKey: Salir\n opción:")
    while menu == "1" or menu == "2":
        if menu == "1":
            filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File")
            name_extension = os.path.basename(filename)
            name_zip = name_extension[:name_extension.rfind(".")]  + "-Comprimido.jmg"

            error = False
            bigger = False
            with open(name_extension, "r") as file_to_compress:
                #file_in_ascii = str(binascii.b2a_qp(file_to_compress.read())).removeprefix("b'").removesuffix("'")
                file_in_ascii = file_to_compress.read()
                if file_in_ascii[0] != "~":
                    BW_Block = 256
                    if len(file_in_ascii) < BW_Block:
                        I, L = BW(file_in_ascii)

                        compress = LempelZiv(L)
                    else: #REVISAR
                        bigger = True
                        j = 0
                        i = BW_Block
                        k = 1
                        index_stringBW = []
                        while k != 0:
                            if i < len(file_in_ascii):
                                I, L = BW(file_in_ascii[j:i])
                                index_stringBW.append((I,L))
                                j += BW_Block
                                i += BW_Block
                                if i >= len(file_in_ascii):
                                    k = BW_Block - (i - len(file_in_ascii))
                            elif k > 0:
                                I, L = BW(file_in_ascii[j:((i - BW_Block) + k)])
                                index_stringBW.append((I,L))
                                k = 0

                        stringLZ = ""
                        for i in range(len(index_stringBW)):
                            stringLZ += index_stringBW[i][1]
                        compress = LempelZiv(stringLZ)
                else:
                    print("No puedo comprimir este archivo D:")
                    error = True
            
            bug = False
            if not error and not bigger:
                aux = bytearray()
                aux.append(I)
                if I == 13:
                    bug = True
                delimiter = int("01111110",2) #Agrego el separador ~
                aux.append(delimiter)
                header = bytes(aux)
                if bug:
                    print("Hubo un error al intentar guardar el archivo")
                else:
                    with open(name_zip, "wb") as zip_file:
                        zip_file.write(header) 
                        zip_file.write(compress)
            elif not error and bigger:
                aux = bytearray()
                for i in range(len(index_stringBW)):
                    aux.append(index_stringBW[i][0])
                    if index_stringBW[i][0] == 13:
                        bug = True
                delimiter = int("01111110",2) #Agrego el separador ~
                aux.append(delimiter)
                header = bytes(aux)
                if bug:
                    print("Hubo un error al intentar guardar el archivo")
                else:
                    with open(name_zip, "wb") as zip_file:
                        zip_file.write(header) 
                        zip_file.write(compress)

            if not error and not bug:
                print("Se almacenó el comprimido en la direccion del programa")    
        elif menu == "2":
            filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File jmg")
            name_extension = os.path.basename(filename)
            name_unzip = name_extension[:name_extension.rfind("-")]  + "-Descomprimido.txt"

            with open(name_extension, "r") as file_to_decompress:
                file_compressed = file_to_decompress.read()
                amount_of_blocks = 0
                indexBW_list = []

                while file_compressed[amount_of_blocks] != "~":
                    indexBW_list.append(ord(file_compressed[amount_of_blocks]))
                    amount_of_blocks += 1
                
                string_compressed = file_compressed[amount_of_blocks + 1:]
            
            string_descompressed = RLempelZiv(string_compressed)

            stringIBW = ""
            if amount_of_blocks == 1:
                stringIBW = (IBW(indexBW_list[0], string_descompressed))
            else:
                BW_Block = 256
                j = 0
                i = BW_Block
                k = 1
                b = 0
                while k != 0 and b < amount_of_blocks:
                    if i < len(string_descompressed):
                        stringIBW += IBW(indexBW_list[b], string_descompressed[j:i])
                        j += BW_Block
                        i += BW_Block
                        b += 1
                        if i >= len(string_descompressed):
                            k = BW_Block - (i - len(string_descompressed))
                    elif k > 0:
                        stringIBW += IBW(indexBW_list[b], string_descompressed[j:((i - BW_Block) + k)])
                        k = 0

            final_string = bytearray(len(stringIBW))
            for i in range(len(stringIBW)):
                final_string[i] = int(bin(ord(stringIBW[i])).removeprefix('0b'),2)
            decompress = bytes(final_string)
            with open(name_unzip, "wb") as file_decompressed:
                file_decompressed.write(decompress)
            
            print("Se almacenó el descomprimido en la direccion del original")

        menu = input("\n\nIngrese la opcion deseada: \n1: Comprimir un archivo\n2: Descomprimir un archivo\nAnyKey: Salir\n opción:")