import os

#op param1 param2 param3
#reg-1 = regDEST but also reg-2 somtimes for example in STR or
#reg-2 = regA
#reg-3 = regB
#index table format (which index each keyword grabs)
#[0]    | [1]    | [2]    | [3]
#opcode | reg-1  | reg-2  | reg-3
#       | FLAG   | Address
#       |        | memory address
#       |        | number
#Address, memory address, number must be last
#ZERO adds gaps between the addresses/variables in binary

#Lookup table on how each command is structured (every 4 bits)
SYNTAX = {
    "NOP": ["0000", "ZERO", "ZERO", "ZERO"],
    "HLT": ["0001", "ZERO", "ZERO", "ZERO"],
    "ADD": ["0010", "reg-1", "reg-2", "reg-3"],
    "SUB": ["0011", "reg-1", "reg-2", "reg-3"],
    "ORR": ["0100", "reg-1", "reg-2", "reg-3"],
    "NOR": ["0101", "reg-1", "reg-2", "reg-3"],
    "AND": ["0110", "reg-1", "reg-2", "reg-3"],
    "XOR": ["0111", "reg-1", "reg-2", "reg-3"],
    "INC": ["1000", "reg-1", "ZERO", "reg-2"],
    "DEC": ["1001", "reg-1", "ZERO", "reg-2"],
    "RSH": ["1010", "reg-1", "ZERO", "reg-2"],
    "JMP": ["1011", "ZERO", "Address"],
    "BIV": ["1100", "FLAG", "Address"],
    "LDI": ["1101", "reg-1", "number"],
    "STR": ["1110", "reg-1", "memory address"],
    "LOD": ["1111", "reg-1", "memory address"],
    "CPY": ["0010", "reg-1", "reg-2", "ZERO"], #extra commands
    "COM": ["0011", "ZERO", "reg-1", "reg-2"],
    "LSH": ["0010", "reg-1", "reg-2", "reg-2"]

}

variables = {}
#returns the length of opcode with out ZERO or repeats
def opLength(opcode):
    length = 1
    for index, param in enumerate(opcode[1:]):
        if param == 'ZERO' or param == opcode[index-1]: #doesnt count of ZERO or duplicate parameter since it gets same index
            continue
        else:
            length += 1
    return length

#get length of command before comments
def commandLength(command):
    length = 0
    for part in command:
        if part.startswith('//'): #stop count when reach a comment
            break
        length += 1
    return length

def hex_to_binary(hex_string):
    hex_value = int(hex_string, 16)  # convert hex string to integer
    num_bits = len(hex_string[2:]) * 4  # calculate number of bits based on length of hex string
    binary_value = format(hex_value, f'0{num_bits}b')  # format integer as binary string with correct number of bits
    return binary_value

#get the binary for the operands
def parse_operands(operand, parts):
    if operand.startswith('reg'):
        regHex = variables.get(parts[int(operand.split('-')[1])]) #get hex register number connected to variable name
        return hex_to_binary(regHex)
        #return hex_to_binary(parts[int(operand.split('-')[1])])
    elif operand == 'Address' or operand == 'memory address':
        return hex_to_binary(parts[len(parts)-1])
    elif operand == 'number':
        return format(int(parts[2]), '08b')
    #elif operand == 'FLAG': #redundant as JMP and BIV are handled seperately
    #    return '00' + parts[1]
    else:
        return -1

#JMP and BIV function to look up POS
def parse_jumps(program_dir, parts):
    with open(program_dir, 'r') as readFile: #open file to find POS
        Address = 0
        for Lines in readFile: 
            lineParts = Lines.split() #split line to get parts
            if not lineParts: #if line is blank set first index to a blank string
                lineParts = ['']
            if SYNTAX.get(lineParts[0]): #if its a command add one to address
                Address += 1
            if (parts[0] == 'JMP' and lineParts[0] == 'POS' and len(lineParts) >= 2 and parts[1] == lineParts[1]): #lineParts out of index error shouldnt matter because POS is checked first
                return '10110000' + format(Address, '08b'), None
            if (parts[0] == 'BIV' and lineParts[0] == 'POS' and len(lineParts) >= 2 and parts[2] == lineParts[1]):
                if parts[1] == 'Z': #find flag binary
                    flag = '01'
                elif parts[1] == 'P':
                    flag = '10'
                elif parts[1] == 'O':
                    flag = '11'
                else:
                    return None, f'no Flag found {parts}'
                return '110000' + flag + format(Address, '08b'), None
        return None, f'could not find POS {parts}' #return error if POS not found


#returns the binary for the input line
#returns binary, -1 if could not compile, nothing if line ignored
def getBinary(line, program_dir):
    parts = line.split()
    if not parts: #skip if line is blank
        return None, None
    opcode = SYNTAX.get(parts[0])
    if opcode: #core instructions
        
        if opLength(opcode) != commandLength(parts): #check length of command and raise error if incorrect
            return None, f'incorrect parameter count: {parts}'
        
        if parts[0] == 'JMP' or parts[0] == 'BIV': #special case for JMP and BIV
            binary, error = parse_jumps(program_dir, parts)
            return binary, error
        
        binary = opcode[0] #set opcode binary (first 4 bits)
        for operand in opcode[1:]: #get binary for parameters
            if operand == 'ZERO':
                binary += '0000'
            else:
                value = parse_operands(operand, parts)
                if value is None:
                    return None, f'could not parse operand {operand}'
                binary += value    
        return binary, None
    
    elif parts[0] == 'DEF':
        variables.update({parts[1] : parts[2]})
        return None, None
    elif parts[0] == 'POS':
        if len(parts) < 2:
            return None, f'POS formmated incorrectly {parts}'
        return None, None
    elif parts[0].startswith('//') or not parts[0]: #ignore codes
        return None, None
    else:
        return None, f'Unknown Opcode {opcode} in Line: {line}'

def assemble(file_name):
    program_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'programs', file_name))
    binary_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'binary.txt'))
    with open(program_dir, 'r') as readFile:
        with open(binary_dir, 'w') as writeFile:
            address = 0
            for i, line in enumerate(readFile):
                binary, error = getBinary(line, program_dir)
                if (error): #check errors
                    print(f'Error on line {i+1}: {error}')
                elif (binary):
                    print(format(address, '08b') + ' | ' + binary + ' | ' + line.strip('\n'))
                    writeFile.write(binary + '\n')
                    address += 1

                

assemble('fibbinaci.asm')