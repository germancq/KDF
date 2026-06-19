import random
import time

import cocotb
import keyDerivationFunction
import numpy as np
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.result import ReturnValue, TestFailure
from cocotb.triggers import FallingEdge, RisingEdge, Timer

CLK_PERIOD = 20  # 50 MHz


# the keyword await
#   Testbenches built using Cocotb use coroutines.
#   While the coroutine is executing the simulation is paused.
#   The coroutine uses the await keyword
#   to pass control of execution back to
#   the simulator and simulation time can advance again.
#
#   await return when the 'Trigger' is resolve
#
#   Coroutines may also await a list of triggers
#   to indicate that execution should resume if any of them fires


def setup_function(dut, salt, count, user_password):
    cocotb.fork(Clock(dut.clk, CLK_PERIOD).start())
    dut.rst.value = 0
    dut.salt.value = salt
    dut.count.value = count
    dut.user_password.value = user_password


async def rst_function_test(dut, first_value):
    dut.rst.value = 1

    await n_cycles_clock(dut, 10)

    if dut.key_derivated.value != 0:
        raise TestFailure(
            """Error rst hash_output,wrong hash value = {0}, expected value is {1}""".format(
                hex(int(dut.key_derivated.value)), 0
            )
        )

    if dut.end_signal.value != 0:
        raise TestFailure(
            """Error rst end_signal,wrong end_signal value = {0}, expected value is {1}""".format(
                hex(int(dut.end_signal.value)), 0
            )
        )

    if dut.counter_output.value != 0:
        raise TestFailure(
            """Error rst counter_output,wrong counter_output value = {0}, expected value is {1}""".format(
                hex(int(dut.counter_output.value)), 0
            )
        )

    if dut.hash_input.value != first_value:
        raise TestFailure(
            """Error rst hash_input,wrong hash_input value = {0}, expected value is {1}""".format(
                hex(int(dut.hash_input.value)), hex(first_value)
            )
        )

    dut.rst.value = 0


async def kdf_test(dut, expected_value):

    i = 0
    while dut.end_signal.value == 0:
        # print(int(dut.current_state.value))

        if dut.hash_end_signal.value:

            print("++++++++++++++++++++++++")
            # print(i)
            print(int(dut.counter_output))
            print(hex(int(dut.hash_input.value)))
            print(hex(int(dut.hash_output.value)))
            print(hex(int(dut.register_output.value)))

            print("++++++++++++++++++++++++++")

        # i = i+1

        await n_cycles_clock(dut, 1)

    print(hex(expected_value))
    if dut.key_derivated.value != expected_value:
        raise TestFailure(
            """Error kdf,wrong value = {0}, expected value is {1}""".format(
                hex(int(dut.key_derivated.value)), hex(expected_value)
            )
        )


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


async def run_test(dut, index=0):

    salt = random.getrandbits(dut.SALT_WIDTH.value)
    count = (random.getrandbits(dut.COUNT_WIDTH.value) & 0x000F) + random.getrandbits(4)
    user_password = random.getrandbits(dut.PSW_WIDTH.value)

    kdf_impl = keyDerivationFunction.KDF(
        count,
        salt,
        user_password,
        dut.COUNT_WIDTH.value,
        dut.SALT_WIDTH.value,
        dut.PSW_WIDTH.value,
    )
    expected_value = kdf_impl.generate_derivate_key()
    print(dut.COUNT_WIDTH.value)

    first_value = (
        (user_password << (dut.COUNT_WIDTH.value + dut.SALT_WIDTH.value))
        + (salt << dut.COUNT_WIDTH.value)
        + count
    )
    print(hex(first_value))

    setup_function(dut, salt, count, user_password)

    await rst_function_test(dut, first_value)
    await kdf_test(dut, expected_value)


n = 5
factory = TestFactory(run_test)

# array de 10 int aleatorios entre 0 y 31
factory.add_option("index", range(0, n))
factory.generate_tests()
