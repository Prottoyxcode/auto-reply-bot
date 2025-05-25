with open("text1.txt") as f1:
    cont1=f1.read()


with open("text2.txt") as f2:
    cont2=f2.read()

if(cont1==cont2):
    print("yes")

else:
    print("no")
