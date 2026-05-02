# On my honor, I have neither given nor received any unauthorized aid on this assignment
import sys

# Meant for beq, bne, blt, sw
def decodeCatOne(binary):
    
    imm_11_5 = binary[0:7]
    rs2 = binary[7:12]
    rs1 = binary[12:17]
    funct3 = binary[17:20]
    imm_4_0 = binary[20:25]
    opcode = binary[25:30]

    immBin = imm_11_5 + imm_4_0
    imm = int(immBin, 2)

    if (immBin[0] == '1'):
        imm -= (1 << 12)

    rs1Num = int(rs1, 2)
    rs2Num = int(rs2, 2)

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


def decodeCatTwo(binary):

    func7 = binary[0:7]
    rs2 = binary[7:12]
    rs1 = binary[12:17]
    funct3 = binary[17:20]
    rd = binary[20:25]
    opcode = binary[25:30]

    rs1Num = int(rs1, 2)
    rs2Num = int(rs2, 2)
    rdNum = int(rd, 2)

    opcodeTable = {
        "00000" : "add",
        "00001" : "sub",
        "00010" : "and",
        "00011" : "or"
    }

    mnemonic = opcodeTable.get(opcode)

    return f"{mnemonic} x{rdNum}, x{rs1Num}, x{rs2Num}"


def decodeCatThree(binary):

    imm_11_0 = binary[0:12]
    rs1 = binary[12:17]
    func3 = binary[17:20]
    rd = binary[20:25]
    opcode = binary[25:30]

    rs1Num = int(rs1, 2)
    rdNum = int(rd, 2)

    imm = int(imm_11_0, 2)

    if (imm_11_0[0] == '1'):
        imm -= (1 << 12)

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
    

def decodeCatFour(binary):
    imm_19_0 = binary[0:20]
    rd = binary[20:25]
    opcode = binary[25:30]

    imm = int(imm_19_0, 2)

    rdNum = int(rd, 2)

    if (imm_19_0[0] == '1'):
        imm -= (1 << 20)

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
    
    with open(inputFile, "r") as file:
        lines = [line.strip() for line in file.readlines()]
    
    breakIndex = None

    for i, binary in enumerate(lines):
        if (binary[25:30] == "11111"):
            breakIndex = i
            break
    dataLines = lines[breakIndex + 1:]

    address = 256
    instructions = {}
    dataMemory = {}

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
    
        instructions[address] = decoded

        if (decoded == "break"):
            address += 4
            break

        address += 4

    for dataLine in dataLines:
        value = int(dataLine, 2)
        if (dataLine[0] == "1"):
            value -= (1 << 32)
        dataMemory[address] = value
        address += 4
    
    return instructions, dataMemory

def isBranch(instr):
    parts = instr.split()[0]
    mnemonic = parts in ["beq", "bne", "blt", "bge", "jal", "jalr"]
    return mnemonic


# Should just return the regs
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


def hazardCheck(instr, inFlight, writebackStalls):
    inputReg, destReg = getRegs(instr)
    # One check for writeback stall and another for structural stalls
    # I hate stalls, I literally missed the deadline because of stalls

    # Check against instructions currently in writeback stall
    for stallInstr, stallReg, _, _ in writebackStalls:
        _, stallDestRegs = getRegs(stallInstr)
        
        # RAW hazard
        if inputReg & stallDestRegs:
            return True
        
        # WAW hazard
        if destReg & stallDestRegs:
            return True

    # Check against in-flight instructions
    for i in inFlight:
        inflightInput, inflightDest = getRegs(i)

        # RAW hazard
        if inputReg & inflightDest:
            return True

        # WAR hazard
        if destReg & inflightInput:
            return True

        # WAW hazard
        if destReg & inflightDest:
            return True

    return False


# Should make sure instructions can be executed
def operandsReady(instr, scoreboard, writebackStalls):
    inputReg, destReg = getRegs(instr)

    # Check if input reg written by stall
    for _, stallReg, _, _ in writebackStalls:
        if stallReg in inputReg:
            return False

    # Check scoreboard
    for reg in inputReg:
        if scoreboard[reg]["write"]:
            return False

    for reg in destReg:
        if scoreboard[reg]["write"] or scoreboard[reg]["read"]:
            return False

    return True


# creates the branching and jumping for the instructions
def computeBranchTarget(pc, instr, registers):
    parts = instr.replace(",", "").split()
    mnemonic = parts[0]

    # mnemonic xN xN #N
    if mnemonic in ["beq", "bne", "blt"]:
        rs1 = int(parts[1][1:])
        rs2 = int(parts[2][1:])
        imm = int(parts[3][1:])
        offset = imm * 2

        taken = False
        if (mnemonic == "beq" and registers[rs1] == registers[rs2]):
            taken = True
        elif (mnemonic == "bne" and registers[rs1] != registers[rs2]):
            taken = True
        elif (mnemonic == "blt" and registers[rs1] < registers[rs2]):
            taken = True

        if (taken):
            return pc + offset
        else:
            return pc + 4
    
    # jal xN #N
    elif (mnemonic == "jal"):
        rd = int(parts[1][1:])
        imm = int(parts[2][1:])
        
        registers[rd] = pc + 4
        return pc + (imm * 2)
    
    else:
        return pc + 4


# Breaks the functions apart
def parseOperand(operand):
    # N(xN)
    parts = operand.strip()

    if ('(' in parts):
        offset_str, reg_str = parts.split('(')
        offset = int(offset_str)
        reg = int(reg_str.strip('x)'))

        return offset, reg
    
    elif parts.startswith('x'):
        return 0, int(parts[1:])
    
    else:
        return int(operand[1:]), None


# God has forsaken me
def simulator(instructions, dataMemory):
    registers = [0] * 32
    fetchPC = 256
    cycle = 1

    # Queues
    preIssue = []
    preALU1 = []
    preMEM = []
    postMEM = []
    preALU2 = []
    postALU2 = []
    preALU3 = []
    postALU3 = []
    
    writebackStalls = []


    breakFetch = False
    waitingInstr = None
    waitingPC = None
    executedInstr = None
    branchWasExecuted = False
    breakExists = False

    scoreboard = {reg: {"read": False, "write": False} for reg in range(32)}

    simulateFile = open("simulation.txt", "w")

    while True and breakExists == False:
        # print(f"Cycle {cycle}, PC={fetchPC}, instr={instructions.get(fetchPC)}") # debug

        # the terminator :D
        pipeline_busy = (preIssue or preALU1 or preMEM or postMEM or 
                        preALU2 or postALU2 or preALU3 or postALU3 or 
                        waitingInstr)

        if breakFetch and not pipeline_busy:
            break

        # Make the header part of the thing
        simulateFile.write("-" * 20 + '\n')
        simulateFile.write(f"Cycle {cycle}:\n\n")

        branchTaken = False
        justExecutedBranch = False
        jalExists = False

        # The actual pipelining part here

        # Memory stage

        if preMEM:
            # MEM Queue:

            memInstr = preMEM.pop(0)
            parts = memInstr.replace(',', '').split()
            mnemonic = parts[0]

            # loads the thing
            if mnemonic == "lw":
                rd = int(parts[1][1:])
                offset, rs1 = parseOperand(parts[2])
                addr = registers[rs1] + offset
                val = dataMemory.get(addr, 0)
                postMEM.append((memInstr, rd, val))

            # stores the thing
            elif mnemonic == "sw":
                rs2 = int(parts[1][1:])
                offset, rs1 = parseOperand(parts[2])
                addr = registers[rs1] + offset
                dataMemory[addr] = registers[rs2]

        # Execute ALU stages

        if preALU1:
            # Pre ALU1 Queue
            # Should be lw sw
            alu1Instr = preALU1.pop(0)
            preMEM.append(alu1Instr)

        if preALU2:
            # ALU2 Queue logic
            alu2Instr = preALU2.pop(0)
            parts = alu2Instr.replace(',', '').split()
            mnemonic = parts[0]

            rd = int(parts[1][1:])
            rs1 = int(parts[2][1:])
            val = None

            # should be add sub addi
            if mnemonic == "add":
                rs2 = int(parts[3][1:])
                val = registers[rs1] + registers[rs2]

            elif mnemonic == "sub":
                rs2 = int(parts[3][1:])
                val = registers[rs1] - registers[rs2]

            elif mnemonic == "addi":
                imm = int(parts[3][1:])
                val = registers[rs1] + imm

            if val is not None:
                postALU2.append((alu2Instr, rd, val))

        if preALU3:
            # ALU3 Queue
            alu3Instr = preALU3.pop(0)
            parts = alu3Instr.replace(',', '').split()
            mnemonic = parts[0]

            rd = int(parts[1][1:])
            rs1 = int(parts[2][1:])
            val = None

            # should be and or andi ori slli srai
            if mnemonic == "and":
                rs2 = int(parts[3][1:])
                val = registers[rs1] & registers[rs2]

            elif mnemonic == "or":
                rs2 = int(parts[3][1:])
                val = registers[rs1] | registers[rs2]

            elif mnemonic == "andi":
                imm = int(parts[3][1:])
                val = registers[rs1] & imm

            elif mnemonic == "ori":
                imm = int(parts[3][1:])
                val = registers[rs1] | imm

            elif mnemonic == "slli":
                imm = int(parts[3][1:])
                val = registers[rs1] << imm

            elif mnemonic == "srai":
                imm = int(parts[3][1:])
                val = registers[rs1] >> imm

            if val is not None:
                postALU3.append((alu3Instr, rd, val))

        # Issue stage

        issuedCount = 0

        # Adds everything together for the mess later
        inFlight = []
        # strings stuff
        for q in [preALU1, preMEM, preALU2, preALU3]:
            inFlight.extend(q)

        # tuple stuff
        for q in [postMEM, postALU2, postALU3]:
            inFlight.extend(i[0] for i in q if isinstance(i, tuple))

        # Does all the delaying stuff
        i = 0

        while i < len(preIssue) and issuedCount < 3:

            instr = preIssue[i]

            # If there's a hazard, this should delay the thingy
            hazard = hazardCheck(instr, inFlight, writebackStalls)
            if hazard or not operandsReady(instr, scoreboard, writebackStalls):
                break

            parts = instr.replace(',', '').split()
            mnemonic = parts[0]
            
            # If there's dupe instr delay
            if mnemonic in ["lw", "sw"] and preALU1:
                break
            if mnemonic in ["add", "sub", "addi"] and (preALU2 or postALU2):
                break
            if mnemonic in ["and", "or", "andi", "ori", "slli", "srai"] and (preALU3 or postALU3):
                break

            # Adds the funct
            if mnemonic in ["lw", "sw"]:
                target = preALU1
                limit = 1
            
            elif mnemonic in ["add", "sub", "addi"]:
                target = preALU2
                limit = 1
            
            elif mnemonic in ["and", "or", "andi", "ori", "slli", "srai"]:
                target = preALU3
                limit = 1
            
            else:
                i += 1
                continue
            
            if len(target) >= limit:
                break

            target.append(instr)
            preIssue.pop(i)
            issuedCount += 1

            inputReg, destReg = getRegs(instr)
            for r in inputReg:
                scoreboard[r]["read"] = True
            for r in destReg:
                scoreboard[r]["write"] = True

        # Fetch

        if not waitingInstr and not branchWasExecuted and not breakFetch and not justExecutedBranch:
            fetchedThisCycle = 0
            
            while (fetchedThisCycle < 2) and (len(preIssue) < 4):
                if fetchPC not in instructions:
                    break

                fetchedInstr = instructions[fetchPC]

                if (fetchedInstr == "break"):
                    breakFetch = True
                    fetchPC += 4
                    breakExists = True
                    break

                # Brach stuff
                if (isBranch(fetchedInstr)):
                    parts = fetchedInstr.split()
                    mnemonic = parts[0]

                    # I hate jal
                    if (mnemonic == "jal"):
                        jalExists = True
                        jalFunction = fetchedInstr
                        executedInstr = fetchedInstr
                        branchTarget = computeBranchTarget(fetchPC, fetchedInstr, registers)
                        fetchPC = branchTarget
                        justExecutedBranch = True
                        waitingInstr = None
                        waitingPC = None
                        break
                    
                    # the rest of the branch stuff
                    waitingInstr = fetchedInstr
                    waitingPC = fetchPC
                    fetchPC += 4
                    break

                preIssue.append(fetchedInstr)
                fetchPC += 4
                fetchedThisCycle += 1

        # Writeback - found out i needed to have writeback in the back the hard way... :(

        writebackStalls = [(instr, reg, val, cycles - 1) 
                          for instr, reg, val, cycles in writebackStalls]

        readyToWriteback = [item for item in writebackStalls if item[3] == 0]
        writebackStalls = [item for item in writebackStalls if item[3] > 0]

        # Does the writeback stuff here
        for instr_w, destReg, val, _ in readyToWriteback:
            registers[destReg] = val
            scoreboard[destReg]["write"] = False
            inflightInput, inflightDest = getRegs(instr_w)

            for r in inflightInput:
                scoreboard[r]["read"] = False

        writebacks = postMEM + postALU2 + postALU3

        # if there's a stall
        for instr_w, destReg, val in writebacks:
            writebackStalls.append((instr_w, destReg, val, 1))

        executedInstr = None
        
        # Try to execute waiting branch

        if waitingInstr:
            # IF Unit:
            pipeline_active = (preIssue or preALU1 or preMEM or postMEM or preALU2 or postALU2 or preALU3 or postALU3)

            # Branch executes if there's nothing in pipe and it can be done
            if not pipeline_active and operandsReady(waitingInstr, scoreboard, writebackStalls):
                if not branchWasExecuted:
                    branchWasExecuted = True
                    
                # Branch can execute this cycle
                else:
                    executedInstr = waitingInstr
                    branchTarget = computeBranchTarget(waitingPC, waitingInstr, registers)

                    parts = waitingInstr.replace(",", "").split()
                    mnemonic = parts[0]
                    if len(parts) > 1:
                        rs1 = int(parts[1][1:])
                    else:
                        rs1 = None
                    if len(parts) > 2:
                        rs2 = int(parts[2][1:])
                    else:
                        rs2 = None
                    branchTaken = False

                    # Branch lojix
                    if mnemonic == "jal":
                        branchTaken = True
                    elif mnemonic == "beq" and registers[rs1] == registers[rs2]:
                        branchTaken = True
                    elif mnemonic == "bne" and registers[rs1] != registers[rs2]:
                        branchTaken = True
                    elif mnemonic == "blt" and registers[rs1] < registers[rs2]:
                        branchTaken = True

                    if branchTaken:
                        fetchPC = branchTarget
                        preIssue.clear()
                    else:
                        fetchPC = waitingPC + 4
                    
                    waitingInstr = None
                    waitingPC = None
                    branchWasExecuted = False
                    justExecutedBranch = True

        # Write everything

        simulateFile.write("IF Unit:\n")
        if waitingInstr:
            simulateFile.write(f"\tWaiting: [{waitingInstr}]\n")
        else:
            simulateFile.write("\tWaiting:\n")
        if executedInstr:
            simulateFile.write(f"\tExecuted: [{executedInstr}] \n")
        elif breakExists:
            simulateFile.write(f"\tExecuted: [break]\n")
        elif jalExists:
            simulateFile.write(f"\tExecuted: [{jalFunction}]\n")
        else:
            simulateFile.write("\tExecuted:\n")
        simulateFile.write("Pre-Issue Queue:\n")
        for i in range(4):
            if i < len(preIssue):
                simulateFile.write(f"\tEntry {i}: [{preIssue[i]}]\n")
            else:
                simulateFile.write(f"\tEntry {i}:\n")
        simulateFile.write("Pre-ALU1 Queue:\n")
        for i in range(2):
            if i < len(preALU1):
                simulateFile.write(f"\tEntry {i}: [{preALU1[i]}]\n")
            else:
                simulateFile.write(f"\tEntry {i}:\n")
        simulateFile.write("Pre-MEM Queue:")
        if preMEM:
            simulateFile.write(f" [{preMEM[0]}]\n")
        else:
            simulateFile.write("\n")
        simulateFile.write("Post-MEM Queue:")
        if postMEM:
            simulateFile.write(f" [{postMEM[0][0]}]\n")
        else:
            simulateFile.write("\n")
        simulateFile.write("Pre-ALU2 Queue: ")
        if preALU2:
            simulateFile.write(f"[{preALU2[0]}]\n")
        else:
            simulateFile.write("\n")
        simulateFile.write("Post-ALU2 Queue: ")
        if postALU2:
            simulateFile.write(f"[{postALU2[0][0]}]\n")
        else:
            simulateFile.write("\n")
        simulateFile.write("Pre-ALU3 Queue:")
        if preALU3:
            simulateFile.write(f" [{preALU3[0]}]\n")
        else:
            simulateFile.write("\n")
        simulateFile.write("Post-ALU3 Queue:")
        if postALU3:
            simulateFile.write(f" [{postALU3[0][0]}]\n")
        else:
            simulateFile.write("\n")
        simulateFile.write("\nRegisters\n")
        for i in range(0, 32, 8):
            vals = [str(registers[j]) for j in range(i, i + 8)]
            simulateFile.write(f"x{i:02d}:\t" + "\t".join(vals) + "\n")
        simulateFile.write("Data\n")
        sortAddress = sorted(dataMemory.keys())
        for i in range(0, len(sortAddress), 8):
            addressGroup = sortAddress[i:i+8]
            vals = [str(dataMemory[a]) for a in addressGroup]
            simulateFile.write(f"{addressGroup[0]}:\t" + "\t".join(vals) + "\n")
        
    
        # Apply branch if executed

        if executedInstr and isBranch(executedInstr):
            if branchTaken:
                fetchPC = branchTarget
                preIssue = []
            branchWasExecuted = False

        postMEM = []
        postALU2 = []
        postALU3 = []

        cycle += 1

        # if cycle > 200:
        #     print("inf loop")
        #     break

    simulateFile.close()


def main():
    inputFile = sys.argv[1]
    instructions, dataMemory = disassembler(inputFile)
    simulator(instructions, dataMemory)


if (__name__ == "__main__"):
    main()