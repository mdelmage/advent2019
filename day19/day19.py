#!/usr/bin/python
# coding: utf-8

import copy
from collections import namedtuple

GRID_SIZE = 100

OFFSET_X = 1523
OFFSET_Y = 1022

STATUS_STATIONARY = 0
STATUS_PULLED     = 1

tiles = { STATUS_STATIONARY: '.',
          STATUS_PULLED    : '#'}

input_index = 0
pulled = 0
output = ""

class IntcodeNode:
    Pointer = namedtuple('Pointer', 'address value')

    OPCODE_ADD      = 1
    OPCODE_MULTIPLY = 2
    OPCODE_INPUT    = 3
    OPCODE_OUTPUT   = 4
    OPCODE_JIT      = 5
    OPCODE_JIF      = 6
    OPCODE_LT       = 7
    OPCODE_EQ       = 8
    OPCODE_RELATIVE = 9
    OPCODE_HALT     = 99

    ADDRESS_POSITION  = 0
    ADDRESS_IMMEDIATE = 1
    ADDRESS_RELATIVE  = 2

    opcode_lengths = { OPCODE_ADD      : 4,
                       OPCODE_MULTIPLY : 4,
                       OPCODE_INPUT    : 2,
                       OPCODE_OUTPUT   : 2,
                       OPCODE_JIT      : 0,
                       OPCODE_JIF      : 0,
                       OPCODE_LT       : 4,
                       OPCODE_EQ       : 4,
                       OPCODE_RELATIVE : 2,
                       OPCODE_HALT     : 0 }

    def __init__(self, program):
        self.program = copy.deepcopy(program)
        self.relative_base = 0
        self.pc = 0
        self.output = []

    def read(self, address):
        if address in self.program:
            return self.program[address]
        else:
            return 0

    def write(self, address, value):
        self.program[address] = value

    def parameter(self, address, mode):
        param = 0

        # Use exceptions to simplify command processing.
        # Shorter opcodes may dereference invalid memory
        # when calculating extra params.
        try:
            if self.ADDRESS_POSITION == mode:
                # Return (parameter, *parameter)
                param = self.Pointer(self.read(self.pc + address), self.read(self.read(self.pc + address)))
            elif self.ADDRESS_IMMEDIATE == mode:
                # Return (&parameter, parameter)
                param = self.Pointer(self.pc + address, self.read(self.pc + address))
            elif self.ADDRESS_RELATIVE == mode:
                # Return (parameter + relative base, *(parameter + relative base)
                param = self.Pointer(self.read(self.pc + address) + self.relative_base, self.read(self.read(self.pc + address) + self.relative_base))
            else:
                print "Unknown parameter mode {0}!".format(mode)
        except:
            pass

        return param

    def execute(self):
        while self.read(self.pc) != self.OPCODE_HALT:
            instruction = self.read(self.pc)
            opcode = instruction % 100
            param1_mode = (instruction / 100) % 10
            param2_mode = (instruction / 1000) % 10
            param3_mode = (instruction / 10000) % 10

            param1 = self.parameter(1, param1_mode)
            param2 = self.parameter(2, param2_mode)
            param3 = self.parameter(3, param3_mode)

            if self.OPCODE_ADD == opcode:
                self.write(param3.address, param1.value + param2.value)
            elif self.OPCODE_MULTIPLY == opcode:
                self.write(param3.address, param1.value * param2.value)
            elif self.OPCODE_INPUT == opcode:
                global input_index
                # Even indices are the X coordinate.
                # Odd indices are the Y coordinate.
                if 0 == input_index % 2:
                    coord = OFFSET_X + ((input_index / 2) % GRID_SIZE)
                    #print "inputting x coord {0}".format(coord)
                else:
                    coord = OFFSET_Y + ((input_index - 1) / 2 / GRID_SIZE)
                    #print "inputting y coord {0}".format(coord)
                self.write(param1.address, coord)
                input_index += 1
            elif self.OPCODE_OUTPUT == opcode:
                global output
                global pulled
                if STATUS_PULLED == param1.value:
                    pulled += 1

                output += tiles[param1.value]
                if 0 == input_index % (2 * GRID_SIZE):
                    print output
                    output = ""
            elif self.OPCODE_JIT == opcode:
                self.pc = param2.value if param1.value != 0 else self.pc + 3
            elif self.OPCODE_JIF == opcode:
                self.pc = param2.value if param1.value == 0 else self.pc + 3
            elif self.OPCODE_LT == opcode:
                self.write(param3.address, 1 if param1.value < param2.value else 0)
            elif self.OPCODE_EQ == opcode:
                self.write(param3.address, 1 if param1.value == param2.value else 0)
            elif self.OPCODE_RELATIVE == opcode:
                self.relative_base += param1.value
            else:
                print "Unknown opcode {0} @ PC {1} RB {2}!".format(opcode, self.pc, self.relative_base)
                break

            self.pc += self.opcode_lengths[opcode]

        #print "halt @ PC {0} ({1})".format(self.pc, self.read(self.pc))

# Open input file
with open("day19.txt", "r") as f:
    for line in f:
        i = 0
        program = {}
        for item in line.strip().split(","):
            program[i] = int(item)
            i += 1

        for i in range(GRID_SIZE * GRID_SIZE):
            node = IntcodeNode(program)
            node.execute()

        print "{0} points affected by the tractor beam in the nearest {1}x{1} area.".format(pulled, GRID_SIZE)