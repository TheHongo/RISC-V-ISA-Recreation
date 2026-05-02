# On my honor, I have neither given nor received any unauthorized aid on this assignment
import sys

# Meant for beq, bne, blt, sw
def decodeCatOne(binary):
    
    imm_11_5 = binary[0:7]
    rs2 = binary[7:12]
    rs1 = binary[12:17]
    funct3 = binary[17:20] # Not used I think
    imm_4_0 = binary[20:25]
    opcode = binary[25:30] # Doesn't consider last 2 bits

    # Adds immediate bits
    immBin = imm_11_5 + imm_4_0
    imm = int(immBin, 2)

    # Checks if the imm value's supposed to be pos or neg
    if (immBin[0] == '1'):
        imm -= (1 << 12)

    # Def Registers
    rs1Num = int(rs1, 2)
    rs2Num = int(rs2, 2)

    # Makes the opcode an actual instruction
    opcodeTable = {
        "00000" : "beq",
        "00001" : "bne",
        "00010" : "blt",
        "00011" : "sw"
    }

    mnemonic = opcodeTable.get(opcode)
    
    if (mnemonic == "beq" or
        mnemonic == "bne" or
        mnemonic == "blt"):
        return f"{mnemonic} x{rs1Num}, x{rs2Num}, #{imm}"
    
    elif (mnemonic == "sw"):
        return f"{mnemonic} x{rs1Num}, {imm}(x{rs2Num})"


# Meant for add, sub, and, or
def decodeCatTwo(binary):

    func7 = binary[0:7] # Won't be used I think
    rs2 = binary[7:12]
    rs1 = binary[12:17]
    funct3 = binary[17:20] # Won't be used I think
    rd = binary[20:25]
    opcode = binary[25:30] # Doesn't consider last 2 bits

    # Def Registers
    rs1Num = int(rs1, 2)
    rs2Num = int(rs2, 2)
    rdNum = int(rd, 2)

    # Makes the opcode an actual instruction
    opcodeTable = {
        "00000" : "add",
        "00001" : "sub",
        "00010" : "and",
        "00011" : "or"
    }

    mnemonic = opcodeTable.get(opcode)

    return f"{mnemonic} x{rdNum}, x{rs1Num}, x{rs2Num}"


# Meant for addi, andi, ori, sll, sra, lw
def decodeCatThree(binary):

    imm_11_0 = binary[0:12]
    rs1 = binary[12:17]
    func3 = binary[17:20]
    rd = binary[20:25]
    opcode = binary[25:30]

    # Def Register
    rs1Num = int(rs1, 2)
    rdNum = int(rd, 2)

    # Immediate bit
    imm = int(imm_11_0, 2)

    # Checks if the imm value's supposed to be pos or neg
    if (imm_11_0[0] == '1'):
        imm -= (1 << 12)

    # Makes the opcode an actual instruction
    opcodeTable = {
        "00000" : "addi",
        "00001" : "andi",
        "00010" : "ori",
        "00011" : "slli",
        "00100" : "srai",
        "00101" : "lw"
    }

    mnemonic = opcodeTable.get(opcode)

    if (mnemonic == "addi" or mnemonic == "andi" or 
        mnemonic == "ori" or mnemonic == "slli" or
        mnemonic == "srai"):
        return f"{mnemonic} x{rdNum}, x{rs1Num}, #{imm}"

    elif (mnemonic == "lw"):
        return f"{mnemonic} x{rdNum}, {imm}(x{rs1Num})"
    

# Meant for jal and break
def decodeCatFour(binary):
    imm_19_0 = binary[0:20]
    rd = binary[20:25]
    opcode = binary[25:30]

    # Def immediate
    imm = int(imm_19_0, 2)

    # Def Register
    rdNum = int(rd, 2)

    # Checks if the imm value's supposed to be pos or neg
    if (imm_19_0[0] == '1'):
        imm -= (1 << 20)

    # Makes the opcode an actual instruction
    opcodeTable = {
        "00000" : "jal",
        "11111" : "break"
    }

    mnemonic = opcodeTable.get(opcode)

    if (mnemonic == "jal"):
        return f"{mnemonic} x{rdNum}, #{imm}"
    
    elif (mnemonic == "break"):
        return f"{mnemonic}"
    

def disassembler(inputFile):
    
    # Opens the file and reads it
    with open(inputFile, "r") as file:
        lines = [line.strip() for line in file.readlines()]
    
    breakIndex = None

    # Checks for breaks
    for i, binary in enumerate(lines):
        if (binary[-7:-2] == "11111"):
            breakIndex = i
            break
    dataLines = lines[breakIndex + 1:]

    # Disassembly file setup
    address = 256
    disassemblyFile = open("disassembly.txt", "w")
    instructions = {}
    dataMemory = {}

    # Depending on last 2 bits, decides on the decode function
    for binary in lines:
        lastTwo = binary[-2:]

        if (lastTwo == "00"):
            decoded = decodeCatOne(binary)
        elif (lastTwo == "01"):
            decoded = decodeCatTwo(binary)
        elif (lastTwo == "10"):
            decoded = decodeCatThree(binary)
        elif (lastTwo == "11"):
            decoded = decodeCatFour(binary)
    
        disassemblyFile.write(f"{binary}\t{address}\t{decoded}\n")
        instructions[address] = decoded


        # break if break appears (wow)
        if (decoded == "break"):
            address += 4
            break

        address += 4

    # Writes the disassembly.txt the values after the break using dataLines
    for dataLine in dataLines:
        value = int(dataLine, 2)
        if (dataLine[0] == "1"):
            value -= (1 << 32)
        disassemblyFile.write(f"{dataLine}\t{address}\t{value}\n")
        dataMemory[address] = value
        address += 4
    
    disassemblyFile.close()

    return instructions, dataMemory


# beq, bne, blt, sw
def simCatOne(instr, pc, registers, dataMemory):
    # Breaks up the string to be used for the functions
    parts = instr.replace(',', '').split()
    mnemonic = parts[0]

    # sw needs to be done first since diff string type
    if (mnemonic == "sw"):
        rs1 = int(parts[1][1:])
        offset, rs2 = parts[2].split('(')
        offset = int(offset)
        rs2 = int(rs2.strip('x)'))
        addr = registers[rs2] + offset
        dataMemory[addr] = registers[rs1]
        return pc + 4

    # Defines the registers, immediate val and offset for later
    rs1 = int(parts[1][1:])
    rs2 = int(parts[2][1:])
    imm = int(parts[3][1:])
    offset = imm * 2

    if (mnemonic == "beq" and
          registers[rs1] == registers[rs2]):
        return pc + offset
    elif (mnemonic == "bne" and 
          registers[rs1] != registers[rs2]):
        return pc + offset
    elif (mnemonic == "blt" and
          registers[rs1] < registers[rs2]):
        return pc + offset
    
    return pc + 4


# add, sub, and, or
def simCatTwo(instr, pc, registers):
    # Breaks up the instruction string and defs the registers and stuff
    parts = instr.replace(',', '').split()
    mnemonic = parts[0]
    rd = int(parts[1][1:])
    rs1 = int(parts[2][1:])
    rs2 = int(parts[3][1:])

    if (mnemonic == "add"):
        registers[rd] = registers[rs1] + registers[rs2]
    elif (mnemonic == "sub"):
        registers[rd] = registers[rs1] - registers[rs2]
    elif (mnemonic == "and"):
        registers[rd] = registers[rs1] & registers[rs2]
    elif (mnemonic == "or"):
        registers[rd] = registers[rs1] | registers[rs2]

    return pc + 4


# addi, andi, ori, sll, sra, lw
def simCatThree(instr, pc, registers, dataMemory):
    # Breaks up the instruction string and defs the registers and stuff
    parts = instr.replace(",", "").split()
    mnemonic = parts[0]
    rd = int(parts[1][1:])

    # lw done first since diff string type
    if mnemonic == "lw":
        offset, rs1 = parts[2].split('(')
        offset = int(offset)
        rs1 = int(rs1.strip('x)'))
        addr = registers[rs1] + offset
        registers[rd] = dataMemory.get(addr, 0)
        return pc + 4


    rs1 = int(parts[2][1:])
    imm = int(parts[3][1:])

    if (mnemonic == "addi"):
        registers[rd] = registers[rs1] + imm
    elif (mnemonic == "andi"):
        registers[rd] = registers[rs1] & imm
    elif (mnemonic == "ori"):
        registers[rd] = registers[rs1] | imm
    elif (mnemonic == "slli"):
        registers[rd] = registers[rs1] << imm
    elif (mnemonic == "srai"):
        registers[rd] = registers[rs1] >> imm

    return pc + 4


# jal
def simCatFour(instr, pc, registers):
    # Breaks up the instruction string and defs the registers and stuff
    parts = instr.replace(',', '').split()
    mnemonic = parts[0]
    rd = int(parts[1][1:])
    imm = int(parts[2][1:])

    # Since break is checked for earlier, jal's all I need to worry abt
    registers[rd] = pc + 4
    return pc + (imm * 2)


def simulator(instructions, dataMemory):
    registers = [0] * 32
    pc = 256
    cycle = 1
    simulateFile = open("simulation.txt", "w")

    while True:
        # Makes the header
        instr = instructions[pc]
        simulateFile.write("-" * 20 + '\n')
        simulateFile.write(f"Cycle {cycle}:\t{pc}\t{instr}\n")

        mnemonic = instr.split()[0]

        if (mnemonic == "beq" or mnemonic == "bne" or
            mnemonic == "blt" or mnemonic == "sw"):
            pc = simCatOne(instr, pc, registers, dataMemory)

        elif (mnemonic == "add" or mnemonic == "sub" or
            mnemonic == "and" or mnemonic == "or"):
            pc = simCatTwo(instr, pc, registers)

        elif (mnemonic == "addi" or mnemonic == "andi" or
            mnemonic == "ori" or mnemonic == "slli" or 
            mnemonic == "srai" or mnemonic == "lw"):
            pc = simCatThree(instr, pc, registers, dataMemory)

        elif (mnemonic == "jal"):
            pc = simCatFour(instr, pc, registers)

        # Makes sure x0 is always 0
        registers[0] = 0 

        # Prints registers
        simulateFile.write("Registers\n")

        for i in range(0, 32, 8):
            vals = [str(registers[j]) for j in range(i, i + 8)]
            simulateFile.write(f"x{i:02d}:\t" + "\t".join(vals) + "\n")

        # Prints data
        simulateFile.write("Data\n")

        sortAddress = sorted(dataMemory.keys())
        for i in range(0, len(sortAddress), 8):
            addressGroup = sortAddress[i:i+8]
            vals = [str(dataMemory[a]) for a in addressGroup]
            simulateFile.write(f"{addressGroup[0]}:\t" + "\t".join(vals) + "\n")

        if mnemonic == "break":
            break

        cycle += 1

    simulateFile.close()


def main():
    # Takes the file to read
    inputFile = sys.argv[1]

    # Instr and datamem used for sim later
    instructions, dataMemory = disassembler(inputFile)

    # Sim takes the two for use
    simulator(instructions, dataMemory)


if (__name__ == "__main__"):
    main()