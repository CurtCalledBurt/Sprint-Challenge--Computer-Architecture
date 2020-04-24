"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.prog_end = 0
        self.flags = [0] * 8
        # Flag register: 00000LGE

    def load(self):
        """Load a program into memory."""

        address = 0

        # get the prgram file name from sys.argv
        program_filename = sys.argv[1]

        # "./" means "in the current directory", which is the folder that our current file is in, which is Computer-Architecture/ls8
 
        f = open(f"./{program_filename}", 'r')

        for line in f:
            # process text
            # split strings on '#' to remove comments from numbers
            line = line.split('#') # line is now an array
            # we know the program is the first non-whitespace in each line wherever it appears, so ...
            # extract the first thing in the line array, and remove whitespace from it
            line = line[0].strip()
            # if it is empty, do nothing, move on to next line
            if line == '':
                continue
            
            # convert the instruction string into a binary integer
            instruction = int(line, 2)
            
            # store the instruction in RAM if there is space
            if address == self.reg[7]:
                print("Error: Not enough memory to run the given program")
            else:
                self.ram[address] = instruction
                address += 1

        self.prog_end = address

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def ram_read(self, pc):
        return self.ram[pc]

    def ram_write(self, pc, value):
        self.ram[pc] = value

    def run(self):
        """Run the CPU."""

        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001
        ADD = 0b10100000
        MUL = 0b10100010
        AND = 0b10101000
        OR = 0b10101010
        XOR = 0b10101011
        NOT = 0b01101001
        SHL = 0b10101100
        SHR = 0b10101101
        PUSH = 0b01000101
        POP = 0b01000110
        RET = 0b00010001
        CALL = 0b01010000
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

        SP = self.reg[7]
        Less = self.flags[5]
        Greater = self.flags[6]
        Equal = self.flags[7]

        running = True
        while running:
            inst = self.ram[self.pc]

            inst_len = ((inst & 0b11000000) >> 6) + 1

            ALU = ((inst & 0b00100000) >> 5) 

            # load value into given register
            if inst == LDI:
                reg_num = self.ram[self.pc+1]
                value = self.ram[self.pc+2]
                self.reg[reg_num] = value

            # print value in given register
            elif inst == PRN:
                reg_num = self.ram[self.pc+1]
                value = self.reg[reg_num]
                print(value)

            # add 2 numbers together, placing result in the first given register
            elif inst == ADD:
                reg_A = self.ram[self.pc+1]
                reg_B = self.ram[self.pc+1]
                value = self.reg[reg_A] + self.reg[reg_B]
                self.reg[reg_A] = value
            
            # multiply 2 numbers together, placing the result in the first given register
            elif inst == MUL:
                reg_num1 = self.ram[self.pc+1]
                reg_num2 = self.ram[self.pc+2]
                value1 = self.reg[reg_num1]
                value2 = self.reg[reg_num2]
                value3 = value1 * value2
                self.reg[reg_num1] = value3

            # if both regA and regB are not 0, sets regA to 1
            elif inst == AND:
                reg_A = self.ram[self.pc+1]
                reg_B = self.ram[self.pc+2]
                value_A = self.reg[reg_A]
                value_B = self.reg[reg_B]
                result = value_A & value_B
                self.reg[reg_A] = result

            # if either regA or regB is not 0, sets regA to 1
            elif inst == OR:
                reg_A = self.ram[self.pc+1]
                reg_B = self.ram[self.pc+2]
                value_A = self.reg[reg_A]
                value_B = self.reg[reg_B]
                result = value_A | value_B
                self.reg[reg_A] = result

            # if either but not both regA and regB is not 0, sets regA to 1
            elif inst == XOR:
                reg_A = self.ram[self.pc+1]
                reg_B = self.ram[self.pc+2]
                value_A = self.reg[reg_A]
                value_B = self.reg[reg_B]
                result = value_A ^ value_B
                self.reg[reg_A] = result

            # sets the value in given register to its binary compliment 
            elif inst == NOT:
                reg_r = self.ram[self.pc+1]
                value = self.reg[reg_r]
                value = 0b11111111 - value
                self.reg[reg_r] = value
            
            # shifts the value in given register left bitwise x times
            elif inst == SHL:
                reg_A = self.ram[self.pc+1]
                reg_B = self.ram[self.pc+2]
                value = self.reg[reg_A]
                shift_num = self.reg[reg_B]
                value = value << shift_num
                self.reg[reg_A] = value & 0b11111111

            # shifts the value in the given register right bitwise x times
            elif inst == SHR:
                reg_A = self.ram[self.pc+1]
                reg_B = self.ram[self.pc+2]
                value = self.reg[reg_A]
                shift_num = self.reg[reg_B]
                value = value >> shift_num
                self.reg[reg_A] = value & 0b11111111

            # push value in given register onto the top of the stack
            elif inst == PUSH:
                # if push would overwrite the program at the bottom of memory, halt and throw an error
                if self.reg[7] - 1 == self.prog_end:
                    print("Error: Stack Overflow. Ending Program")
                    running = False
                
                # decrement sp counter, 
                # place value from given register where the sp is currently pointing
                else: 
                    SP -= 1
                    reg_num = self.ram[self.pc+1]
                    self.ram[SP] = self.reg[reg_num]
            
            # places value at the top of the stack into the given register
            elif inst == POP:
                # if stack is empty:
                # place value where sp is currently pointing into given register
                # do NOT increment sp counter
                if SP == 0xF4:
                    reg_num = self.ram[self.pc+1]
                    self.reg[reg_num] = self.ram[SP]

                # if stack has something in it:
                # place value where sp is currently pointing into the given register,
                # increment sp counter
                else:
                    reg_num = self.ram[self.pc+1]
                    self.reg[reg_num] = self.ram[SP]
                    SP += 1
            
            elif inst == CALL:
                # push address of instruction immediately after CALL onto stack
                SP -= 1
                func_address = self.pc+2
                self.ram[SP] = func_address

                # set PC to address in given register
                reg_r = self.ram[self.pc+1]
                self.pc = self.reg[reg_r]
                # we just set the pc to EXACTLY where we want it, but
                # at the end of the loop we add the instance length to pc. So
                # we subtract the instance length here to undo that.
                self.pc -= inst_len

            # return from subroutine
            elif inst == RET:
                where_we_left_off = self.ram[SP]
                self.pc = where_we_left_off
                # increment the stack pointer
                SP += 1
                # pc is set to EXACTLY where we want it, but at the end
                # of the loop we add the instance length to pc. So we 
                # subtract the inst_len from pc to counteract that.
                self.pc -= inst_len
            
            elif inst == CMP:
                # compare's the values in 2 given registers. 
                reg_A = self.ram[self.pc+1]
                reg_B = self.ram[self.pc+2]
                value_A = self.reg[reg_A]
                value_B = self.reg[reg_B]

                if value_A == value_B:
                    Less = 0
                    Greater = 0
                    Equal = 1
                
                elif value_A < value_B:
                    Less = 1
                    Greater = 0
                    Equal = 0

                elif value_A > value_B:
                    Less = 0
                    Greater = 1
                    Equal = 0
            
            # jump to the ram address in the given register
            elif inst == JMP:
                reg_r = self.ram[self.pc+1]
                address = self.reg[reg_r]
                self.pc = address
                # we jump to exactly where we want to go, so 
                # don't increment the pc automatically
                self.pc -= inst_len

            # if Equal flag is true, jump to the ram address in the given register
            elif inst == JEQ:
                if Equal:
                    reg_r = self.ram[self.pc+1]
                    address = self.reg[reg_r]
                    self.pc = address
                    # we jump on this branch of the 'if' statment, 
                    # don't increment pc
                    self.pc -= inst_len
                else:
                    # do nothing, increment pc later in loop
                    pass

            # if Equal flag is false, jump to the ram address in the given register
            elif inst == JNE:
                if not Equal:
                    reg_r = self.ram[self.pc+1]
                    address = self.reg[reg_r]
                    self.pc = address
                    # we jump on this branch of the 'if' statment, don't
                    # increment pc
                    self.pc -= inst_len
                else:
                    # do nothing, increment pc later in loop
                    pass

            # end program
            elif inst == HLT:
                running = False

            else:
                print(f"Error: Command '{bin(inst)}' not found, ending program")
                running = False
            
            self.pc += inst_len
