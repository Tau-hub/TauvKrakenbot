
kraken = r'$$\   $$\ $$$$$$$\   $$$$$$\  $$\   $$\ $$$$$$$$\ $$\   $$\ ' + "\n"
kraken +=r'$$ | $$  |$$  __$$\ $$  __$$\ $$ | $$  |$$  _____|$$$\  $$ |' + "\n"
kraken +=r'$$ |$$  / $$ |  $$ |$$ /  $$ |$$ |$$  / $$ |      $$$$\ $$ |' + "\n"
kraken +=r'$$$$$  /  $$$$$$$  |$$$$$$$$ |$$$$$  /  $$$$$\    $$ $$\$$ |' + "\n"
kraken +=r'$$  $$<   $$  __$$< $$  __$$ |$$  $$<   $$  __|   $$ \$$$$ |' + "\n"
kraken +=r'$$ |\$$\  $$ |  $$ |$$ |  $$ |$$ |\$$\  $$ |      $$ |\$$$ |' + "\n"
kraken +=r'$$ | \$$\ $$ |  $$ |$$ |  $$ |$$ | \$$\ $$$$$$$$\ $$ | \$$ |' + "\n"
kraken +=r'\__|  \__|\__|  \__|\__|  \__|\__|  \__|\________|\__|  \__|' + "\n" +"\n"

def display():
    print()
    print("\033[5;32;40m{}".format(kraken), end='')
    n = 22
    print("\033[0;31;40m")
    string_equal = "".join(["=" for _ in range(0,n)])
    space_equal = "".join([" " for _ in range(0,(n-4))])
    print("{} VERSION 1.0.0 {}".format(string_equal,string_equal))
    print("|{}MADE BY TEDDY AUDEVAL{}|".format(space_equal, space_equal))
    print("===========================================================")
    print("\033[0;37;40m")
    
    