# Compresor-LempelZIV-BW

## Versión 2 del compresor

Tiene las siguientes restriciones:
  >Por como estan conformados los bytes del comprimido(1 flag + 4 pos + 3 long), solo se aceptan ascii hasta el 128
  
  >(Fixed)Problema de que un índice del BW sea 13 (lo skipea y cancela la compresión), esto provoca que no se guarde el ascii del retorno de carro por usar str
  
  >Escrito en python 3.10
  
Se agregan también un nuevo archivo de pruebas que valida la compresion del algoritmo aplicado
