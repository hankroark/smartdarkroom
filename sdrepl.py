#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# stuff to bootstrap the REPL

import smartdarkroom.main
import smartdarkroom.prints as p

# Say hello to the world
smartdarkroom.main.main()

# Grab the enlarger for the user
enlarger = smartdarkroom.main.get_enlarger()