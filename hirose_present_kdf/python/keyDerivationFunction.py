# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    keyDerivationFunction.py                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: germancq <germancq@dte.us.es>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2019/10/17 15:49:52 by germancq          #+#    #+#              #
#    Updated: 2019/10/18 15:58:58 by germancq         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


import importlib
import sys

import hirose_present

sys.path.append(
    "/home/germancq/gitProjects/IPCores/hash_functions/hirose_present/python_code"
)


class KDF:
    def __init__(
        self, count, salt, user_password, count_len=32, salt_len=64, psw_len=32
    ):

        self.count = count  # valores de 32 bits
        self.salt = salt  # valores de 64 bits
        self.user_password = user_password  # valores de 32 bits
        self.count_len = count_len
        self.salt_len = salt_len
        self.psw_len = psw_len
        self.hash_function = hirose_present.HirosePresent(
            0x1234567812345678, self.count_len + self.salt_len + self.psw_len
        )

    def generate_derivate_key(self):

        x_i = (
            (self.user_password << (self.count_len + self.salt_len))
            + (self.salt << self.count_len)
            + self.count
        )
        print(hex(x_i))
        for i in range(0, self.count):
            x_i = self.hash_function.generate_hash(x_i)
            print(hex(x_i))

        return x_i


if __name__ == "__main__":
    kdf_impl = KDF(2000, 0x123456789ABCDEF0, 0xAAAA)
    kdf_value = kdf_impl.generate_derivate_key()
    # print(hex(kdf_value))

