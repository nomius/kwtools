#!/usr/bin/env bash

fscrypt status $HOME 2>/dev/null | grep "Unlocked: No" && fscrypt unlock $HOME
