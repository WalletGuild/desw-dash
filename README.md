# Shared Wallet Dash RPC Plugin

Dash RPC plugin for the Deginner Shared Wallet project. Allows sending, receiving, and other generic wallet functionality using Dashd over RPC.

# Configuration

This plugin expects a .ini configuration file. Like other desw plugins, this file can be specified by setting the `DESW_CONFIG_FILE` environmental variable, like so.

`export DESW_CONFIG_FILE="path/to/cfg.ini"`

# Testing

This project requires 2 dash testnet nodes. The first should be configured for normal `desw_dash` use, and the second in the `DASH` variable of the `test` section in the config file. Both should have a nominal (>0.5 coin) balance.

```
[dash]
RPCURL: http://dashrpc:pass@127.0.0.1:8332
CONFS: 3

[test]
DASH: http://dashrpc:testpass@remote.server.com:18332
```