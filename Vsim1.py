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
        if (binary[25:30] == "11111"):
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

# Helpers for sim
def isBranch(instr):
    parts = instr.split()[0]
    mnemonic = parts in ["beq", "bne", "blt", "bge", "jal", "jalr"]
    return mnemonic

def getRegs(instr):
    parts = instr.replace(',', '').split()
    mnemonic = parts[0]
    inputReg = set()
    destReg = set()
    
    catOne = ["beq", "bne", "blt"]
    catTwo = ["add", "sub", "and", "or"]
    catThree = ["addi", "andi", "ori", "slli", "srai"]

    if mnemonic in catTwo:
        destReg.add(int(parts[1][1:]))
        inputReg.update([int(parts[2][1:]), int(parts[3][1:])])

    elif mnemonic in catThree:
        destReg.add(int(parts[1][1:]))
        inputReg.add(int(parts[2][1:]))

    elif mnemonic == "lw":
        offset, rs1 = parts[2].split('(')
        destReg.add(int(parts[1][1:]))
        inputReg.add(int(rs1.strip('x)')))

    elif mnemonic == "sw":
        offset, rs1 = parts[2].split('(')
        inputReg.add(int(parts[1][1:]))
        inputReg.add(int(rs1.strip('x)')))

    elif mnemonic in catOne:
        inputReg.update([int(parts[1][1:]), int(parts[2][1:])])

    elif mnemonic == "jal":
        destReg.add(int(parts[1][1:]))

    return inputReg, destReg

def hazardCheck(instr, inFlight):
    inputReg, destReg = getRegs(instr)

    for i in inFlight:
        inflightInput, inflightDest = getRegs(i)

        # RAW issue
        if inputReg & inflightDest:
            return True, "RAW"

        # WAR issue
        if destReg & inflightInput:
            return True, "WAR"

        # WAW issue
        if destReg & inflightDest:
            return True, "WAW"

    return False, None

# Should make sure if source and destination registers are not in use
def operandsReady(instr, scoreboard):
    inputReg, destReg = getRegs(instr)

    for reg in inputReg:
        if scoreboard[reg]["write"]:
            return False

    for reg in destReg:
        if scoreboard[reg]["write"] or scoreboard[reg]["read"]:
            return False

    return True


def computeBranchTarget(pc, instr, registers):
    parts = instr.replace(",", "").split()
    mnemonic = parts[0]

    if mnemonic in ["beq", "bne", "blt"]:
        rs1 = int(parts[1][1:])
        rs2 = int(parts[2][1:])
        imm = int(parts[3][1:])
        offset = imm * 2

        if mnemonic == "beq" and registers[rs1] == registers[rs2]:
            return pc + offset
        elif mnemonic == "bne" and registers[rs1] != registers[rs2]:
            return pc + offset
        elif mnemonic == "blt" and registers[rs1] < registers[rs2]:
            return pc + offset
        else:
            return pc + 4
        
    elif mnemonic == "jal":
        rd = int(parts[1][1:])
        imm = int(parts[2][1:])
        registers[rd] = pc + 4
        return pc + (imm * 2)
    
    else:
        return pc + 4

def parseOperand(operand):
    operand = operand.strip()
    if '(' in operand and ')' in operand:
        offset_str, reg_str = operand.split('(')
        offset = int(offset_str)
        reg = int(reg_str.strip('x)'))
        return offset, reg
    elif operand.startswith('x'):
        return 0, int(operand[1:])
    else:
        return int(operand[1:]), None

def simulator(instructions, dataMemory):
    registers = [0] * 32
    pc = 256
    cycle = 1
    executedInstr = None

    preIssue = []   # 4 things
    preALU1 = []    # 2 things
    preMEM = []     # 1 thing
    postMEM = []    # 1 thing
    preALU2 = []    # 1 thing
    postALU2 = []   # 1 thing
    preALU3 = []    # 1 thing
    postALU3 = []   # 1 thing

    # Control flags and hazard tracking
    breakFetch = False
    scoreboard = {reg: {"read": False, "write": False} for reg in range(32)}

    simulateFile = open("simulation.txt", "w")

    while True:
        print(f"Cycle {cycle}, PC={pc}, instr={instructions.get(pc)}")
        if breakFetch:
            print(f"Breaking early at cycle {cycle-1}, PC={pc}")
            break

        # Makes the header
        instr = instructions[pc]
        if instr == "break":
            print(f"Encountered break at PC={pc}. Halting simulation.")
            break

        simulateFile.write("-" * 20 + '\n')
        simulateFile.write(f"Cycle {cycle}:\n\n")
        cycle += 1

        # Writeback
        if postMEM:
            instr, destReg, val = postMEM.pop()
            registers[destReg] = val
            scoreboard[destReg]["write"] = False

        if postALU2:
            instr, destReg, val = postALU2.pop()
            registers[destReg] = val
            scoreboard[destReg]["write"]

        if postALU3:
            instr, destReg, val = postALU3.pop()
            registers[destReg] = val
            scoreboard[destReg]["write"]
        
        # Memory
        if preMEM:
            memInstr = preMEM.pop(0)
            parts = memInstr.replace(',', '').split()
            mnemonic = parts[0]

            if mnemonic == "lw":
                rd = int(parts[1][1:])
                offset, rs1 = parseOperand(parts[2])
                if rs1 is not None:
                    addr = registers[rs1] + offset
                    val = dataMemory.get(addr, 0)
                    postMEM.append((memInstr, rd, val))

            elif mnemonic == "sw":
                rs2 = int(parts[1][1:])
                offset, rs1 = parseOperand(parts[2])
                if rs1 is not None:
                    addr = registers[rs1] + offset
                    dataMemory[addr] = registers[rs2]

        # ALU stuff
        # lw and sw
        if preALU1:
            alu1Instr = preALU1.pop(0)
            parts = alu1Instr.replace(',', '').split()
            mnemonic = parts[0]

            if mnemonic in ["lw", "sw"]:
                offset, rs1 = parseOperand(parts[2])
                if rs1 is not None:
                    addr = registers[rs1] + offset
                    preMEM.append(alu1Instr)

        # add sub addi
        elif preALU2:
            alu2Instr = preALU2.pop(0)
            parts = alu2Instr.replace(',', '').split()

            mnemonic = parts[0]
            rd = int(parts[1][1:])
            offset, rs1 = parseOperand(parts[2])


            if mnemonic == "add":
                rs2 = int(parts[3][1:])
                val = registers[rs1] + registers[rs2]

            elif mnemonic == "sub":
                rs2 = int(parts[3][1:])
                val = registers[rs1] - registers[rs2]

            elif mnemonic == "addi":
                imm = int(parts[3][1:])
                val = registers[rs1] + imm
            
            else:
                val = None
            
            if val is not None:
                postALU2.append((alu2Instr, rd, val))
        
        # and or andi ori sll sra
        elif preALU3:
            alu3Instr = preALU3.pop(0)
            parts = alu3Instr.replace(',', '').split()
            
            mnemonic = parts[0]
            rd = int(parts[1][1:])
            offset, rs1 = parseOperand(parts[2])

            if mnemonic == "and":
                rs2 = int(parts[3][1:])
                value = registers[rs1] & registers[rs2]

            elif mnemonic == "or":
                rs2 = int(parts[3][1:])
                value = registers[rs1] | registers[rs2]

            elif mnemonic == "andi":
                imm = int(parts[3][1:])
                value = registers[rs1] & imm

            elif mnemonic == "ori":
                imm = int(parts[3][1:])
                value = registers[rs1] | imm

            elif mnemonic == "slli":
                imm = int(parts[3][1:])
                value = registers[rs1] << imm

            elif mnemonic == "srai":
                imm = int(parts[3][1:])
                value = registers[rs1] >> imm
            else:
                val = None

            if val is not None:
                postALU3.append((alu3Instr, rd, value))

        # Issue Stage
        issuedCount = 0
        inFlight = []
        for q in [preALU1, preMEM, preALU2, preALU3]:
            inFlight.extend(q)

        for q in [postMEM, postALU2, postALU3]:
            inFlight.extend(i[0] for i in q if isinstance(i, tuple))

        for instr in preIssue[:]:
            if issuedCount > 1:
                break

            parts = instr.replace(',', '').split()
            mnemonic = parts[0]

            hazard, type = hazardCheck(instr, inFlight)
            if hazard:
                continue
            
            if not operandsReady(instr, scoreboard):
                continue

            targetFU = None
            # Mem stuff
            if mnemonic in ["lw", "sw"]:
                targetFU = "ALU1"
            # Arith stuff
            elif mnemonic in ["add", "sub", "addi"]:
                targetFU = "ALU2"
            # Logi stuff
            elif mnemonic in ["and", "or", "andi", "ori", "slli", "srai"]:
                targetFU = "ALU3"

            # Checks structural hazards
            if (targetFU == "ALU1" and len(preALU1) > 1):
                continue
            if (targetFU == "ALU2" and len(preALU2) > 1):
                continue
            if (targetFU == "ALU3" and len(preALU3) > 1):
                continue

            if targetFU == "ALU1":
                preALU1.append(instr)
            elif targetFU == "ALU2":
                preALU2.append(instr)
            elif targetFU == "ALU3":
                preALU3.append(instr)

            inputReg, destReg = getRegs(instr)
            for r in inputReg:
                scoreboard[r]["read"] = True
            for r in destReg:
                scoreboard[r]["write"] = True

            preIssue.remove(instr)
            issuedCount += 1

        # Fetch / Decode
        fetchStall = False
        fetchPC = 256
        waitingInstr = None

        if (waitingInstr and operandsReady(waitingInstr, scoreboard)):
            executedInstr = waitingInstr
            pc = computeBranchTarget(pc, waitingInstr, registers)
            fetchPC = computeBranchTarget(pc, waitingInstr, registers)
            waitingInstr = None
            fetchStall = False
            continue
        else:
            executedInstr = None


        if not breakFetch:
            fetchedThisCycle = 0

            while fetchedThisCycle < 2 and len(preIssue) < 4 and not fetchStall:
                if fetchPC not in instructions:
                    break
                
                instr = instructions[fetchPC]
                
                if (instr == "break"):
                    breakFetch = True
                    break

                if isBranch(instr):
                    waitingInstr = instr
                    fetchStall = True
                    break

                preIssue.append(instr)
                fetchPC += 4
                fetchedThisCycle += 1

        # Write everything
        simulateFile.write("IF Unit:\n")

        if fetchStall and waitingInstr and isBranch(waitingInstr):
            simulateFile.write(f"\tWaiting: [{waitingInstr}]\n")
        else:
            simulateFile.write(f"\tWaiting:\n")

        if executedInstr and isBranch(executedInstr):
            simulateFile.write(f"\tExecuted: [{executedInstr}]\n")
        else:
            simulateFile.write(f"\tExecuted:\n")
        
        simulateFile.write("Pre-Issue Queue:\n")
        for i in range(4):
            if i < len(preIssue):
                simulateFile.write(f"\tEntry {i}: [{preIssue[i]}]\n")
            else:
                simulateFile.write(f"\tEntry {i}:\n")
        
        simulateFile.write(f"Pre-ALU1 Queue:\n")
        for i in range(2):
            if i < len(preALU1):
                simulateFile.write(f"\tEntry {i}: [{preALU1[i]}]\n")
            else:
                simulateFile.write(f"\tEntry {i}:\n")
        
        # MEM stuff
        simulateFile.write(f"Pre-MEM Queue:")
        if preMEM:
            simulateFile.write(f"\t[{preMEM[0]}]\n")
        else:
            simulateFile.write("\n")
        
        simulateFile.write(f"Post-MEM Queue:")
        if postMEM:
            simulateFile.write(f"\t[{postMEM[0][0]}]\n")
        else:
            simulateFile.write(f"\n")

        # ALU2
        simulateFile.write(f"Pre-ALU2 Queue:")
        if preALU2:
            simulateFile.write(f"\t[{preALU2[0]}]\n")
        else:
            simulateFile.write(f"\n")
        
        simulateFile.write(f"Post-ALU2 Queue:")
        if postALU2:
            simulateFile.write(f"\t[{postALU2[0][0]}]\n")
        else:
            simulateFile.write("\n")
        
        # ALU3
        simulateFile.write("Pre-ALU3 Queue:")
        if preALU3:
            simulateFile.write(f"\t[{preALU3[0][0]}]\n")
        else:
            simulateFile.write("\n")
        
        simulateFile.write("Post-ALU3 Queue:")
        if postALU3:
            simulateFile.write(f"\t[{postALU3[0][0]}]\n")
        else:
            simulateFile.write("\n")
        
        simulateFile.write("\n")
        
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

        simulateFile.write(f"\n")
        if not fetchStall and not breakFetch and not waitingInstr:
            pc += 4

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