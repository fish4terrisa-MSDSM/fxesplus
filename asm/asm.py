import sys
import keys
import struct
prompts = '''
Usage:
    asm <input file>
'''

base_addr = 0xd522
syms = []
debug =False
showdump = print
if not debug:
    print = lambda a=0,b=0,c=0,d=0,e=0,f=0,g=0:0

def loadsym():
    global syms
    with open('../991cnx/symbols.txt','r') as f:
        lines = f.readlines()
        for s in lines:
            flag = 0
            s = s.strip()
            if len(s) == 0 or s[0] == ';':
                continue
            if s[0] == '@':
                flag = 1
                s = s[1:]
            ps = s.split('       ')
            if len(ps)==2:
                syms.append([ps[0].lower(),ps[1].lower(),flag])

def loopup(name:str):
    global syms
    flag = 0
    if name[0] == '@':
        flag = 1
        name = name[1:]
    for s in syms:
        if s[1] == name:
            if s[2] == 1:
                if flag == 1:
                    return hex(int('3'+s[0],16))
                return hex(int('3'+s[0],16)+2)
            elif s[2] == 2:
                return hex(int(s[0],16))
            else:
                return hex(int('3'+s[0],16))
    print('Unknown symbol name: '+name)
    exit()                    

def preline(line:str):
    return nextstr(line[0:len(line)].strip().lower())


def next_arg(line:str,force16 = False):
    s = line.split(' ')
    if len(s)<2:
        return 0,'Require at least 1 argument here!\n'+'---> '+line
    s[1] = s[1].strip()
    i = 0
    if s[1].startswith('0x') or force16:
        i = int(s[1],16)
    else:
        i = int(s[1])
    if len(s) > 2:
        if not s[2].strip().startswith(';'):
            return 0,'Too much arguments here!\n'+'---> '+line
    return i,''

def readall(path):
    with open(path, 'r') as f:
        return f.readlines()
def nextstr(line:str):
    idx = line.find(';')
    if idx == -1:
        return line.strip()
    return line[0:line.find(';')].strip()

def process(strs,fstpass=True):
    global base_addr
    dump = ''
    line_num = 1
    for line in strs:
        line = preline(line)

        if line.startswith(';') or line == '':
            continue
        
        if line.startswith('space'):
            i,p = next_arg(line)
            if p != '':
                print(p)
                exit()
            print('space '+str(i)+' bytes.')
            base_addr+=i
        elif line.startswith('hex'):
            tokens = line[3:]
            print(tokens)
            i = 0
            bin = ''
            while i < len(tokens):
                if len(bin)<2 and not fstpass:
                    if tokens[i]!=' ':
                        bin+=tokens[i]
                        if len(bin) == 2:
                            #print('<'+bin+'>')
                            dump+=keys.byte2keys(bin)[0]+' '
                            bin = ''
                            base_addr+=2
                    
                i+=1
            if len(bin)>0:
                print('hex require to be aligned with 2 bytes!')
                exit()
        elif line.endswith(':'):
            s = line[:-1]
            syms.append([hex(base_addr),s,2])
        elif line.startswith('adr'):
            p = line[3:].strip().split(' ')
            if len(p) >2 or len(p) == 0:
                print('Too many args for adr!')
                exit()
            off = 0
            if len(p) == 2:
                if p[1].startswith('0x'):
                    off = int(p[1],16)
                else:
                    off = int(p[1])
            adr = loopup(p[0])[2:]
            adr = struct.pack('<I',int(adr,16)+off)
            adr = adr.hex()
            dump += keys.byte2keys(adr[0:2])[0]+' '
            dump += keys.byte2keys(adr[2:4])[0]+' '

        elif len(line):
            if not fstpass:
                name = nextstr(line)
                print(line)
                adr = '30'+loopup(name)[2:]
                adr = struct.pack('<I',int(adr,16))
                adr = adr.hex()
                print(adr)
                dump += keys.byte2keys(adr[0:2])[0]+' '
                dump += keys.byte2keys(adr[2:4])[0]+' '
                dump += keys.byte2keys(adr[4:6])[0]+' '+'0 '
            base_addr+=4
        line_num += 1
    if fstpass:
        dump = ''
        print('first pass [OK]')
    else:
        showdump(dump)
if __name__ == '__main__':
    
    l = len(sys.argv)
    if l != 2:
        print(prompts)
        exit()
    path = sys.argv[1]
    loadsym()
    print(syms)
    c = readall(path)
    process(c)
    process(c,False)